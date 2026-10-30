"""Opt-in, one-shot Windows pilot worker.

No unrestricted commands, arbitrary local paths, or persistent background service.
Only a predefined fixed-file action in a dedicated workspace.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from bridge_protocol import (
    FIXED_OUTPUT_BYTES,
    FIXED_OUTPUT_NAME,
    JOB_ID_PATTERN,
    JobValidationError,
    parse_job,
)

CONTROL_REPO = "GalexY3/gpt-chat-local-bridge-control"
WORKSPACE_NAME = "gpt-chat-local-bridge-pilot"
WORKSPACE_MARKER = ".gpt-chat-bridge-pilot-v0"
MARKER_BYTES = b"GPT Chat Local Bridge isolated pilot v0\n"
MAX_API_OUTPUT = 32768


class WorkerError(RuntimeError):
    """A deliberately terse error that is safe to report in a terminal."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def workspace_path() -> Path:
    # The remote job cannot choose this path.
    return Path.home() / WORKSPACE_NAME


def _no_link(path: Path) -> bool:
    # Python >=3.13 for this pilot. Junctions matter on Windows too.
    return not path.is_symlink() and not getattr(path, "is_junction", lambda: False)()


def create_workspace(root: Path) -> None:
    """Explicit local opt-in. Refuses preexisting directories or reparse points."""
    if root.exists() or root.is_symlink():
        raise WorkerError("workspace_already_exists")
    if not _no_link(root.parent):
        raise WorkerError("workspace_parent_is_link")
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    try:
        (root / WORKSPACE_MARKER).write_bytes(MARKER_BYTES)
        (root / ".bridge-state").mkdir(mode=0o700)
    except OSError as exc:
        raise WorkerError("workspace_initialization_failed") from exc


def check_workspace(root: Path) -> None:
    if not root.is_dir() or not _no_link(root):
        raise WorkerError("workspace_not_initialized")
    marker = root / WORKSPACE_MARKER
    state = root / ".bridge-state"
    if not marker.is_file() or not _no_link(marker) or marker.read_bytes() != MARKER_BYTES:
        raise WorkerError("workspace_marker_invalid")
    if not state.is_dir() or not _no_link(state):
        raise WorkerError("workspace_state_invalid")


class GitHubCLI:
    """GitHub Contents API via preauthenticated gh CLI, never a shell."""

    def __init__(self) -> None:
        if shutil.which("gh") is None:
            raise WorkerError("gh_not_found")

    @staticmethod
    def request(endpoint: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        args = ["gh", "api", endpoint, "-H", "Accept: application/vnd.github+json"]
        data = None
        if payload is not None:
            args += ["--method", "PUT", "--input", "-"]
            data = json.dumps(payload, separators=(",", ":"))
        try:
            result = subprocess.run(
                args, input=data, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=25, shell=False,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise WorkerError("github_request_failed") from exc
        if result.returncode != 0:
            # Avoid publishing raw CLI stderr, which might contain private details.
            raise WorkerError("github_request_failed")
        if len(result.stdout.encode("utf-8")) > MAX_API_OUTPUT:
            raise WorkerError("github_response_too_large")
        try:
            parsed = json.loads(result.stdout)
        except ValueError as exc:
            raise WorkerError("github_invalid_response") from exc
        if not isinstance(parsed, dict):
            raise WorkerError("github_invalid_response")
        return parsed

    def verify_repository(self) -> None:
        info = self.request(f"repos/{CONTROL_REPO}")
        if info.get("full_name") != CONTROL_REPO or info.get("private") is not True:
            raise WorkerError("unexpected_control_repository")

    def read_job(self, job_id: str) -> bytes:
        info = self.request(f"repos/{CONTROL_REPO}/contents/jobs/pending/{job_id}.json")
        if info.get("type") != "file" or info.get("encoding") != "base64":
            raise WorkerError("unexpected_job_response")
        encoded = info.get("content")
        if not isinstance(encoded, str) or len(encoded) > 10000:
            raise WorkerError("unexpected_job_response")
        try:
            return base64.b64decode(encoded, validate=False)
        except (ValueError, base64.binascii.Error) as exc:
            raise WorkerError("invalid_job_encoding") from exc

    def publish_receipt(self, job_id: str, receipt: dict[str, Any]) -> None:
        payload = {
            "message": f"chore: pilot receipt {job_id}",
            "content": base64.b64encode(
                (json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            ).decode("ascii"),
            "branch": "main",
        }
        result = self.request(
            f"repos/{CONTROL_REPO}/contents/jobs/receipts/{job_id}.json",
            payload=payload,
        )
        if not isinstance(result.get("commit"), dict):
            raise WorkerError("github_receipt_unconfirmed")


def run_job(root: Path, job_id: str, transport: Any, *, now: datetime | None = None) -> dict[str, Any]:
    """One-shot execution. Durable local reservation precedes the side effect.

    A crash after reservation prevents silent re-execution. Inspect manually to
    recover; there is no automatic retry for v0.
    """
    if not isinstance(job_id, str) or not JOB_ID_PATTERN.fullmatch(job_id):
        raise WorkerError("invalid_job_id")
    check_workspace(root)
    transport.verify_repository()
    raw = transport.read_job(job_id)
    try:
        job = parse_job(raw, now=now)
    except JobValidationError as exc:
        raise WorkerError(f"invalid_job:{exc}") from exc
    if job["job_id"] != job_id:
        raise WorkerError("job_id_mismatch")

    target = root / FIXED_OUTPUT_NAME
    state_path = root / ".bridge-state" / f"{job_id}.json"
    if not _no_link(target) or target.exists():
        raise WorkerError("target_already_exists_or_link")
    if not _no_link(state_path) or state_path.exists():
        raise WorkerError("job_already_reserved")

    started = utc_now()
    reservation = {
        "job_id": job_id,
        "status": "reserved",
        "job_sha256": hashlib.sha256(raw).hexdigest(),
        "started_at": utc_iso(started),
    }
    try:
        with state_path.open("x", encoding="utf-8") as marker:
            json.dump(reservation, marker, sort_keys=True)
            marker.flush()
            os.fsync(marker.fileno())
    except FileExistsError as exc:
        raise WorkerError("job_already_reserved") from exc

    # Exclusive create: never overwrite an existing file, even after a crash.
    try:
        with target.open("xb") as out:
            out.write(FIXED_OUTPUT_BYTES)
            out.flush()
            os.fsync(out.fileno())
    except OSError as exc:
        raise WorkerError("local_write_failed_reserved") from exc
    digest = hashlib.sha256(FIXED_OUTPUT_BYTES).hexdigest()
    receipt = {
        "schema_version": 0,
        "job_id": job_id,
        "status": "succeeded",
        "operation": job["operation"],
        "output_file": FIXED_OUTPUT_NAME,
        "output_sha256": digest,
        "job_sha256": reservation["job_sha256"],
        "completed_at": utc_iso(utc_now()),
    }
    # The local reservation prevents duplicates even if publishing fails.
    try:
        transport.publish_receipt(job_id, receipt)
    except Exception as exc:
        raise WorkerError("local_write_succeeded_receipt_upload_failed") from exc
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--init", action="store_true", help="Create dedicated isolated pilot workspace")
    actions.add_argument("--run-id", metavar="JOB_ID", help="Run one explicitly selected queued pilot job")
    args = parser.parse_args()
    root = workspace_path()
    try:
        if args.init:
            create_workspace(root)
            print("pilot_workspace_initialized")
        else:
            receipt = run_job(root, args.run_id, GitHubCLI())
            print(json.dumps({"receipt_uploaded": True, "job_id": receipt["job_id"],
                              "output_sha256": receipt["output_sha256"]}, sort_keys=True))
        return 0
    except (WorkerError, OSError, ValueError) as exc:
        print(f"pilot_worker_error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
