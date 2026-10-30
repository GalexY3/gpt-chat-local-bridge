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
- Public feature branch feat/pilot-schema-v0 includes bridge_protocol.py, tests/test_bridge_protocol.py and docs/WINDOWS_PREREQUISITES.md. Latest known feature commit: d501807a01707fba562f4293df4c52e1a15aa4d3. Verify live branch HEAD before editing.

The protocol validator has been written but its tests have not yet been executed by the user. No Windows worker or GUI automation has been installed or tested.

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

Run the existing offline protocol tests on the user's Windows machine:

```powershell
cd $HOME
git clone https://github.com/GalexY3/gpt-chat-local-bridge.git
cd gpt-chat-local-bridge
git switch feat/pilot-schema-v0
py -3 -m unittest discover -s tests -v
```

If the target folder already exists, inspect it and fetch instead of recloning. Report the test output. After tests pass, review the validator and build a restricted one-shot worker; only later attempt the first end-to-end dispatch from Chat.

## New-chat recovery prompt

Continue the GPT Chat Local Bridge pilot from the current GitHub state. Open the public repository GalexY3/gpt-chat-local-bridge and read CONTINUITY.md, docs/PILOT_PROTOCOL.md, and current feature-branch code. Check both repository branch HEADs and access to the private repository GalexY3/gpt-chat-local-bridge-control. Follow the next action documented here. Report actual changes and tests separately from plans, preserve the safety boundaries and do not claim Windows execution without evidence. Keep this continuity document current after each significant project exchange so the next chat can resume without prior conversation history.
