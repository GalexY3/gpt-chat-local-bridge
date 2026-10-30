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

## Latest conversational checkpoint (2026-10-30, Europe/Madrid)

**Local initialization is user-reported complete.** The user's latest PowerShell transcript shows `git pull --ff-only` fast-forward to feature commit `bbc9ca5fb1fee0271d1f2796afd8f6dd4831df34` (adds Python-cache `.gitignore`), followed by `py -3 bridge_worker.py --init` with exact stdout `pilot_workspace_initialized`. Earlier 20/20 offline tests passed, 0.052 s. These are user-shared PowerShell outputs, not local execution by ChatGPT.

**First real remote job QUEUED (not executed or completed).** Verified via connected GitHub read-back in the PRIVATE control repo: `jobs/pending/pilot-20261030-2209.json`, commit `80e821c1e27d629f66a38eac952f60e89f4209e5`, file SHA `66b2500fa006dc858c08e58343f0213dabe0273e`. Fields: `schema_version=0`, `job_id=pilot-20261030-2209`, `operation=write_fixed_test_file`, `workspace_profile=isolated-pilot`, `parameters={}`, `expires_at=2026-10-30T21:22:00Z` (22:22 Europe/Madrid). Job was created only after user confirmed local initialization. **No Windows execution or receipt has yet been observed.**

## Next action

The user was instructed to run the following in their already-initialized checkout **before 2026-10-30 22:22 Europe/Madrid**:

```powershell
py -3 bridge_worker.py --run-id pilot-20261030-2209
```

Do not enqueue another task while the first remains eligible. When the user returns output, check whether `jobs/receipts/pilot-20261030-2209.json` exists in the **private** repo, inspect status/job SHA/output SHA, and compare against the SHA-256 of exact bytes `b"GPT Chat Local Bridge pilot v0\\n"`. Distinguish receipt existence from local stdout, and check that the local fixed file exists if needed. If the job expired or there is an error, inspect first and do not blindly retry: the worker's durable reservation and fixed file can block repeat execution, intentionally. If no execution occurred before expiry, a new ID and expiry may be needed after inspection. This is still a manual one-shot pilot, not autonomous background control. Update this file before concluding the next substantive project turn.

## New-chat recovery prompt

Continue the GPT Chat Local Bridge pilot from the current GitHub state. Open the public repository GalexY3/gpt-chat-local-bridge and read CONTINUITY.md, docs/PILOT_PROTOCOL.md, and current feature-branch code. Check both repository branch HEADs and access to the private repository GalexY3/gpt-chat-local-bridge-control. Follow the next action documented here. Report actual changes and tests separately from plans, preserve the safety boundaries and do not claim Windows execution without evidence. Keep this continuity document current after each significant project exchange so the next chat can resume without prior conversation history.
