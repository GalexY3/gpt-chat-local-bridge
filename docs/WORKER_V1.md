# Windows worker v1 — bounded foreground listener (development only)

**Status (2026-10-30):** The user ran 55/55 original v1 offline tests successfully on Windows. A live, foreground, user-authorized listener was started and reported `listener_ready`; the subsequent attempted chat-side GitHub job creation was blocked by connection security controls, and no new job or receipt was observed. The user confirmed stopping the listener. Therefore the **v1 live end-to-end acceptance test is incomplete**. Ten additional mock transport tests have now passed on Windows as part of the **65/65** complete offline suite (0.147 seconds, no failures/skips). They do **not** resolve the blocked ChatGPT-side dispatch.

## Version separation

- The tested v0 worker remains `bridge_worker.py`. Its previous `--init` and `--run-id` commands still exist.
- The new opt-in listener is a separate file: `bridge_listener.py`.
- V1 reads the same strict v0 JSON job schema and executes only the same fixed-file operation. It does **not** accept instructions to execute commands, Python scripts, URLs, arbitrary file paths, browser actions or Windows UI events.
- V1 supports one new job per session with a separate `outputs/<job_id>/chat_local_bridge_pilot.txt` and a durable reservation file.

## Review + offline tests (not permission to dispatch live jobs)

The user already has the public repo cloned on Windows and is on `feat/v1-bounded-listener`. For the newly added offline transport tests, use ordinary PowerShell:

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git pull --ff-only
py -3 -m unittest discover -s tests -v
```

If the branch exists locally, use `git switch feat/v1-bounded-listener` then `git pull --ff-only`; do not delete or overwrite local changes. No `pip` or `uv` install is required for these standard-library unit tests.

**STOP after tests.** The preceding live attempt was closed by the user. Do not restart the listener, submit tasks to the control repo, create scheduled jobs, or enable background startup while the chat-side dispatch action remains blocked.

## Planned foreground run (separate future authorization gate)

A previous user-authorized live attempt ended without dispatch. **The following is illustrative only, not an instruction to restart:**

```powershell
py -3 bridge_listener.py --listen --max-minutes 10 --poll-seconds 15
```

The listener:
1. Checks the existing isolated pilot workspace and creates a lock. A lock left by an interrupted/crashed process requires inspection, never an automatic override.
2. Verifies the precise private control repo and default `main` branch.
3. Captures currently pending job IDs **as a baseline**; it does not execute jobs already present when it starts.
4. Prints `listener_ready` after successful initialization. **Only then** should the connected Chat publish one fresh short-lived job.
5. Polls every 15 seconds, within a maximum 10-minute foreground session (up to additional bounded network request time). Stops after one permitted job, a terminal validation error, repeated GitHub errors, timeout, or Ctrl+C.
6. Creates one per-job output directory under the fixed local pilot workspace and uploads a redacted receipt. Does not retry a side effect on a receipt upload failure.

No Windows service, startup task or background process is installed. `Ctrl+C` stops the normal foreground process. A system crash can leave a stale lock by design.

## Safety limits and known residual risks

- This is still a **single-user pilot**. Exclusive local locking prevents parallel listeners in the same workspace, but GitHub file operations alone are not a distributed lock across *different computers*. Do not start workers on multiple machines with the same control repository.
- As with the v0 pilot, this is not a hardened OS sandbox. A separate hostile local process running with the same user's permissions can interfere with filesystem operations or symlinks between checks. Use only disposable test data. V1 refuses detected symlinks and junctions; it does not claim to eliminate all time-of-check/time-of-use races.
- The listener reads the job contents from the explicit private repository and pinned branch, and binds file read to the SHA exposed in the directory listing. That is not cryptographic proof of a particular ChatGPT conversation's identity.
- The `jobs/pending` and `jobs/receipts` directories must exist in the private control repo. An invalid directory listing stops the session; v1 deliberately does not create or seed any operational queue.
- Queue listings are capped at 96 entries per directory. Historical jobs may require an explicit, audited retention policy later. Never manually delete audit entries during an active pilot.
- Publishing a GitHub receipt is not a substitute for local file verification. The final live acceptance check requires retrieving the receipt and checking the physical file's SHA-256 on Windows.
- Multiple code paths have offline tests, but the current prototype is **not independently security audited** and should not be exposed to sensitive data or privileged tasks.

## Windows adversarial-test coverage

The first user-reported v1 suite discovered 54 tests: 53 passed and 1 was skipped because the local Windows account could not create a real symbolic link. This is not equivalent to 54 passes. The subsequent source revision replaced that privilege-dependent test with deterministic simulation of a symlink metadata response, and added an analogous simulated Windows junction check. The original 55-test suite ran on Windows with **55 passes, 0 skips, 0 failures**. Ten separate GitHub CLI transport tests were subsequently added, and the user reran the **entire 65-test suite** on Windows: **65 passes, 0 skips, 0 failures**, completed in 0.147 seconds. These transport tests mock the CLI rather than sending live GitHub requests.

The simulated tests exercise the worker's refusal path without requiring administrator or Developer Mode permissions. They do **not** independently validate real Windows filesystem reparse-point behavior under all circumstances. Any later genuine filesystem integration test must use a disposable workspace, be separately reviewed, and never require elevated privileges to pass the basic unit test suite.

## Current connector boundary

Read [ADR-0002](ADR-0002-DISPATCH-BOUNDARY.md) before any further live workflow. The attempted connected GitHub creation of a new queue item returned a host security block. A subsequent fetch of the proposed pending job and receipt returned 404. This is **not evidence of a Windows worker error**. The reason for the host decision cannot be independently verified here.

The mock transport tests in `tests/test_transport_offline.py` do not contact GitHub and do not cure the blocked chat-side write permission. Do not switch to alternate paths, browser automation, another connector or manual credential submission as a workaround for that block.

## Review gates before claiming v1 complete

- Full offline tests passed on Windows, with actual output and Python version recorded.
- A new explicitly supported and authorized chat-side dispatch path; the previous connected GitHub job creation was blocked.
- One newly queued private test job **after** `listener_ready`.
- A single completed output in a job-specific directory, receipt with matching hashes, and clean listener exit.
- No changes to the public `main` branch, scientific repositories, or private job queue until authorized.
