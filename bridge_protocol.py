"""Strict, side-effect-free protocol validation for the isolated Windows pilot.

This module DOES NOT execute commands, access GitHub, or alter local files.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import re
from typing import Any

SCHEMA_VERSION = 0
OPERATION = "write_fixed_test_file"
WORKSPACE_PROFILE = "isolated-pilot"
ALLOWED_FIELDS = frozenset({
    "schema_version", "job_id", "operation",
    "workspace_profile", "parameters", "expires_at",
})
JOB_ID_PATTERN = re.compile(r"[a-z0-9](?:[a-z0-9-]{1,62}[a-z0-9])?\Z", re.ASCII)
MAX_TTL = timedelta(minutes=15)
MAX_JOB_BYTES = 4096
FIXED_OUTPUT_NAME = "chat_local_bridge_pilot.txt"
FIXED_OUTPUT_BYTES = b"GPT Chat Local Bridge pilot v0\n"


class JobValidationError(ValueError):
    """Rejected job: schema, authorization envelope, or expiry mismatch."""


def parse_job(raw: bytes, *, now: datetime | None = None) -> dict[str, Any]:
    """Validate a v0 job without interpreting any field as a shell command.

    `now` is injectable for unit tests; production callers omit it.
    """
    if not isinstance(raw, bytes) or len(raw) > MAX_JOB_BYTES:
        raise JobValidationError("invalid_size")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise JobValidationError("invalid_json") from exc

    if not isinstance(data, dict) or set(data) != ALLOWED_FIELDS:
        raise JobValidationError("unexpected_fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise JobValidationError("invalid_schema_version")
    job_id = data["job_id"]
    if not isinstance(job_id, str) or not JOB_ID_PATTERN.fullmatch(job_id):
        raise JobValidationError("invalid_job_id")
    if data["operation"] != OPERATION:
        raise JobValidationError("operation_not_allowed")
    if data["workspace_profile"] != WORKSPACE_PROFILE:
        raise JobValidationError("workspace_not_allowed")
    if type(data["parameters"]) is not dict or data["parameters"]:
        raise JobValidationError("parameters_not_allowed")
    expires_at = data["expires_at"]
    if not isinstance(expires_at, str):
        raise JobValidationError("invalid_expiry")
    try:
        expiry = datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise JobValidationError("invalid_expiry") from exc

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now_must_be_timezone_aware")
    now = now.astimezone(timezone.utc)
    if expiry <= now:
        raise JobValidationError("job_expired")
    if expiry - now > MAX_TTL:
        raise JobValidationError("expiry_too_distant")
    return data
