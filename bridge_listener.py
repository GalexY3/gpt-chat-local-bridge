"""Bounded foreground listener for the fixed-action GitHub/Windows pilot.

No arbitrary commands, no dynamic file paths, no desktop automation, no daemon.
Start only after reviewing code and passing local offline tests.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Callable

from bridge_protocol import (
    FIXED_OUTPUT_BYTES,
    FIXED_OUTPUT_NAME,
    JOB_ID_PATTERN,
    JobValidationError,
    MAX_JOB_BYTES,
    parse_job,
)
from bridge_worker import (
    CONTROL_REPO,
    GitHubCLI,
    WorkerError,
    _no_link,
    check_workspace,
    utc_iso,
    utc_now,
    workspace_path,
)

QUEUE_BRANCH = "main"
WORKER_VERSION = "listener-v1-dev"
MAX_QUEUE_ITEMS = 96
MAX_API_BYTES = 131072
MAX_MINUTES = 10
MIN_POLL_SECONDS = 10
MAX_POLL_SECONDS = 60
MAX_CONSECUTIVE_ERRORS = 3
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z", re.ASCII)
TRANSIENT_ERRORS = frozenset({"github_request_failed", "github_response_too_large",
                              "github_invalid_response"})


class GitHubQueue:
    """Read only fixed private repository paths; publish sanitized receipts."""

    def __init__(self) -> None:
        if shutil.which("gh") is None:
            raise WorkerError("gh_not_found")

    @staticmethod
    def _get(endpoint: str) -> Any:
        # Endpoint is assembled entirely from constants and validated job IDs.
        cmd = ["gh", "api", "--method", "GET", endpoint,
               "-H", "Accept: application/vnd.github+json"]
        try:
            response = subprocess.run(
                cmd, capture_output=True, text=True, timeout=25,
                encoding="utf-8", errors="replace", check=False, shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise WorkerError("github_request_failed") from exc
        if response.returncode != 0:
            raise WorkerError("github_request_failed")
        if len(response.stdout.encode("utf-8")) > MAX_API_BYTES:
            raise WorkerError("github_response_too_large")
        try:
            return json.loads(response.stdout)
        except ValueError as exc:
            raise WorkerError("github_invalid_response") from exc

    def verify_repository(self) -> None:
        info = self._get(f"repos/{CONTROL_REPO}")
        if (not isinstance(info, dict)
                or info.get("full_name") != CONTROL_REPO
                or info.get("private") is not True
                or info.get("default_branch") != QUEUE_BRANCH
                or info.get("archived") is True):
            raise WorkerError("unexpected_control_repository")

    def _list(self, folder: str) -> dict[str, str]:
        data = self._get(
            f"repos/{CONTROL_REPO}/contents/jobs/{folder}?ref={QUEUE_BRANCH}"
        )
        if not isinstance(data, list) or len(data) > MAX_QUEUE_ITEMS:
            raise WorkerError("queue_listing_invalid_or_over_limit")
        out: dict[str, str] = {}
        for item in data:
            if not isinstance(item, dict) or item.get("type") != "file":
                raise WorkerError("queue_entry_invalid")
            name = item.get("name")
            path = item.get("path")
            sha = item.get("sha")
            size = item.get("size")
            if (not isinstance(name, str) or not name.endswith(".json")
                    or not JOB_ID_PATTERN.fullmatch(name[:-5])
                    or path != f"jobs/{folder}/{name}"
                    or not isinstance(sha, str) or not SHA_PATTERN.fullmatch(sha)
                    or type(size) is not int or size < 0
                    or size > (MAX_JOB_BYTES if folder == "pending" else 4096)):
                raise WorkerError("queue_entry_invalid")
            if name[:-5] in out:
                raise WorkerError("queue_duplicate_id")
            out[name[:-5]] = sha
        return out

    def list_pending(self) -> dict[str, str]:
        return self._list("pending")

    def list_receipts(self) -> dict[str, str]:
        return self._list("receipts")

    def read_job(self, job_id: str, expected_sha: str) -> bytes:
        if not isinstance(job_id, str) or not JOB_ID_PATTERN.fullmatch(job_id):
            raise WorkerError("invalid_job_id")
        data = self._get(
            f"repos/{CONTROL_REPO}/contents/jobs/pending/{job_id}.json?ref={QUEUE_BRANCH}"
        )
        if (not isinstance(data, dict) or data.get("type") != "file"
                or data.get("path") != f"jobs/pending/{job_id}.json"
                or data.get("sha") != expected_sha or data.get("encoding") != "base64"):
            raise WorkerError("job_changed_or_invalid")
        encoded = data.get("content")
        if not isinstance(encoded, str) or len(encoded) > 8192:
            raise WorkerError("job_content_invalid")
        try:
            raw = base64.b64decode("".join(encoded.split()), validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise WorkerError("job_content_invalid") from exc
        if len(raw) > MAX_JOB_BYTES:
            raise WorkerError("job_content_invalid")
        return raw

    def publish_receipt(self, job_id: str, receipt: dict[str, Any]) -> None:
        # The inherited v0 method uses PUT with no SHA: it refuses to overwrite.
        GitHubCLI.publish_receipt(self, job_id, receipt)


def _ensure_outputs_root(root: Path) -> Path:
    """Keep new outputs below the already initialized fixed workspace."""
    outputs = root / "outputs"
    if outputs.exists() or outputs.is_symlink():
        if not outputs.is_dir() or not _no_link(outputs):
            raise WorkerError("output_root_invalid")
    else:
        try:
            outputs.mkdir(exist_ok=False)
        except FileExistsError as exc:
            raise WorkerError("output_root_invalid") from exc
    return outputs


def execute_fixed_job(
    root: Path, job_id: str, raw: bytes, transport: Any,
    *, now: datetime | None = None,
) -> dict[str, Any]:
    """Execute one validated job with durable reservation and exclusive output."""
    if not isinstance(job_id, str) or not JOB_ID_PATTERN.fullmatch(job_id):
        raise WorkerError("invalid_job_id")
    check_workspace(root)
    try:
        data = parse_job(raw, now=now)
    except JobValidationError as exc:
        raise WorkerError(f"invalid_job:{exc}") from exc
    if data["job_id"] != job_id:
        raise WorkerError("job_id_mismatch")

    outputs = _ensure_outputs_root(root)
    target_dir = outputs / job_id
    reservation_path = root / ".bridge-state" / f"{job_id}.json"
    if reservation_path.exists() or reservation_path.is_symlink():
        raise WorkerError("job_already_reserved")
    if target_dir.exists() or target_dir.is_symlink():
        raise WorkerError("output_already_exists")

    reservation = {
        "job_id": job_id, "status": "reserved",
        "job_sha256": hashlib.sha256(raw).hexdigest(),
        "started_at": utc_iso(utc_now()), "worker_version": WORKER_VERSION,
    }
    # Atomic O_EXCL reservation *before* any output side effect.
    try:
        with reservation_path.open("x", encoding="utf-8") as handle:
            json.dump(reservation, handle, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise WorkerError("job_already_reserved") from exc

    try:
        target_dir.mkdir(exist_ok=False)
        if not _no_link(target_dir):
            raise WorkerError("output_dir_invalid")
        target = target_dir / FIXED_OUTPUT_NAME
        with target.open("xb") as output:
            output.write(FIXED_OUTPUT_BYTES)
            output.flush()
            os.fsync(output.fileno())
    except (OSError, WorkerError) as exc:
        raise WorkerError("local_output_failed_reserved") from exc

    receipt = {
        "schema_version": 0,
        "job_id": job_id, "status": "succeeded",
        "operation": data["operation"], "worker_version": WORKER_VERSION,
        "output_file": f"outputs/{job_id}/{FIXED_OUTPUT_NAME}",
        "output_sha256": hashlib.sha256(FIXED_OUTPUT_BYTES).hexdigest(),
        "job_sha256": reservation["job_sha256"],
        "completed_at": utc_iso(utc_now()),
    }
    try:
        transport.publish_receipt(job_id, receipt)
    except Exception as exc:
        raise WorkerError("local_write_succeeded_receipt_upload_failed") from exc
    return receipt


def _has_local_state(root: Path, job_id: str) -> bool:
    path = root / ".bridge-state" / f"{job_id}.json"
    directory = root / "outputs" / job_id
    return path.exists() or path.is_symlink() or directory.exists() or directory.is_symlink()


def _acquire_listener_lock(root: Path) -> Path:
    check_workspace(root)
    lock = root / ".bridge-state" / "listener.lock"
    try:
        with lock.open("x", encoding="utf-8") as handle:
            handle.write("bounded-listener-v1\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise WorkerError("listener_already_running_or_stale_lock") from exc
    return lock


def listen(
    root: Path, transport: Any, *, max_minutes: int = 10,
    poll_seconds: int = 15,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    utc: Callable[[], datetime] = utc_now,
) -> dict[str, Any]:
    """One new, permitted job per bounded foreground session; returns a safe status.

    Pending IDs present in the first snapshot are intentionally ignored.
    This reduces the risk from historical jobs and requires the Chat to queue
    its test *after* the listener begins. No local GUI or shell is exposed.
    """
    if type(max_minutes) is not int or not 1 <= max_minutes <= MAX_MINUTES:
        raise WorkerError("max_minutes_out_of_range")
    if type(poll_seconds) is not int or not MIN_POLL_SECONDS <= poll_seconds <= MAX_POLL_SECONDS:
        raise WorkerError("poll_seconds_out_of_range")

    lock = _acquire_listener_lock(root)
    try:
        end = clock() + max_minutes * 60
        transport.verify_repository()
        baseline = set(transport.list_pending())
        # Fail closed if receipt directory is missing or unreadable.
        transport.list_receipts()
        failures = 0

        while clock() < end:
            try:
                pending = transport.list_pending()
                receipt_ids = set(transport.list_receipts())
                failures = 0
            except WorkerError as exc:
                if str(exc) not in TRANSIENT_ERRORS:
                    raise
                failures += 1
                if failures >= MAX_CONSECUTIVE_ERRORS:
                    raise WorkerError("github_repeated_failures") from exc
                sleep(min(poll_seconds * 2 ** (failures - 1), max(0.0, end - clock())))
                continue

            for job_id, sha in sorted(pending.items()):
                if clock() >= end:
                    break
                if job_id in baseline or job_id in receipt_ids or _has_local_state(root, job_id):
                    continue
                # Any malformed new request stops the session without a side effect.
                raw = transport.read_job(job_id, sha)
                try:
                    data = parse_job(raw, now=utc())
                except JobValidationError as exc:
                    if str(exc) == "job_expired":
                        baseline.add(job_id)
                        continue
                    raise WorkerError(f"invalid_new_job:{exc}") from exc
                if data["job_id"] != job_id:
                    raise WorkerError("job_id_mismatch")
                if clock() >= end:
                    break
                receipt = execute_fixed_job(root, job_id, raw, transport, now=utc())
                return {"status": "succeeded", "job_id": receipt["job_id"],
                        "output_sha256": receipt["output_sha256"],
                        "receipt_uploaded": True}
            remaining = end - clock()
            if remaining > 0:
                sleep(min(poll_seconds, remaining))
        return {"status": "timed_out", "jobs_executed": 0}
    finally:
        # A process crash preserves a stale lock for manual inspection; normal
        # timeouts, errors and Ctrl+C release the lock.
        lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen", action="store_true", required=True)
    parser.add_argument("--max-minutes", type=int, required=True)
    parser.add_argument("--poll-seconds", type=int, default=15)
    args = parser.parse_args()
    try:
        result = listen(workspace_path(), GitHubQueue(),
                        max_minutes=args.max_minutes, poll_seconds=args.poll_seconds)
        print(json.dumps(result, sort_keys=True))
        return 0
    except KeyboardInterrupt:
        print("listener_stopped_by_user")
        return 130
    except (WorkerError, OSError, ValueError) as exc:
        print(f"listener_error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
