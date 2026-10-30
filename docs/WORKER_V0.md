# Windows one-shot pilot worker

**Experimental, not a service.** It does nothing in the background. It never
accepts arbitrary shell commands, custom output paths, GUI actions or packages
from a remote job.

Prerequisites: a Python 3.13+ interpreter via `py`, GitHub CLI `gh` logged in,
and access to the **private** control repository. No pip packages required.

## Update the public checkout

Run in normal PowerShell, not as Administrator:

```powershell
cd $HOME\gpt-chat-local-bridge
git status --short
git pull --ff-only
py -3 -m unittest discover -s tests -v
```

The code lives on the feature branch `feat/pilot-schema-v0`. Do not run the
one-shot worker if the tests fail or the checkout has unexpected changes.

## Initialize only the disposable pilot workspace

```powershell
py -3 bridge_worker.py --init
```

This creates a **new** dedicated `gpt-chat-local-bridge-pilot` folder under
your Windows profile with a fixed marker and state directory. It refuses an
existing folder, rather than silently reusing arbitrary content. It does not
contact GitHub or perform any queued operation.

**Stop here until Chat explicitly enqueues a fresh short-lived test job** in
the private repository, after checking that the worker code has passed tests.

## First real task (later; only after Chat confirms the task ID)

```powershell
py -3 bridge_worker.py --run-id <FRESH_JOB_ID_FROM_CHAT>
```

One selected job is fetched using authenticated `gh api`, strictly validated,
and used to create a single fixed text file in the pilot workspace. The worker
attempts to upload a minimal SHA-256 receipt into the private control repo.
On any local reservation or upload error, it does **not** retry side effects:
report the error and inspect the workspace/state before further action.

Once this round trip has been observed, a later phase may add explicit user
opt-in background polling. V0 does **not** run persistently.
