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
- Public feature branch feat/pilot-schema-v0 includes bridge_protocol.py, tests/test_bridge_protocol.py and docs/WINDOWS_PREREQUISITES.md. Feature branch HEAD observed 2026-10-30: b144727fe02ff6de9951d5df8ec14037c2dc04a6. Verify live HEAD before editing.

The user reports cloning the public repository, switching to the feature branch and running the original 11 protocol tests with Python 3.14.3: **11/11 PASS, 0.004 s** (PowerShell transcript provided in the conversation). This is a user-observed Windows result, not an execution performed by the ChatGPT tool. Subsequently, the assistant added `bridge_worker.py` (opt-in, one-shot fixed-file worker), `tests/test_bridge_worker.py` (nine more offline tests) and `docs/WORKER_V0.md` to the same feature branch, latest HEAD above. **The new worker and its nine tests have not yet been run on Windows or independently verified. No job has been dispatched, no worker installed or started, and no actual Chat → PC → Chat execution has occurred.**

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

## Next action

The user already cloned the public repo in their Windows home folder and is on `feat/pilot-schema-v0`. **Do not clone again.** First inspect the current local checkout and update the feature branch, then execute the expanded offline test suite:

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git pull --ff-only
py -3 -m unittest discover -s tests -v
```

Expected test discovery is 20 methods (11 original + 9 new). **Do not report PASS until user returns actual output.** If `git status --short` shows local changes, stop and inspect before pulling. If tests pass and the user approves the next gate, initialize the fixed disposable workspace with `py -3 bridge_worker.py --init`. That command creates one dedicated folder locally and contacts no network endpoint. Only **after** test review and local initialization should Chat enqueue a fresh, 15-minute, explicitly authorized fixed-file job in the private control repository, followed by the user's one-shot `py -3 bridge_worker.py --run-id JOB_ID`. The v0 worker is manual, not a background agent, and only uploads a receipt after completing its predefined operation.

## New-chat recovery prompt

Continue the GPT Chat Local Bridge pilot from the current GitHub state. Open the public repository GalexY3/gpt-chat-local-bridge and read CONTINUITY.md, docs/PILOT_PROTOCOL.md, and current feature-branch code. Check both repository branch HEADs and access to the private repository GalexY3/gpt-chat-local-bridge-control. Follow the next action documented here. Report actual changes and tests separately from plans, preserve the safety boundaries and do not claim Windows execution without evidence. Keep this continuity document current after each significant project exchange so the next chat can resume without prior conversation history.
