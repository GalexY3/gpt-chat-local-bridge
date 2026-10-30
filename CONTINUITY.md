# Project continuity

Updated: 2026-10-30. This document is the public, persistent project handoff.

## Purpose

Build an experimental bridge from ordinary ChatGPT Chat to a user-installed Windows worker. GitHub is the message transport. A connected GitHub repository does not give ChatGPT direct access to local applications or files. The original v0 worker was initialized and executed manually on Windows; the v1 bounded listener is not yet validated or activated there. The project aims to support scientific workflows across independent projects, without changing their repositories during the pilot.

## Repositories

- Public source: https://github.com/GalexY3/gpt-chat-local-bridge
- Private task transport: https://github.com/GalexY3/gpt-chat-local-bridge-control

Both repositories have been accessible through the GitHub connection. The private repository contains documentation only; it has no pending jobs.

## Work completed in GitHub

- Public README created on main, commit 4850d85e65df7c60309b7cd492245d7925a5bb5c.
- docs/PILOT_PROTOCOL.md on main, commit 6938a5b5cdd07d1b5b83911e0b9841f0e51c47ef.
- Private control README updated, commit e6f0891c493797a9951651bf641d69346746894c.
- Permanent restart mechanism established on public main (2026-10-30): `CONTINUITY.md`, `AGENTS.md`, `START_HERE.md`, plus a README link. `AGENTS.md` documents the convention that every future substantive project exchange should update this canonical file after verifying the latest GitHub SHA. Known commits: continuity creation `4eb47b821c18ca7c9a7a882382cf7a6aa9fa65ea`; AGENTS `549450077056e44159db2f00443758fc228b2709`; START_HERE `fb52c1c500019122d4425a70db8c7aff3e904fbe`; README link `c9a0acafaac688e0322816407672db916bb89c39`.
- Public feature branch feat/pilot-schema-v0 includes bridge_protocol.py, tests/test_bridge_protocol.py and docs/WINDOWS_PREREQUISITES.md. Feature branch HEAD observed 2026-10-30 after cache ignore addition: bbc9ca5fb1fee0271d1f2796afd8f6dd4831df34. Verify live HEAD before editing.

**Windows testing observed through user-provided PowerShell transcripts:** initial 11 protocol tests passed (11/11, 0.004 s); subsequently the user pulled the one-shot worker and reports **20/20 tests PASS, 0.052 s** with Python 3.14.3. `git pull --ff-only` fast-forwarded the feature branch from d501807 to b144727. Their `git status --short` showed only untracked Python cache directories (`__pycache__/`, `tests/__pycache__/`). This is a **user-reported Windows execution**, not code remotely executed by this assistant. After that report, `.gitignore` was added on the feature branch to ignore those caches, commit bbc9ca5fb1fee0271d1f2796afd8f6dd4831df34. **This historical status was superseded by the verified first pilot execution recorded below.**

## User-reported Windows diagnostics

- Python 3.14.3 is the default real Python interpreter accessed via py -3.
- Python 3.13 is also installed.
- Git, GitHub CLI, and uv are present.
- GitHub CLI is authenticated to the account that owns both repos.
- GitHub CLI can access the private control repository and confirms its visibility is private.
- These diagnostics come from user-shared PowerShell output, not remote execution by ChatGPT.

## Safety decisions

- Public repository contains source/docs; private repository contains future job messages and minimal receipts.
- Initially permit only a predefined, harmless fixed-file operation inside a dedicated test workspace; never dispatch arbitrary commands or paths.
- No administrator privileges, sensitive data, passwords, tokens, unreviewed public code or personal desktop access.
- No changes to Politics Fantasy League, LARP, Mercados de pareja, or AB research repositories during the pilot.
- No auto-merges to main and no license chosen yet.
- A submitted job is not proof of execution. Require an observed local action plus a return receipt and hash.

## Latest verified checkpoint (2026-10-30, Europe/Madrid)

**FIRST REAL END-TO-END PILOT SUCCEEDED, INCLUDING USER-SIDE PHYSICAL FILE VERIFICATION.** This is a verified manual single-shot round trip, not an unattended agent or an independent remote forensic inspection of Windows.

1. User-provided PowerShell confirms the checkout was fast-forwarded to feature commit `bbc9ca5fb1fee0271d1f2796afd8f6dd4831df34`, 20/20 unit tests passed in 0.052s, and `py -3 bridge_worker.py --init` printed `pilot_workspace_initialized`.
2. ChatGPT's GitHub connector created a task in the **private** control repo: `jobs/pending/pilot-20261030-2209.json`, commit `80e821c1e27d629f66a38eac952f60e89f4209e5`; task expiry `2026-10-30T21:22:00Z` and only permitted operation `write_fixed_test_file`.
3. User-provided PowerShell confirms explicit execution `py -3 bridge_worker.py --run-id pilot-20261030-2209` and output `{"job_id":"pilot-20261030-2209","output_sha256":"b0cba8c8a2710c8a32599b3088a34260493eb773d7ccc4cb0e87c5f9f7f6ac73","receipt_uploaded":true}`.
4. ChatGPT **independently fetched** `jobs/receipts/pilot-20261030-2209.json` from the private control repo, blob SHA `8acc7e9e44baa0bef35bd75db23bbdfe3c2c8e89`. It contains `status=succeeded`, `completed_at=2026-10-30T21:09:39Z`, `output_file=chat_local_bridge_pilot.txt`, `output_sha256=b0cba8c8a2710c8a32599b3088a34260493eb773d7ccc4cb0e87c5f9f7f6ac73`, `job_sha256=f9ac0450236464140458ae093d1976a6055d297f1de782a9accaf6ca576b5c11`.
5. ChatGPT independently computed SHA-256 from the *exact submitted UTF-8 job JSON bytes* and from `b"GPT Chat Local Bridge pilot v0\n"`; **both match the corresponding hashes in the receipt**. The receipt completion time precedes expiry. The physical local file's hash was subsequently checked directly in Windows, as recorded below. The evidence consists of user-provided PowerShell output plus a GitHub receipt retrieved separately; this is not independent remote forensic inspection of Windows.

**Additional physical-file verification (user-reported Windows PowerShell):** `Test-Path (Join-Path $HOME "gpt-chat-local-bridge-pilot\\chat_local_bridge_pilot.txt")` returned `True`. `Get-FileHash (...)-Algorithm SHA256` returned `B0CBA8C8A2710C8A32599B3088A34260493EB773D7CCC4CB0E87C5F9F7F6AC73`, exactly matching the SHA-256 in the independently retrieved GitHub receipt. This closes the manual pilot acceptance criteria. **Do not rerun the consumed job:** the durable reservation and exclusive output are intentional.

**Next-stage design was documented, but not implemented:** `docs/ADR-0001-BOUNDED_LISTENER.md` was created on public feature branch `feat/pilot-schema-v0`, commit `4dd776047081f6c40c90c29f88cba0ef6c89673c`. It proposes foreground opt-in polling with an explicit maximum lifetime, one job per session, strict allowlists, per-job isolated outputs, idempotency, redacted receipts, offline tests, and manual kill-switch. No daemon, Windows service, scheduled task, broad shell access, GUI control, or background automation has been enabled. The design is **proposed, not yet user-reviewed or authorized for execution**.

**Capability achieved:** Manual, single-shot ChatGPT Chat → GitHub private job → Windows worker → private GitHub receipt → ChatGPT Chat. The system does **not** yet run continuously, poll autonomously, execute arbitrary code, operate Windows GUI, or support general scientific projects.

**Historical next action (v1 design now implemented on a feature branch):** Review the proposed bounded-listener design in `docs/ADR-0001-BOUNDED_LISTENER.md` on feature branch, and—if the user wishes to continue—implement it on a feature branch, with offline unit tests and no live unattended execution before the user has reviewed the updated protocol and tests. Address the present v0 limitation that a second job cannot reuse the one existing fixed output. Update and run tests on Windows before any new private dispatch. Do not automatically merge to `main`. The user has not yet explicitly approved a continuously running service or generalized execution on their PC.

## Development checkpoint: v1 bounded listener (2026-10-30)

The user authorized **development and offline tests only** for v1, with no new live dispatch or service activation before a separate approval. Public branch: `feat/v1-bounded-listener`, last verified HEAD `5f03087b23f1104e6b746f615a460e7eea0cfa43`. The public `main` branch has not received the implementation.

New source: `bridge_listener.py` provides an opt-in bounded foreground listener with a ten-minute maximum, startup queue baseline, private GitHub repository checks, one operation per session, per-job output directories, local lock, idempotent reservations, SHA-256 receipts and safe termination. Protocol parser additionally rejects duplicate JSON keys and nonfinite JSON. Documentation: `docs/WORKER_V1.md`, updated `docs/ADR-0001-BOUNDED_LISTENER.md`.

**54 test methods are written**: 14 protocol, 9 previous worker, 31 v1 listener/adversarial cases. **They have NOT been run on Windows or independently validated in this turn.** No v1 listener has been launched. No new private job, system service, background process, or GUI automation has been activated. Prior manual v0 pilot remains successful and verified.

The single-computer pilot is not a hardened sandbox: locking is local rather than distributed, filesystem checks have possible local same-user race conditions, and queue write authorization does not prove which chat initiated an operation.

**Next local test, before any live queue use:**

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git fetch origin
git switch --track origin/feat/v1-bounded-listener
py -3 -m unittest discover -s tests -v
```

Expected test discovery is 54, not a claimed passing result. If the branch already exists locally, use a normal switch and fast-forward pull. Review results, fix errors if any, and seek separate approval before a live v1 session. Do not merge to `main` automatically.

## Latest Windows v1 test result and portability repair (2026-10-30)

The user provided a new PowerShell transcript (also attached as `Texto pegado.txt`) showing their clean checkout, successful `git fetch origin`, switch to `feat/v1-bounded-listener`, and execution of `py -3 -m unittest discover -s tests -v` on Windows/Python 3.14.3. **Exactly 54 tests discovered, 53 passed, 1 skipped, 0 failed; duration 0.141s, output `OK (skipped=1)`.** The skipped case was `test_symlinked_outputs_dir_refused`, because Windows did not allow real symlink creation in this test environment. Do not report this as 54/54 passed.

In response, the assistant amended the test **only on the v1 feature branch**: the symlink check now uses deterministic simulated `Path.is_symlink` OS metadata instead of requiring privileged symlink creation; a second test similarly exercises `Path.is_junction` rejection without requiring `mklink` or elevation. `tests/test_bridge_listener.py` changed in commit `ff1d5f27c25578e5c430a55c6a21fd8127ab8d4d`. `docs/WORKER_V1.md` was updated to distinguish mocked checks from actual Windows filesystem integration tests, commit `41932d16a249c01c247aa8b2fb3bb919352d2a08`. **Revised source defines 55 tests; those 55 have NOT yet been run on Windows or otherwise independently executed.** The use of `unittest.mock.patch.object(Path, "is_symlink"/"is_junction", autospec=True)` was smoke-checked with Python 3.13 in a separate isolated environment, not a full project-suite run.

**Next user step:** Their local working branch is already `feat/v1-bounded-listener`. From regular PowerShell, run:

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git pull --ff-only
py -3 -m unittest discover -s tests -v
```

If there are local tracked changes, inspect before pulling. Expected test discovery is 55. **Do not claim 55 pass until seeing the actual returned output.** No GitHub control jobs, listener process or services were started; user approval for LIVE v1 execution has not been granted. Preserve that approval boundary. `main` still contains project continuity, not the v1 feature implementation.

## Latest v1 Windows test acceptance (2026-10-30)

**User-reported PowerShell result: 55 tests discovered, 55 PASS, 0 failed, 0 skipped; 0.182 s; final `OK`.** The user's checkout was clean before `git pull --ff-only`, which fast-forwarded `feat/v1-bounded-listener` from `5f03087` to `41932d1`. Both simulated filesystem safety tests, `test_symlinked_outputs_dir_refused` and `test_windows_junctioned_outputs_dir_refused`, now report `ok`. This validates their *mocked rejection paths*, not all real Windows reparse-point behavior. This is a user-supplied Windows test transcript, not execution by ChatGPT.

**Verified GitHub state:** Feature branch `feat/v1-bounded-listener` HEAD `41932d16a249c01c247aa8b2fb3bb919352d2a08`; the private control repo is still private on `main`. No v1 listener started or live v1 job dispatched. The earlier manual v0 round trip remains complete. The implementation is not merged into public `main`, and no service/daemon or arbitrary command execution is enabled.

**Authorization boundary:** The user explicitly authorized v1 *development*, but required separate approval before any live listener or new private job. The offline test gate is now satisfied. **Do not start a live listener or enqueue a new job without the user's new explicit authorization.**

**Next action:** Ask the user to authorize one live, foreground, time-bounded v1 acceptance test with a single harmless fixed-file operation. After authorization, instruct the user to run `py -3 bridge_listener.py --listen --max-minutes 10 --poll-seconds 15` from their existing checkout, then wait for its exact `listener_ready` stdout before adding one fresh short-lived job to the PRIVATE queue. The listener ignores all jobs present at startup and exits after one completed operation or timeout; it does not install as a Windows service or run at login. Verify the receipt on GitHub, request a direct Windows file hash comparison, and update this file. If `listener_ready` has not been observed, do not publish a job. If more than ten minutes have elapsed, restart only with the user's approval and a fresh task, not a replay. No merge to `main` without authorization.

## Live v1 acceptance test authorization and preflight (2026-10-30, Europe/Madrid)

**The user has now explicitly authorized exactly ONE controlled LIVE v1 foreground listening test**, following `docs/ADR-0001-BOUNDED_LISTENER.md`. Conditions: user manually launches listener for at most 10 minutes, assistant waits for user-confirmed exact `listener_ready` before enqueuing ONE fresh harmless fixed-file task to the PRIVATE control repo, then fetches receipt and verifies SHA-256; no Windows services, generalized command execution, AB repository edits or merges to public `main`.

**Preflight verified by connected GitHub tools:** current feature branch `feat/v1-bounded-listener` HEAD `41932d16a249c01c247aa8b2fb3bb919352d2a08`; `bridge_listener.py` contains a readiness print after its initial queue snapshot and a 10-minute maximum lifetime; private control repo `GalexY3/gpt-chat-local-bridge-control` remains private on `main`. The private `jobs/pending` directory contains ONLY the previously completed `pilot-20261030-2209.json`; `jobs/receipts` contains its receipt. Thus the fresh v1 job must use a new identifier, and the listener should ignore the historical job via its initial snapshot.

**At this checkpoint, NO v1 listener start has been confirmed and NO v1 job has been enqueued.** The next assistant response must give the user this PowerShell command on the already checked-out feature branch:

```powershell
cd $HOME\gpt-chat-local-bridge
py -3 bridge_listener.py --listen --max-minutes 10 --poll-seconds 15
```

User must report seeing the exact stdout `listener_ready` while the window remains running. **Do not create a job just because the command was recommended.** Only after the user confirms `listener_ready` and the session is still inside its time window should the assistant obtain the target-local current time, select a fresh short-lived `job_id`, and enqueue the strict v0 JSON job with `write_fixed_test_file`, `isolated-pilot`, empty parameters and an expiry within 15 minutes (preferably within the remaining listener window). After execution, independently inspect `jobs/receipts/<job_id>.json`, verify expected SHA-256 against the exact fixed bytes, and ask the user to check the physical per-job output. If the process has timed out, been stopped, or errored, do not enqueue; inspect and coordinate a fresh explicit start instead. The live test authorizes a single job only, not a permanent agent.

## Latest v1 live-test attempt (2026-10-30)

The user reported `listener_ready` in foreground PowerShell. ChatGPT attempted to enqueue one fixed-file task, `pilot-v1-20261030-2337`, via the private GitHub connector. The write was blocked by security controls. Follow-up GitHub reads of the pending job and receipt both returned 404. **No new v1 job or receipt was found; the live acceptance test is not complete.**

The user was instructed to stop the listener via Ctrl+C or allow its ten-minute timeout. Do not circumvent the rejected write with another transport. Existing v0 manual success and v1 55/55 offline tests remain valid; no merge or service activation occurred.

## Follow-up engineering after stopped v1 listener (2026-10-30)

**User confirmed the v1 listener is stopped** and instructed continued development. No further live dispatch was authorized; the rejected chat-side job creation was not retried through another transport. Read-only GitHub inspection confirmed the private `jobs/pending` directory still contains only `pilot-20261030-2209.json`, from the previously completed manual v0 pilot. The v1 live acceptance test remains **BLOCKED** at chat-side dispatch, not a proven Windows listener failure.

**New feature-branch commits verified** on public `feat/v1-bounded-listener`:
- `4866feb6ab9a01f72be0d75ebfff175cb4e44bb8`: added `tests/test_transport_offline.py` with **10 new offline test methods** mocking GitHub CLI GET and PUT calls, fixed endpoint usage, no-shell execution, error redaction, timeouts, malformed/oversized responses, path/SHA validation and receipt encoding. These tests were **written but not yet executed in the user's Windows or independently verified**. Prior 55/55 passing Windows suite remains valid. **Current source count: 65 test methods**.
- `60dc5e7b978b094af372bdde22357f5a2e43846e`: added `docs/ADR-0002-DISPATCH-BOUNDARY.md` to distinguish a host security block from a Windows bug and forbid changing connectors, transports or credentials merely to bypass the rejected job.
- `96bfebd3aca1b8c021f49018da69c7345d9f466d`: updated `docs/WORKER_V1.md` to reflect actual user-run Windows validation and the unsuccessful live trial.
- `de1fb9aa976451d415f26bf5242b228b2e09a7c6`: added `docs/SECURITY_REVIEW_V1.md` with an evidence matrix, threat model, residual risks and prioritization.
- Feature branch latest observed HEAD: **`de1fb9aa976451d415f26bf5242b228b2e09a7c6`**. Recheck before editing. No merge to `main`, no edits to the private control queue or scientific repositories, no service/GUI execution.

**NEXT CONCRETE STEP:** Run the expanded offline suite only, from the already-existing `feat/v1-bounded-listener` checkout, in ordinary Windows PowerShell (no administrator rights):

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git pull --ff-only
py -3 -m unittest discover -s tests -v
```

Expected discovery: 65 test methods, **not a passing result until user supplies the real output**. Stop if local tracked changes exist. These tests mock `subprocess.run` and do not write to the control repository. The broader product blocker remains the ChatGPT-side connector security rejection; the internal cause cannot be verified. Do not restart the listener, reattempt the forbidden write or propose a covert alternative. Further live work requires a supported approved dispatch mechanism and separately scoped user authorization. Continue updating this public continuity document before each substantive project response.

## Latest Windows regression results (2026-10-30)

The user ran the complete expanded suite on Windows from a clean local `feat/v1-bounded-listener` checkout. Their PowerShell log confirms `git pull --ff-only` fast-forward from `41932d1` to `de1fb9a`, followed by `py -3 -m unittest discover -s tests -v`: **65 tests discovered, 65 passed, 0 failed, 0 skipped, 0.147 seconds; final `OK`**. All ten new mocked GitHub CLI transport tests passed. This is user-reported Windows execution, not a live test by the ChatGPT connector.

The assistant subsequently updated `docs/SECURITY_REVIEW_V1.md` on `feat/v1-bounded-listener` (commit `ff17ed1d99b8460e45183f5e743ce4cc7f2b3def`) and `docs/WORKER_V1.md` (commit `c7218aa4929bf83f7bbb403220e800fc8b3d757d`) to record 65/65 accurately. Current feature branch HEAD: `c7218aa4929bf83f7bbb403220e800fc8b3d757d`; recheck before editing. These updates are documentation only, so the user's last test run remains a valid verification of the unchanged program/test code.

**Current capability gate:** Manual v0 end-to-end round trip remains verified. V1 listener startup (`listener_ready`) was user-observed, then user stopped it. New ChatGPT-side private queue creation was explicitly blocked by host security controls; no v1 job or receipt was found. The host's internal block reason is unknown. **65/65 passing simulated/offline tests do not establish a real ChatGPT → GitHub → Windows v1 round trip.** No fresh private job has been submitted, no service installed, no AB/project repo altered, and no merge to `main` occurred.

**Next research/engineering decision:** Stop adding low-value mock tests until there is a clearly supported and authorized chat-side dispatch mechanism. Document any vendor-supported capabilities and permissions by authoritative sources; do not treat an alternate transport as a workaround for the blocked write. The existing offline worker is ready for code review and targeted reliability fixes. Do not ask the user to restart the listener or send another job without a new, supported path and explicit approval. Maintain `CONTINUITY.md` after each substantive turn.

## Documented transport support research (2026-10-30)

After the 65/65 user-reported Windows offline test success, the assistant consulted current **official OpenAI Help Center** documentation:
- `https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt`: standard ChatGPT GitHub integration is documented as read-only for code reading and analysis, with writing/editing directed to Codex.
- `https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt`: custom MCP app write/modify actions are documented under current plan/workspace limits, particularly Business/Enterprise/Edu full MCP beta; host may ask for approval or block risky actions.
- `https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt`: managed custom MCP connections require workspace permissions; remote/supported secure tunnel connectivity is described.

The documentation does **NOT** explain the internal reason for the specific blocked v1 private queue write, and is not proof of the user's individual plan eligibility or specific tool authorizations. Earlier successful GitHub writes via available connector tools, including the verified v0 job, remain factual and must not be erased or rewritten as impossible. Individual permission for each write is separate from general tool availability.

A source-linked documentary note was created at `docs/TRANSPORT_SUPPORT_RESEARCH.md` on public development branch `feat/v1-bounded-listener`, commit `95568c73a891d6997144da9381a425943f80cac5`. This proposes **no live dispatch** or bypass: custom MCP write actions are only a possible future product architecture subject to eligibility, official authorization, hosting/security review and separate user consent. The existing block must not be evaded through alternative transports or disguised requests.

**Current decision:** Pause new mock-test development and live bridge operations until a supported authorized dispatch capability is identified. V0 manual E2E verification and v1 65/65 offline pass stand. The listener is stopped; v1 live E2E is not verified. No new control jobs, services, merges or AB project changes. Keep documenting exact verified facts and report blockers without promising future deployment.

## Decision checkpoint: actionable options after transport block (2026-10-30)

In response to the user's request for a decision rather than more tests, the assistant confirmed the v1 worker's local test milestone (65/65 Windows offline passes) and the **unresolved chat-side dispatch blocker**. The system does not currently meet the desired normal-ChatGPT-Chat-to-Windows automatic execution requirement. It would be inaccurate to call it a functioning automatic local bridge.

Official OpenAI documentation reviewed in this exchange:
- `https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt`: full custom MCP write/modify capability is currently limited to Business and Enterprise/Edu; Pro custom MCP servers have read/fetch permissions. Eligibility of this specific user account is not verified.
- `https://help.openai.com/es-es/articles/20001275-chatgpt-work-and-codex`: Work and Codex, where plan/permissions allow, are separate supported execution experiences; Work Local and Codex Local can operate with local files/apps.
- `https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt`: Work Cloud browser runs on a separate cloud machine, not automatically the user's personal Windows.
- `https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt`: standard GitHub connector's read-oriented documented behavior; historical successfully used GitHub tools in this conversation remain real but do not imply permission for the previously blocked job write.

**Decision:** Stop requesting new Windows unit runs or restarting the listener solely to repeat the blocked chat-side dispatch. Preserve v1 as a bounded research prototype. For immediate practical local automation, discuss the officially supported Work Local / Codex Local pathways if the user decides to accept them; otherwise retain the validated manual v0 and request a supported, authorized write-capable connector path rather than bypassing the block. No new job, service, public main merge, or scientific repo changes are authorized by this decision.

## 2026-10-30 — Research: Plus/Pro Chat-only bridge without API billing

The user explicitly reaffirmed that **regular ChatGPT Chat must be the primary interface** because they want to stay within their Plus/Pro subscription and avoid separately charged API inference, and requested a broad investigation of solutions and alternatives.

**Current official documentation checked (live sources linked in the research memo):** personal Free/Go/Plus/Pro accounts can no longer create new custom GPTs, and existing GPTs are scheduled to retire on Dec 11, 2026; legacy GPT Actions therefore are not a sustainable fresh build. Custom write-capable remote MCP connections are documented primarily for Business/Enterprise/Edu, not verified for personal Plus/Pro. Desktop-only local MCP plugin submissions require approved partners and local execution; **ordinary Chat mode local MCP invocation remains unverified**. ChatGPT built-in-browser WebMCP site tools require Work or Codex conversations. Sign in with ChatGPT permits eligible partner apps to consume included Work/Codex usage in place of separately keyed API calls but does not preserve the normal Chat UI. The OpenAI API is separately billed outside Plus, and EU terms restrict automated/programmatic extraction of ChatGPT output. Free external hosting (such as Cloudflare Workers Free's 100k requests/day) does not grant native Chat write permissions.

**Public development branch research artifact:** `docs/CHAT_ONLY_OPTIONS_2026-10-30.md` on `feat/v1-bounded-listener`, created commit `5e9ff4385871c5a34092249de90e3be6e6fdb4b5`. Includes option matrix, subscription implications, permissions, and decision gates. No code or new live task was deployed.

**Conclusion:** no documented and independently verified **zero-touch** personal Plus/Pro **Chat** → arbitrary local Windows execution channel exists within current permissions. Historical v0 Chat→GitHub→Windows success remains real; v1 write block remains unexplained and cannot be circumvented by changing transport. The strongest immediately plausible **no extra API cost** fallback is **explicit user-mediated job handoff** from Chat (copy control or explicitly downloaded job file) to a narrowly allowlisted Windows intake worker with local confirmation and return receipts. This is a design proposal, NOT implemented or tested and NOT fully automatic. A one-click local deep-link handoff is speculative and must be vetted for supported URL behavior and local CSRF security. Browser DOM scraping to auto-extract model output is not recommended because OpenAI EU terms prohibit automatic/programmatic output extraction and circumventing safety measures.

**Next user decision (only one essential point):** is **one explicit approval/click per job** acceptable, or must transfer be **fully zero-touch**? If one click acceptable, user may authorize design/implementation on a separate feature branch (without service or general shell). If zero-touch is mandatory, pause implementation pending authorized native plugin/write capability and account-specific eligibility. Do not offer Work/Codex or billable API as if they satisfy the user's explicit constraint.

## New-chat recovery prompt

Continue the GPT Chat Local Bridge pilot from the current GitHub state. Open the public repository GalexY3/gpt-chat-local-bridge and read CONTINUITY.md, docs/PILOT_PROTOCOL.md, and current feature-branch code. Check both repository branch HEADs and access to the private repository GalexY3/gpt-chat-local-bridge-control. Follow the next action documented here. Report actual changes and tests separately from plans, preserve the safety boundaries and do not claim Windows execution without evidence. Keep this continuity document current after each significant project exchange so the next chat can resume without prior conversation history.
