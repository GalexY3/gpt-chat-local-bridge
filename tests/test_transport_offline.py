"""Offline GitHub CLI transport tests; never contact GitHub or launch gh.

Confirms fixed GET invocation, response validation, error handling, and that
receipt publishing uses a non-shell API call without exposing sensitive stderr.
"""
from __future__ import annotations

import base64
import json
import subprocess
import unittest
from unittest.mock import patch

from bridge_listener import GitHubQueue, MAX_API_BYTES
from bridge_worker import CONTROL_REPO, GitHubCLI, WorkerError


def simulated_process(*, stdout: str = "{}", returncode: int = 0,
                      stderr: str = "private diagnostic"):
    return subprocess.CompletedProcess(
        args=["gh", "api"], returncode=returncode, stdout=stdout, stderr=stderr,
    )


class QueueTransportOfflineTests(unittest.TestCase):
    def test_get_is_explicit_non_shell_request(self):
        endpoint = f"repos/{CONTROL_REPO}"
        with patch("bridge_listener.subprocess.run", return_value=simulated_process(
            stdout='{"private":true}'
        )) as run:
            response = GitHubQueue._get(endpoint)
        self.assertEqual(response, {"private": True})
        args, kwargs = run.call_args
        self.assertEqual(args[0][:4], ["gh", "api", "--method", "GET"])
        self.assertEqual(args[0][4], endpoint)
        self.assertIs(kwargs["shell"], False)
        self.assertFalse(kwargs["check"])
        self.assertLessEqual(kwargs["timeout"], 25)

    def test_get_rejects_command_failure_without_exposing_stderr(self):
        with patch("bridge_listener.subprocess.run", return_value=simulated_process(
            returncode=1, stderr="Bearer PRIVATE_SECRET"
        )):
            with self.assertRaises(WorkerError) as caught:
                GitHubQueue._get("repos/example")
        self.assertEqual(str(caught.exception), "github_request_failed")
        self.assertNotIn("PRIVATE_SECRET", str(caught.exception))

    def test_get_rejects_timeout(self):
        with patch("bridge_listener.subprocess.run",
                   side_effect=subprocess.TimeoutExpired(["gh", "api"], 25)):
            with self.assertRaisesRegex(WorkerError, "github_request_failed"):
                GitHubQueue._get("repos/example")

    def test_get_rejects_unparseable_json(self):
        with patch("bridge_listener.subprocess.run", return_value=simulated_process(
            stdout="not-json"
        )):
            with self.assertRaisesRegex(WorkerError, "github_invalid_response"):
                GitHubQueue._get("repos/example")

    def test_get_rejects_oversized_response(self):
        with patch("bridge_listener.subprocess.run", return_value=simulated_process(
            stdout=" " * (MAX_API_BYTES + 1)
        )):
            with self.assertRaisesRegex(WorkerError, "github_response_too_large"):
                GitHubQueue._get("repos/example")

    def test_get_accepts_array_for_queue_listing(self):
        with patch("bridge_listener.subprocess.run", return_value=simulated_process(
            stdout="[]"
        )):
            self.assertEqual(GitHubQueue._get("repos/example/contents/jobs/pending"), [])

    def test_repo_verification_fails_closed_when_auth_response_missing(self):
        with patch("bridge_listener.GitHubQueue._get", return_value={}):
            with self.assertRaisesRegex(WorkerError, "unexpected_control_repository"):
                GitHubQueue.verify_repository(object.__new__(GitHubQueue))

    def test_read_job_rejects_wrong_git_sha_or_path(self):
        encoded = base64.b64encode(b"{}").decode("ascii")
        invalid_response = {
            "type": "file", "encoding": "base64", "content": encoded,
            "path": "jobs/pending/other-id.json", "sha": "a" * 40,
        }
        with patch("bridge_listener.GitHubQueue._get", return_value=invalid_response):
            with self.assertRaisesRegex(WorkerError, "job_changed_or_invalid"):
                GitHubQueue.read_job(object.__new__(GitHubQueue), "new-001", "a" * 40)

    def test_receipt_publishing_has_no_shell_or_overwrite_sha(self):
        receipt = {
            "schema_version": 0, "job_id": "new-001", "status": "succeeded",
            "output_sha256": "b" * 64,
        }
        with patch("bridge_worker.shutil.which", return_value="gh"), patch(
            "bridge_worker.subprocess.run",
            return_value=simulated_process(stdout='{"commit":{"sha":"c"}}'),
        ) as run:
            GitHubQueue.publish_receipt(object.__new__(GitHubQueue), "new-001", receipt)
        args, kwargs = run.call_args
        self.assertEqual(args[0][:2], ["gh", "api"])
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(args[0][2], f"repos/{CONTROL_REPO}/contents/jobs/receipts/new-001.json")
        self.assertIn("--method", args[0])
        self.assertEqual(args[0][args[0].index("--method") + 1], "PUT")
        request = json.loads(kwargs["input"])
        self.assertNotIn("sha", request)
        self.assertEqual(request["branch"], "main")
        decoded = json.loads(base64.b64decode(request["content"]).decode("utf-8"))
        self.assertEqual(decoded, receipt)

    def test_receipt_upload_failure_does_not_log_credentials(self):
        with patch("bridge_worker.shutil.which", return_value="gh"), patch(
            "bridge_worker.subprocess.run",
            return_value=simulated_process(
                returncode=1, stderr="Secret PAT: should-never-appear"
            ),
        ):
            with self.assertRaises(WorkerError) as caught:
                GitHubQueue.publish_receipt(
                    object.__new__(GitHubQueue), "new-001", {"status": "succeeded"}
                )
        self.assertEqual(str(caught.exception), "github_request_failed")


if __name__ == "__main__":
    unittest.main()
