"""Offline tests for the one-shot worker. No GitHub calls; no personal files."""
import hashlib
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from bridge_protocol import FIXED_OUTPUT_BYTES, FIXED_OUTPUT_NAME
from bridge_worker import WorkerError, create_workspace, run_job

NOW = datetime(2026, 10, 30, 20, 0, tzinfo=timezone.utc)


def valid_job(job_id="pilot-0001"):
    return json.dumps({
        "schema_version": 0,
        "job_id": job_id,
        "operation": "write_fixed_test_file",
        "workspace_profile": "isolated-pilot",
        "parameters": {},
        "expires_at": (NOW + timedelta(minutes=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }).encode("utf-8")


class FakeTransport:
    def __init__(self, raw=None):
        self.raw = raw if raw is not None else valid_job()
        self.receipts = []
        self.verified = 0
        self.fail_publish = False

    def verify_repository(self):
        self.verified += 1

    def read_job(self, job_id):
        return self.raw

    def publish_receipt(self, job_id, receipt):
        if self.fail_publish:
            raise RuntimeError("simulated_network_failure")
        self.receipts.append((job_id, receipt))


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "isolated-pilot"
        create_workspace(self.root)

    def test_success_receipt_and_hash(self):
        transport = FakeTransport()
        receipt = run_job(self.root, "pilot-0001", transport, now=NOW)
        self.assertEqual(transport.verified, 1)
        self.assertEqual((self.root / FIXED_OUTPUT_NAME).read_bytes(), FIXED_OUTPUT_BYTES)
        self.assertEqual(receipt["output_sha256"], hashlib.sha256(FIXED_OUTPUT_BYTES).hexdigest())
        self.assertEqual(transport.receipts[0][1], receipt)

    def test_repeated_job_does_not_repeat_effect(self):
        transport = FakeTransport()
        run_job(self.root, "pilot-0001", transport, now=NOW)
        with self.assertRaisesRegex(WorkerError, "target_already_exists_or_link|job_already_reserved"):
            run_job(self.root, "pilot-0001", transport, now=NOW)
        self.assertEqual(len(transport.receipts), 1)

    def test_rejects_without_workspace_marker(self):
        (self.root / ".gpt-chat-bridge-pilot-v0").unlink()
        with self.assertRaisesRegex(WorkerError, "workspace_marker_invalid"):
            run_job(self.root, "pilot-0001", FakeTransport(), now=NOW)

    def test_job_id_mismatch(self):
        with self.assertRaisesRegex(WorkerError, "job_id_mismatch"):
            run_job(self.root, "pilot-0002", FakeTransport(), now=NOW)
        self.assertFalse((self.root / FIXED_OUTPUT_NAME).exists())

    def test_bad_job_without_side_effect(self):
        payload = json.loads(valid_job())
        payload["operation"] = "powershell"
        transport = FakeTransport(json.dumps(payload).encode("utf-8"))
        with self.assertRaisesRegex(WorkerError, "operation_not_allowed"):
            run_job(self.root, "pilot-0001", transport, now=NOW)
        self.assertFalse((self.root / FIXED_OUTPUT_NAME).exists())

    def test_cannot_overwrite_existing_output(self):
        (self.root / FIXED_OUTPUT_NAME).write_bytes(b"do not overwrite")
        with self.assertRaisesRegex(WorkerError, "target_already_exists_or_link"):
            run_job(self.root, "pilot-0001", FakeTransport(), now=NOW)
        self.assertEqual((self.root / FIXED_OUTPUT_NAME).read_bytes(), b"do not overwrite")

    def test_upload_failure_does_not_repeat_file_write(self):
        transport = FakeTransport()
        transport.fail_publish = True
        with self.assertRaisesRegex(WorkerError, "local_write_succeeded_receipt_upload_failed"):
            run_job(self.root, "pilot-0001", transport, now=NOW)
        self.assertTrue((self.root / FIXED_OUTPUT_NAME).exists())
        self.assertTrue((self.root / ".bridge-state" / "pilot-0001.json").exists())
        with self.assertRaises(WorkerError):
            run_job(self.root, "pilot-0001", transport, now=NOW)

    def test_does_not_accept_path_escape_id(self):
        with self.assertRaisesRegex(WorkerError, "invalid_job_id"):
            run_job(self.root, "../pilot-0001", FakeTransport(), now=NOW)

    def test_expired_job_no_effect(self):
        with self.assertRaisesRegex(WorkerError, "job_expired"):
            run_job(self.root, "pilot-0001", FakeTransport(), now=NOW + timedelta(days=1))
        self.assertFalse((self.root / FIXED_OUTPUT_NAME).exists())


if __name__ == "__main__":
    unittest.main()
