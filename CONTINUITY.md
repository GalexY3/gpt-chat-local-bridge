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

**Windows testing observed through user-provided PowerShell transcripts:** initial 11 protocol tests passed (11/11, 0.004 s); subsequently the user pulled the one-shot worker and reports **20/20 tests PASS, 0.052 s** with Python 3.14.3. `git pull --ff-only` fast-forwarded the feature branch from d501807 to b144727. Their `git status --short` showed only untracked Python cache directories (`__pycache__/`, `tests/__pycache__/`). This is a **user-reported Windows execution**, not code remotely executed by this assistant. After that report, `.gitignore` was added on the feature branch to ignore those caches, commit bbc9ca5fb1fee0271d1f2796afd8f6dd4831df34. **No worker workspace initialization, no private queue dispatch, no remote receipt and no Chat → PC → Chat end-to-end test has occurred.**

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

## Latest conversational checkpoint (2026-10-30)

User pasted a PowerShell log showing `git pull` to feature HEAD `b144727` and the same 20/20 offline tests passing in 0.052 s. **No invocation or output of `py -3 bridge_worker.py --init` appears in this log.** Therefore local workspace initialization remains UNVERIFIED and no GitHub job has been queued or executed. The next reply should ask only for `git pull --ff-only` to retrieve `.gitignore` at later commit `bbc9ca5`, then `py -3 bridge_worker.py --init` (in the existing project directory). Treat any failure non-destructively and inspect before proceeding. Do not claim a new test run beyond user-shared output.

## Next action

The user already cloned the public repo in their Windows home folder and is on `feat/pilot-schema-v0`. **Do not clone again.** As of this checkpoint **20/20 offline tests have been user-reported as passing.** Now update the feature branch to collect the harmless Python cache ignore and **explicitly initialize the isolated workspace**:

```powershell
cd $HOME\gpt-chat-local-bridge
git pull --ff-only
py -3 bridge_worker.py --init
```

The expected stdout on successful initialization is `pilot_workspace_initialized`. The command creates exactly one dedicated `gpt-chat-local-bridge-pilot` folder under the Windows home with a marker and state subfolder. It performs no network requests or remote jobs. If it reports `workspace_already_exists` or another error, do not delete or overwrite anything; inspect the state first. The worker is **one-shot only**, never a background service.

**After user reports local initialization success:** Chat should generate a fresh safe job ID and expiry strictly within the next 15 min, create a v0 JSON job at `jobs/pending/<id>.json` in the PRIVATE control repo using the GitHub connector; verify exact JSON and confirm it is still within TTL. Only then ask the user to run `py -3 bridge_worker.py --run-id <id>` from the project checkout while job is valid. The worker creates a fixed benign file and posts a minimal receipt; Chat must independently fetch and inspect `jobs/receipts/<id>.json` and compare the SHA-256 with known bytes. Do not claim success merely from a queued task or stdout. Do not write any job until local initialization is user-confirmed, and never disclose GitHub credentials.

## New-chat recovery prompt

Continue the GPT Chat Local Bridge pilot from the current GitHub state. Open the public repository GalexY3/gpt-chat-local-bridge and read CONTINUITY.md, docs/PILOT_PROTOCOL.md, and current feature-branch code. Check both repository branch HEADs and access to the private repository GalexY3/gpt-chat-local-bridge-control. Follow the next action documented here. Report actual changes and tests separately from plans, preserve the safety boundaries and do not claim Windows execution without evidence. Keep this continuity document current after each significant project exchange so the next chat can resume without prior conversation history.
