# Windows worker v1 — bounded foreground listener (development only)

**Status: code and adversarial tests drafted. Not installed, not run on the user's Windows, and not authorized for live queue execution.**

## Version separation

- The tested v0 worker remains `bridge_worker.py`. Its previous `--init` and `--run-id` commands still exist.
- The new opt-in listener is a separate file: `bridge_listener.py`.
- V1 reads the same strict v0 JSON job schema and executes only the same fixed-file operation. It does **not** accept instructions to execute commands, Python scripts, URLs, arbitrary file paths, browser actions or Windows UI events.
- V1 supports one new job per session with a separate `outputs/<job_id>/chat_local_bridge_pilot.txt` and a durable reservation file.

## Review + offline tests (not permission to dispatch live jobs)

The user already has the public repo cloned on Windows and is currently on `feat/pilot-schema-v0`. Once this branch is ready for user review, in ordinary PowerShell:

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git fetch origin
git switch --track origin/feat/v1-bounded-listener
py -3 -m unittest discover -s tests -v
```

If the branch exists locally, use `git switch feat/v1-bounded-listener` then `git pull --ff-only`; do not delete or overwrite local changes. No `pip` or `uv` install is required for these standard-library unit tests.

**STOP after tests.** Do not launch the listener, submit tasks to the control repo, create scheduled jobs, or enable background start-up until a separate user authorization after successful Windows test output.

## Planned foreground run (separate future authorization gate)

Only once the user approves the live test:

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

## Review gates before claiming v1 complete

- Full offline tests passed on Windows, with actual output and Python version recorded.
- Explicit live-test authorization from the user.
- One newly queued private test job **after** `listener_ready`.
- A single completed output in a job-specific directory, receipt with matching hashes, and clean listener exit.
- No changes to the public `main` branch, scientific repositories, or private job queue until authorized.
