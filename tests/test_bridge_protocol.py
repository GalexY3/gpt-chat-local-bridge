"""Protocol tests are offline and have no filesystem/network side effects."""
from datetime import datetime, timedelta, timezone
import json
import unittest

from bridge_protocol import JobValidationError, parse_job

NOW = datetime(2026, 10, 30, 20, 0, tzinfo=timezone.utc)


def valid_job():
    return {
        "schema_version": 0,
        "job_id": "pilot-0001",
        "operation": "write_fixed_test_file",
        "workspace_profile": "isolated-pilot",
        "parameters": {},
        "expires_at": (NOW + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def encode(data):
    return json.dumps(data).encode("utf-8")


class ProtocolTests(unittest.TestCase):
    def test_accepts_minimal_valid_job(self):
        self.assertEqual(parse_job(encode(valid_job()), now=NOW)["job_id"], "pilot-0001")

    def test_rejects_arbitrary_command(self):
        job = valid_job()
        job["operation"] = "powershell"
        with self.assertRaisesRegex(JobValidationError, "operation_not_allowed"):
            parse_job(encode(job), now=NOW)

    def test_rejects_extra_command_field(self):
        job = valid_job()
        job["command"] = "whoami"
        with self.assertRaisesRegex(JobValidationError, "unexpected_fields"):
            parse_job(encode(job), now=NOW)

    def test_rejects_job_id_path_traversal(self):
        job = valid_job()
        job["job_id"] = "../private"
        with self.assertRaisesRegex(JobValidationError, "invalid_job_id"):
            parse_job(encode(job), now=NOW)

    def test_rejects_boolean_schema_version(self):
        job = valid_job()
        job["schema_version"] = False
        with self.assertRaisesRegex(JobValidationError, "invalid_schema_version"):
            parse_job(encode(job), now=NOW)

    def test_rejects_parameters(self):
        job = valid_job()
        job["parameters"] = {"path": "../secret"}
        with self.assertRaisesRegex(JobValidationError, "parameters_not_allowed"):
            parse_job(encode(job), now=NOW)

    def test_rejects_expired_job(self):
        job = valid_job()
        job["expires_at"] = (NOW - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self.assertRaisesRegex(JobValidationError, "job_expired"):
            parse_job(encode(job), now=NOW)

    def test_rejects_long_lived_job(self):
        job = valid_job()
        job["expires_at"] = (NOW + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self.assertRaisesRegex(JobValidationError, "expiry_too_distant"):
            parse_job(encode(job), now=NOW)

    def test_rejects_invalid_utf8(self):
        with self.assertRaisesRegex(JobValidationError, "invalid_json"):
            parse_job(bytes([255]), now=NOW)

    def test_rejects_oversized_payload(self):
        with self.assertRaisesRegex(JobValidationError, "invalid_size"):
            parse_job(b"x" * 4097, now=NOW)

    def test_rejects_duplicate_json_keys(self):
        raw = encode(valid_job()).replace(b'"job_id":', b'"job_id":"other", "job_id":')
        with self.assertRaisesRegex(JobValidationError, "invalid_json"):
            parse_job(raw, now=NOW)

    def test_rejects_duplicate_nested_parameter_keys(self):
        raw = encode(valid_job()).replace(b'"parameters": {}', b'"parameters": {"a": 1, "a": 2}')
        with self.assertRaisesRegex(JobValidationError, "invalid_json"):
            parse_job(raw, now=NOW)

    def test_rejects_nonfinite_json_number(self):
        raw = encode(valid_job()).replace(b'"schema_version": 0', b'"schema_version": NaN')
        with self.assertRaisesRegex(JobValidationError, "invalid_json"):
            parse_job(raw, now=NOW)

    def test_rejects_non_utc_expiry(self):
        job = valid_job()
        job["expires_at"] = "2026-10-30T20:05:00+00:00"
        with self.assertRaisesRegex(JobValidationError, "invalid_expiry"):
            parse_job(encode(job), now=NOW)


if __name__ == "__main__":
    unittest.main()
