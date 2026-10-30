# Windows pilot: prerequisites (no installation yet)

This page covers **only diagnostics**, not granting remote control or installing an executor.

## Existing tools

The pilot targets Windows PowerShell. We use the Python launcher `py.exe`, rather than assuming the `python.exe` in `WindowsApps` is a functional interpreter.

From an **ordinary PowerShell window, without administrator elevation**, run:

```powershell
py -0p
py -3 --version
gh auth status
uv --version
```

- `py -0p`: enumerates Python interpreters known to the launcher.
- `py -3 --version`: confirms a real Python 3 interpreter.
- `gh auth status`: confirms whether GitHub CLI has been authenticated. Share account/status only; **never share tokens, credential files, or the output of `gh auth token`.**
- `uv --version`: verifies the package/environment manager (not required for the first protocol tests).

If GitHub CLI needs authentication, run `gh auth login` locally. Choose GitHub.com, HTTPS and browser login. Do not paste authentication codes into chat.

## Offline protocol test

Once the public source repository is cloned:

```powershell
cd <your-cloned-gpt-chat-local-bridge-directory>
py -3 -m unittest discover -s tests -v
```

These protocol tests validate job envelopes without connecting to GitHub, writing in personal directories or executing external programs.

## Next gate

The worker implementation has **not** been installed or connected. First confirm the Python and GitHub CLI diagnostics; then implement a strict, one-operation, one-shot worker for the private control repository.

Do not paste personal paths, API keys or access tokens into public GitHub issues.
