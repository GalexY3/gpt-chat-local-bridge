# ADR-0001 — Time-bounded polling instead of an unattended remote shell

**Status:** Proposed. **Scope:** post-pilot v1 design. Not implemented, authorized, deployed, or executed.

## Context

On 2026-10-30 the one-shot pilot completed end-to-end from ChatGPT Chat through a private GitHub request, Windows manual worker, and GitHub receipt. The local file's SHA-256 was subsequently checked directly by the user and matched the receipt.

The pilot still needs a manually typed `--run-id`. The current fixed output name is intentionally exclusive and already exists after the first run, so another request cannot reuse that path as implemented.

## Decision proposed

Introduce an **explicitly started, foreground, time-bounded listener** rather than a daemon or a general remote command executor.

1. The local user launches an opt-in command such as `py -3 bridge_worker.py --listen --max-minutes 10` after reviewing code/tests. Nothing auto-starts with Windows.
2. The worker polls only the configured **private** control repository and trusted branch through authenticated outbound HTTPS at a bounded interval (for example, >= 10 seconds).
3. A task is a strict JSON envelope with a fixed known `operation`. Remote job content must not supply shell commands, Python code, local paths, URLs, dynamic module names, or executable filenames.
4. Select an unprocessed, short-lived task deterministically. Before execution, verify exact repository identity and visibility, schema, expiry, operation, workspace profile, job ID, deduplication status, and all local path safety properties. No job is executed just because a public repository PR or issue contains text.
5. Permit **only one fixed benign test operation per process invocation** in the first listener release. The process exits after success, explicit error, timeout, or user interruption (`Ctrl+C`). This keeps the first unattended dispatch window narrow.
6. Each task gets a separate, safely derived output directory under the already initialized pilot workspace, such as `outputs/<validated-job-id>/`. The target must be created exclusively, never via a remotely supplied path; refuse links, junctions and unexpected existing paths. Durable local reservation precedes the side effect. Keep bounded space use.
7. Write a minimal redacted receipt, including task identity, operation, outcome, output hash, start/completion timestamps, and code version. Verify receipt upload; a failed upload does not trigger automatic re-execution.
8. Polling must not continue endlessly after a poisoned/expired task, repeated network errors, or loss of permissions. Explicit timeouts, backoff, clear error codes and maximum attempts are required. Public GitHub content cannot activate the listener.
9. Keep a locally operated emergency stop and no elevated privileges, Windows service registration, scheduled task, personal browser profile access, GUI automation or project-repository write access in this milestone.

## Security and correctness tests required before real listener dispatch

- Strict job-envelope validation: unknown fields, unknown operations, missing/invalid expiry, IDs with traversal characters, excessive payloads and non-UTF-8 input.
- Selection and de-duplication: zero jobs, already acknowledged jobs, wrong path/branch, expired jobs, maliciously named jobs and concurrent workers.
- Durable reservation, crash during execution, receipt upload failure, partial output, and retry logic with **no duplicate side effect**.
- Workspace safety: existing file, symlinks/reparse points, directory junctions, non-initialized workspace and denied permissions.
- Boundaries: exit after one operation, fixed maximum lifetime, clean Ctrl+C termination, no externally supplied commands, and all logs redacted.
- Deterministic offline tests with a fake GitHub transport before any live run. Run them on Windows and preserve actual output.

## Scope that remains out of bounds

This milestone does not confer autonomous reasoning upon ChatGPT between turns. The listener merely picks up task envelopes written by an authorized connected chat and runs allowlisted, predetermined behavior. More flexible execution of science and GUI automation will require independent safety gates and explicit user authorization.

## Completion criteria

- Public branch code and offline tests reviewed.
- User-reported Windows test suite passes with real output.
- User deliberately launches bounded foreground listener.
- Chat writes a new short-lived safe job to the private queue.
- User does not need to type a job ID.
- Exactly one benign file appears in a **new per-job** directory.
- Private receipt is independently fetched by Chat; file hash agrees with the user-side check.
- Listener exits as specified.

No automatic merge to `main` or private job dispatch is implied by approval of this document.
