# Project continuity

Updated: 2026-10-30. This document is the public, persistent project handoff.

## Purpose

Build an experimental bridge from ordinary ChatGPT Chat to a user-installed Windows worker. GitHub is the message transport. A connected GitHub repository does not give ChatGPT direct access to local applications or files. The worker is not installed yet. The project aims to support scientific workflows across independent projects, without changing their repositories during the pilot.

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

**Next action:** Review the proposed bounded-listener design in `docs/ADR-0001-BOUNDED_LISTENER.md` on feature branch, and—if the user wishes to continue—implement it on a feature branch, with offline unit tests and no live unattended execution before the user has reviewed the updated protocol and tests. Address the present v0 limitation that a second job cannot reuse the one existing fixed output. Update and run tests on Windows before any new private dispatch. Do not automatically merge to `main`. The user has not yet explicitly approved a continuously running service or generalized execution on their PC.

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

## New-chat recovery prompt

Continue the GPT Chat Local Bridge pilot from the current GitHub state. Open the public repository GalexY3/gpt-chat-local-bridge and read CONTINUITY.md, docs/PILOT_PROTOCOL.md, and current feature-branch code. Check both repository branch HEADs and access to the private repository GalexY3/gpt-chat-local-bridge-control. Follow the next action documented here. Report actual changes and tests separately from plans, preserve the safety boundaries and do not claim Windows execution without evidence. Keep this continuity document current after each significant project exchange so the next chat can resume without prior conversation history.
