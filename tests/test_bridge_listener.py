"""Offline/adversarial tests for the v1 bounded foreground listener.

No live GitHub requests and no background processes.
"""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bridge_protocol import FIXED_OUTPUT_BYTES, FIXED_OUTPUT_NAME
from bridge_worker import WorkerError, create_workspace
from bridge_listener import (
    GitHubQueue, _acquire_listener_lock, execute_fixed_job, listen,
    MAX_QUEUE_ITEMS,
)

NOW = datetime(2026, 10, 30, 20, 0, tzinfo=timezone.utc)
SHA = "a" * 40


def payload(job_id="new-001", *, expiry_seconds=240):
    return json.dumps({
        "schema_version": 0, "job_id": job_id,
        "operation": "write_fixed_test_file", "workspace_profile": "isolated-pilot",
        "parameters": {},
        "expires_at": (NOW + timedelta(seconds=expiry_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }).encode("utf-8")


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def monotonic(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds

    def utc(self):
        return NOW + timedelta(seconds=self.t)


class FakeQueue:
    def __init__(self, *, pending=None, receipts=None, raw=None):
        self.pending = list(pending or [{}])
        self.last_pending = self.pending[-1]
        self.receipts = receipts or {}
        self.raw = raw if raw is not None else payload()
        self.published = []
        self.verify_count = 0
        self.read_count = 0
        self.publish_fails = False

    def verify_repository(self):
        self.verify_count += 1

    def list_pending(self):
        if self.pending:
            self.last_pending = self.pending.pop(0)
        return dict(self.last_pending)

    def list_receipts(self):
        return dict(self.receipts)

    def read_job(self, job_id, expected_sha):
        self.read_count += 1
        if expected_sha != SHA:
            raise WorkerError("job_changed_or_invalid")
        return self.raw

    def publish_receipt(self, job_id, receipt):
        if self.publish_fails:
            raise RuntimeError("simulated_publish_failure")
        self.published.append((job_id, receipt))


class ListenerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "pilot"
        create_workspace(self.root)
        self.clock = FakeClock()

    def listen(self, queue, **kwargs):
        return listen(
            self.root, queue, max_minutes=1, poll_seconds=10,
            clock=self.clock.monotonic, sleep=self.clock.sleep, utc=self.clock.utc,
            **kwargs,
        )

    def test_processes_one_new_task_and_isolates_output(self):
        queue = FakeQueue(pending=[{}, {}, {"new-001": SHA}])
        result = self.listen(queue)
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(len(queue.published), 1)
        target = self.root / "outputs" / "new-001" / FIXED_OUTPUT_NAME
        self.assertEqual(target.read_bytes(), FIXED_OUTPUT_BYTES)
        self.assertEqual(result["output_sha256"], hashlib.sha256(FIXED_OUTPUT_BYTES).hexdigest())
        self.assertFalse((self.root / ".bridge-state" / "listener.lock").exists())
        self.assertFalse((self.root / FIXED_OUTPUT_NAME).exists())

    def test_ignores_preexisting_job_even_if_valid(self):
        queue = FakeQueue(pending=[{"new-001": SHA}])
        result = self.listen(queue)
        self.assertEqual(result, {"status": "timed_out", "jobs_executed": 0})
        self.assertFalse((self.root / "outputs").exists())

    def test_ignores_receipted_new_job(self):
        queue = FakeQueue(
            pending=[{}, {"new-001": SHA}],
            receipts={"new-001": "b" * 40},
        )
        self.assertEqual(self.listen(queue)["status"], "timed_out")
        self.assertFalse((self.root / "outputs").exists())

    def test_ignores_previously_reserved_new_job(self):
        (self.root / ".bridge-state" / "new-001.json").write_text("{}")
        queue = FakeQueue(pending=[{}, {"new-001": SHA}])
        self.assertEqual(self.listen(queue)["status"], "timed_out")
        self.assertFalse((self.root / "outputs").exists())

    def test_expires_old_job_and_never_executes(self):
        queue = FakeQueue(
            pending=[{}, {"new-001": SHA}],
            raw=payload(expiry_seconds=-1),
        )
        self.assertEqual(self.listen(queue)["status"], "timed_out")
        self.assertFalse((self.root / "outputs" / "new-001").exists())

    def test_malformed_new_job_fails_closed(self):
        job = json.loads(payload())
        job["operation"] = "powershell"
        queue = FakeQueue(pending=[{}, {"new-001": SHA}], raw=json.dumps(job).encode())
        with self.assertRaisesRegex(WorkerError, "invalid_new_job:operation_not_allowed"):
            self.listen(queue)
        self.assertFalse((self.root / "outputs" / "new-001").exists())
        self.assertFalse((self.root / ".bridge-state" / "listener.lock").exists())

    def test_wrong_job_identity_fails_closed(self):
        queue = FakeQueue(pending=[{}, {"new-001": SHA}], raw=payload("different-id"))
        with self.assertRaisesRegex(WorkerError, "job_id_mismatch"):
            self.listen(queue)
        self.assertFalse((self.root / "outputs" / "new-001").exists())

    def test_one_job_only_even_when_two_new_arrive(self):
        other = "new-002"
        queue = FakeQueue(pending=[{}, {"new-001": SHA, other: SHA}])
        self.assertEqual(self.listen(queue)["status"], "succeeded")
        self.assertEqual(len(queue.published), 1)
        self.assertFalse((self.root / "outputs" / other).exists())

    def test_listener_lock_rejects_concurrent_instance(self):
        lock = _acquire_listener_lock(self.root)
        self.addCleanup(lambda: lock.unlink(missing_ok=True))
        with self.assertRaisesRegex(WorkerError, "listener_already_running_or_stale_lock"):
            self.listen(FakeQueue())
        self.assertTrue(lock.exists())

    def test_cannot_listen_without_initialized_workspace(self):
        (self.root / ".gpt-chat-bridge-pilot-v0").unlink()
        with self.assertRaisesRegex(WorkerError, "workspace_marker_invalid"):
            self.listen(FakeQueue())

    def test_rejects_out_of_range_listener_lifetime(self):
        with self.assertRaisesRegex(WorkerError, "max_minutes_out_of_range"):
            listen(self.root, FakeQueue(), max_minutes=0)
        with self.assertRaisesRegex(WorkerError, "max_minutes_out_of_range"):
            listen(self.root, FakeQueue(), max_minutes=11)
        with self.assertRaisesRegex(WorkerError, "poll_seconds_out_of_range"):
            listen(self.root, FakeQueue(), poll_seconds=1)

    def test_ctrl_c_releases_lock(self):
        queue = FakeQueue()
        def interrupted(_):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            listen(self.root, queue, max_minutes=1, poll_seconds=10,
                   clock=self.clock.monotonic, sleep=interrupted, utc=self.clock.utc)
        self.assertFalse((self.root / ".bridge-state" / "listener.lock").exists())

    def test_output_of_second_job_does_not_overwrite_first(self):
        q1 = FakeQueue()
        q2 = FakeQueue(raw=payload("new-002"))
        execute_fixed_job(self.root, "new-001", q1.raw, q1, now=NOW)
        execute_fixed_job(self.root, "new-002", q2.raw, q2, now=NOW)
        self.assertEqual((self.root / "outputs/new-001" / FIXED_OUTPUT_NAME).read_bytes(),
                         FIXED_OUTPUT_BYTES)
        self.assertEqual((self.root / "outputs/new-002" / FIXED_OUTPUT_NAME).read_bytes(),
                         FIXED_OUTPUT_BYTES)
        self.assertEqual(len(q1.published) + len(q2.published), 2)

    def test_replaying_same_id_never_overwrites(self):
        queue = FakeQueue()
        execute_fixed_job(self.root, "new-001", queue.raw, queue, now=NOW)
        with self.assertRaisesRegex(WorkerError, "job_already_reserved"):
            execute_fixed_job(self.root, "new-001", queue.raw, queue, now=NOW)
        self.assertEqual(len(queue.published), 1)

    def test_receipt_failure_leaves_durable_reservation(self):
        queue = FakeQueue()
        queue.publish_fails = True
        with self.assertRaisesRegex(WorkerError, "local_write_succeeded_receipt_upload_failed"):
            execute_fixed_job(self.root, "new-001", queue.raw, queue, now=NOW)
        self.assertTrue((self.root / ".bridge-state" / "new-001.json").exists())
        self.assertTrue((self.root / "outputs" / "new-001" / FIXED_OUTPUT_NAME).exists())
        with self.assertRaises(WorkerError):
            execute_fixed_job(self.root, "new-001", queue.raw, queue, now=NOW)

    def test_existing_output_dir_refused(self):
        (self.root / "outputs/new-001").mkdir(parents=True)
        with self.assertRaisesRegex(WorkerError, "output_already_exists"):
            execute_fixed_job(self.root, "new-001", payload(), FakeQueue(), now=NOW)
        self.assertFalse((self.root / ".bridge-state" / "new-001.json").exists())

    def test_malformed_job_does_not_reserve(self):
        with self.assertRaisesRegex(WorkerError, "invalid_job:invalid_json"):
            execute_fixed_job(self.root, "new-001", b"{", FakeQueue(), now=NOW)
        self.assertFalse((self.root / ".bridge-state" / "new-001.json").exists())

    def test_symlinked_outputs_dir_refused(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        try:
            (self.root / "outputs").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation not supported on this runner")
        with self.assertRaisesRegex(WorkerError, "output_root_invalid"):
            execute_fixed_job(self.root, "new-001", payload(), FakeQueue(), now=NOW)
        self.assertFalse((outside / "new-001").exists())

    def test_lease_lock_stale_crash_requires_manual_inspection(self):
        (self.root / ".bridge-state" / "listener.lock").write_text("stale")
        with self.assertRaisesRegex(WorkerError, "listener_already_running_or_stale_lock"):
            self.listen(FakeQueue())

    def test_permission_error_leaves_reservation_without_execution(self):
        queue = FakeQueue()
        # Prepare the root first: fail specifically when creating the per-job
        # output directory, i.e. after the durable reservation is written.
        (self.root / "outputs").mkdir()
        with patch("bridge_listener.Path.mkdir", side_effect=PermissionError("test")):
            with self.assertRaisesRegex(WorkerError, "local_output_failed_reserved"):
                execute_fixed_job(self.root, "new-001", queue.raw, queue, now=NOW)
        self.assertTrue((self.root / ".bridge-state" / "new-001.json").exists())
        self.assertEqual(queue.published, [])

    def test_network_errors_bounded_and_no_output(self):
        class FailingQueue(FakeQueue):
            def __init__(self):
                super().__init__()
                self.n = 0
            def list_pending(self):
                self.n += 1
                if self.n > 1:
                    raise WorkerError("github_request_failed")
                return {}
        with self.assertRaisesRegex(WorkerError, "github_repeated_failures"):
            self.listen(FailingQueue())
        self.assertFalse((self.root / "outputs").exists())
        self.assertFalse((self.root / ".bridge-state" / "listener.lock").exists())

    def test_expiry_rechecked_at_execution(self):
        queue = FakeQueue()
        with self.assertRaisesRegex(WorkerError, "invalid_job:job_expired"):
            execute_fixed_job(self.root, "new-001", queue.raw, queue,
                              now=NOW + timedelta(minutes=10))
        self.assertFalse((self.root / "outputs" / "new-001").exists())


class QueueValidationTests(unittest.TestCase):
    def queue(self, data):
        queue = object.__new__(GitHubQueue)
        queue._get = lambda endpoint: data
        return queue

    def entry(self, job_id="new-001", *, folder="pending", type_="file"):
        return {
            "name": f"{job_id}.json", "path": f"jobs/{folder}/{job_id}.json",
            "type": type_, "sha": SHA, "size": 120,
        }

    def test_accepts_strict_directory_entry(self):
        self.assertEqual(self.queue([self.entry()]).list_pending(), {"new-001": SHA})

    def test_rejects_path_traversal_filename(self):
        with self.assertRaisesRegex(WorkerError, "queue_entry_invalid"):
            self.queue([self.entry("../private")]).list_pending()

    def test_rejects_symlink_file_from_github(self):
        with self.assertRaisesRegex(WorkerError, "queue_entry_invalid"):
            self.queue([self.entry(type_="symlink")]).list_pending()

    def test_rejects_wrong_directory(self):
        bad = self.entry()
        bad["path"] = "elsewhere/new-001.json"
        with self.assertRaisesRegex(WorkerError, "queue_entry_invalid"):
            self.queue([bad]).list_pending()

    def test_rejects_oversized_listing(self):
        with self.assertRaisesRegex(WorkerError, "queue_listing_invalid_or_over_limit"):
            self.queue([self.entry()] * (MAX_QUEUE_ITEMS + 1)).list_pending()

    def test_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(WorkerError, "queue_duplicate_id"):
            self.queue([self.entry(), self.entry()]).list_pending()

    def test_refuses_wrong_repo_or_public_repo(self):
        for info in [
            {"full_name": "other/repo", "private": True, "default_branch": "main"},
            {"full_name": "GalexY3/gpt-chat-local-bridge-control", "private": False, "default_branch": "main"},
            {"full_name": "GalexY3/gpt-chat-local-bridge-control", "private": True, "default_branch": "untrusted"},
        ]:
            with self.subTest(info=info):
                with self.assertRaisesRegex(WorkerError, "unexpected_control_repository"):
                    self.queue(info).verify_repository()

    def test_read_job_requires_expected_commit_blob_sha(self):
        raw = payload()
        data = {
            "type": "file", "path": "jobs/pending/new-001.json",
            "sha": "b" * 40, "encoding": "base64",
            "content": base64.b64encode(raw).decode(),
        }
        with self.assertRaisesRegex(WorkerError, "job_changed_or_invalid"):
            self.queue(data).read_job("new-001", SHA)

    def test_read_job_rejects_malformed_base64(self):
        data = {
            "type": "file", "path": "jobs/pending/new-001.json",
            "sha": SHA, "encoding": "base64", "content": "not@base64",
        }
        with self.assertRaisesRegex(WorkerError, "job_content_invalid"):
            self.queue(data).read_job("new-001", SHA)


if __name__ == "__main__":
    unittest.main()
