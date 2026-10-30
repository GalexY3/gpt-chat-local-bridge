# V1 security review and verification matrix

**Review date:** 2026-10-30  
**Disposition:** Continue offline testing; do not dispatch new live jobs through an explicitly blocked chat-side action.

This is an engineering review of the prototype's code and observed records, **not** an independent security audit or approval for untrusted/privileged workloads.

## Evidence ledger

| Gate | Evidence | Status |
| --- | --- | --- |
| Manual v0 request → Windows action → GitHub receipt | Private queue/receipt GitHub fetches and user-run Windows file SHA-256 | **Passed** for a single harmless fixed-file action |
| Strict job schema and fixed operation | 14 offline unit tests in v1, user-run Windows result | **Passed** |
| Bounded listener logic and simulated queue | 32 offline unit tests in v1, user-run Windows result | **Passed**, simulated transport |
| v0 worker regression | 9 offline unit tests in v1, user-run Windows result | **Passed** |
| Total tests before transport hardening | 55 tests in 0.182 seconds, no failures/skips, user PowerShell output | **Passed** |
| **Complete expanded offline suite** | **65 tests in 0.147 seconds**, zero failures and skips, user PowerShell output | **Passed locally; NOT a live v1 dispatch** |
| Foreground listener ready state | User reported `listener_ready`; later confirmed worker stopped | **Observed**, not an executed job |
| New chat-side v1 queue write | Connected action explicitly blocked; target and receipt absent on subsequent GitHub reads | **Blocked** |
| New GitHub CLI mock transport tests | 10 methods in `tests/test_transport_offline.py`; user PowerShell transcript 2026-10-30 | **Passed locally (10/10, mocked transport)** |
| General/privileged/GUI workloads | No design/permission/implementation | **Out of scope** |

## Adversarial model and controls

| Risk | Existing control | Residual gap |
| --- | --- | --- |
| Untrusted job supplies command/path/code | Exact JSON fields; single allowlisted fixed-file operation; empty parameters | A future action registry requires separate design and authorization |
| Expired or malformed job | Strict parser; 15-minute TTL; reject unknown operations, duplicate keys and nonfinite values | Wall-clock changes and network delays can affect timeliness; failure must be observable |
| Replay / duplicate effects | Exclusive local reservation before write; no automatic repeat after receipt failure | Crash recovery needs manual inspection; state is not a distributed transaction |
| Older queued job executes when listener starts | Baseline snapshot of pending IDs | No cryptographic proof of which chat turn authorized a later item |
| Symlink / junction escape | Fixed workspace; path component checks; exclusive file creation; mocked rejection tests | TOCTOU attacks by a hostile process sharing the Windows user; real junction/symlink integration not fully tested |
| Concurrent listeners | Exclusive local `listener.lock` | Different computers with same repo not mutually excluded |
| Unbounded resource use | One job/session, <=10-minute requested lifetime, 10–60-second poll, network request timeouts, 96-file listing cap | Network requests can extend elapsed wall time; queue retention currently manual |
| Lost access / GitHub outages | Stop after repeated transient errors; fail closed on malformed listing or changed SHA | No remote observability of partial local state if receipt upload fails |
| Secret leakage | CLI stderr is suppressed in worker error paths; receipts contain relative paths and hashes | Existing host credentials remain in local GitHub CLI; account permissions should be reviewed before broader deployment |
| Host-side dispatch restrictions | Tool safety block respected; no alternate transport used | **Critical external blocker** for a fully Chat-initiated v1 round trip |

## Immediate priority order

**P0 — Trust boundary:** Obtain a supported and explicitly authorized chat-side capability for queuing the fixed-format job, without bypassing a security rejection. Until then, no claim of v1 live end-to-end operation is warranted. This is not necessarily solvable by changes to the Windows worker.

**P1 — Offline transport confidence (COMPLETE for present scope):** The user ran the expanded 65-test suite on Windows: all 65 passed, no failures/skips. The ten new tests intercept subprocess invocations, so no live `gh api` request is performed. This does **not** validate the host-side ChatGPT dispatch action, which remains blocked.

**P2 — Reliability before broadening operations:** Design explicit lifecycle and recovery state (`reserved`, `written`, `receipt_queued`, `acknowledged`), redact and bound logs, make queue retention deliberate, and plan an end-to-end test for real Windows junctions without assuming elevation.

**P3 — Future workloads:** Define capability-specific task schemas, local confirmation gates, sandboxing, data minimization and project-level authorization scopes **before** any new operation beyond a disposable fixed-file test.

## Non-goals / prohibitions

No merging to `main`, no changes to AB or other scientific repos, no service installed, no auto-start, no general shell, no credential copying, and no workaround for a blocked chat-side dispatch. An offline mock receipt must always be labeled as simulated evidence, never a Windows execution.
