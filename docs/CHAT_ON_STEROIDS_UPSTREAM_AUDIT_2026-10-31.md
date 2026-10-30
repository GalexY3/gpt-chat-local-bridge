# Independent source audit: Chat On Steroids upstream (2026-10-31)

**Status:** documentary / selected-source review, NOT full line-by-line security audit. No binaries downloaded or executed. No service, tunnel, browser extension, account plugin or local PC action enabled. This supersedes the earlier assessment based on an obsolete fork.

## Critical repository identity correction

The earlier reference `frstich/chat-on-gptmcptodesk` is a **fork** of `totec448-spec/chat-on-steroids`, created August 26, 2026 and last updated then. The real upstream project is:
- https://github.com/totec448-spec/chat-on-steroids
- Live GitHub API metadata observed Oct 31: created 2026-08-22, pushed 2026-10-30, approximately 5,113 stars and 665 forks, MIT licensed, ongoing issues and 37 open issues.
- Main HEAD observed: `7406be73f48b0e60d6bf9afff9d8ca8b565bf992`.
- Latest GitHub release verified by API: `v2.1.48`, published 2026-10-30 08:39:39 UTC, Windows x64 installer `Chat-On-Steroids-Setup-x64.exe` approximately 178 MB and `SHA256SUMS.txt` checksum release artifact; Electron app package `2.1.48`.
- The obsolete fork's `package.json` reports `2.0.1`. All conclusions derived solely from its SECURITY.md/README are superseded by the current upstream docs.

## Architecture verified in current upstream source

1. **Three MCP connectors**: Core (read, search, patch, save generated image, shell, interactive stdin, task plans, agents, JS exec), Desktop (browser tab DOM/screenshot/network/console/actions and native OS window/input/clipboard), Plugins (installed external MCP tools). Source: `docs/tool-surface.md`, `src/main/mcp/surfaces.ts`.
2. **ChatGPT Chat remains the primary LLM and browser conversation**. The app's companion Chrome extension manages chat capture, message delivery, identity and multiagent tabs; source: `README.md`, `docs/setup.md`, `extension/manifest.json`. No alternative paid inference API required for the main chat, but all subscription limits still apply.
3. **Goal/Loop can use ChatGPT itself** through helper ChatGPT browser chats (default in current code), a configured OpenRouter/API model, or a custom local OpenAI-compatible endpoint (including `http://localhost:11434/v1` for Ollama). Source: `src/main/goal.ts` (notably `goalBackendFor`, `requestBrowserDecision`, `resolveGoalBaseUrl`, `goalProviderKey`). The old fork's claim that OpenRouter was mandatory is OUTDATED.
4. A local optional **control API** is off by default. When activated it is loopback-only, authenticated using a per-launch bearer token stored in the app user-data folder, rejects Origin headers, and has a separate OFF-by-default action switch for posting messages. Source: `src/main/control-api.ts`, `docs/setup.md`, `SECURITY.md`. This is not an authorized ChatGPT remote connector.
5. MCP tools have resource bounds. Current `exec` is bounded JavaScript in an isolated QuickJS worker (64k source chars, 2s CPU, 60s wall, 32 tool calls) and dispatches only that connector's enabled tools. It is NOT a filesystem/OS sandbox: a dispatched `exec_command` can still have its normal user-level effects and errors do not roll them back. Source: `src/main/mcp/code-mode-runtime.ts`, `docs/tool-surface.md`.
6. The app supports command Allowlist/Denylist policies with fail-closed unsupported syntax, but they are off by default and cannot sandbox a permitted process or its children/interactive input. File access paths are checked against approved roots; terminal commands and desktop actions are outside filesystem-root confinement. Source: `SECURITY.md`, `docs/tool-surface.md`, `src/main/exec.ts`.
7. Current `extension/manifest.json` includes `debugger`, `tabs`, `tabGroups`, `scripting`, optional `cookies`, and HTTP/HTTPS host permissions beyond ChatGPT. This is a broad browser capability, though the script injection matches specifically ChatGPT pages; broad host permission alone is not evidence of abuse.
8. Conversation/tool history is always recorded in current build and is **not encrypted by Electron safeStorage**; saved credentials use OS secure storage. The optional Google sign-in flow can transfer ChatGPT session-token cookies via an explicit temporary user-initiated process. Source: current `SECURITY.md`.
9. Release installers are **unsigned** and new installs enable Core and Windows Desktop permissions. Check release SHA-256 before installation, but same-publisher GitHub checksum is not a substitute for independently authenticated publisher signing or malware analysis. CI builds are Windows-native and test verification exists; this review did not independently run them.
10. Historical `docs/public-history-privacy-incident-2026-08-24.md` documents a git-history leak of maintainer email and Claude session URLs; project claims later cleanup and privacy checks, not a leaked live API token. Do not portray it as malware or live credential compromise. The project is solo-maintained beta; no independent security audit verified.

## Key Plus/Pro eligibility finding: real user report contradicts general plan docs

- OpenAI's official current custom MCP help page still says full custom MCP writes are available primarily in Business/Enterprise/Edu, and Pro custom MCP read/fetch only: https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- However, upstream issue **#522** includes an explicit 2026-09-27 report from collaborator `Haz4rdovisk` of a FRESH personal **ChatGPT Plus account** completing full CoS setup through `Plugins → Add → Create MCP App`, then creating/reading/editing a text file and opening Windows Task Manager using Desktop tools. Another collaborator accepted this as a confirmed Plus live test. URL: https://github.com/totec448-spec/chat-on-steroids/issues/522
- Upstream issue **#1550** includes an Oct 20 user report of creating Core and Desktop Plus-account plugin connections with a Cloudflare Quick Tunnel, after named-tunnel trouble: https://github.com/totec448-spec/chat-on-steroids/issues/1550 . Subsequent app-creation reliability remained account/setup dependent.
- These are **developer/user reports**, not independent proof for this particular account, and do not override safety blocks. A Pro custom-write E2E report was not confirmed within issue #522. Distinguish absence of the old Developer Mode setting from the current `Plugins → Add → Add custom MCP server` UI.
- The user's connected GitHub app had `Allow all actions` but a prior private job dispatch was specifically blocked. Neither broad local permission nor a successful Plus anecdote authorizes replaying the earlier blocked action through CoS.

## Costs and transports

- CoS main ChatGPT conversation and optional ChatGPT Goal helper utilize included account messages/quotas, not externally metered OpenAI inference calls.
- OpenAI Secure MCP Tunnel uses a **restricted Platform API key with Tunnels Read/Use**; this credential is for transport, not equivalent to using a paid GPT inference endpoint. Official guide https://developers.openai.com/api/docs/guides/secure-mcp-tunnels describes limits/roles but this review did NOT independently verify all account-specific charges or restrictions.
- Cloudflare Quick Tunnel is another supported project transport but has a public changing hostname and secret URL path, and introduces separate exposure/availability assumptions. Do not treat it as a workaround for host-denied tool permission.
- The local OpenRouter Goal backend may incur independent API fees. Current ChatGPT-helper default avoids it, and Ollama custom endpoint is an option if the local model is suitable. No claim that the multi-chat workflow is unlimited: account usage limits, context and provider policies remain.
- A fresh Chrome extension install grants browser debugger/tabs and broad HTTP(S) host permissions, and a local app with file/shell/desktop rights is high trust. Test only in a disposable non-sensitive environment initially.

## Safety-ranked recommendation

**Assessment: HIGH functional alignment but MATERIAL account-eligibility and PC security uncertainties.** Stronger candidate for the user than rebuilding a complete local desktop harness from scratch, given its active upstream and built-in ChatGPT helper/worker features.

**First action, NO installation:** The user can open `https://chatgpt.com/plugins`, choose Add, and CHECK whether `Add custom MCP server` (or `Create MCP App`) is available. Do not create yet. This tests the earliest eligibility gate without installing unsigned software or exposing PC.

If offered, next step after specific consent: create an isolated Windows user/project or VM, verify exact `v2.1.48` release checksum and source, install ONLY into the disposable environment, immediately disable Desktop/input/commands/third-party plugins/multi-agent until needed, set a small approved root, do not paste tokens into chat; connect ONLY Core via an officially permitted tunnel; use a read-only test first and then a single harmless file-write test with explicit consent. Keep no auto-start and no privileged run. Do not use browser automation to circumvent any denial.

Later, after review, expand capability by capability (file patches/test commands, GUI browser, native desktop), with a visible kill switch and per-session bounded authority. A single blanket grant of unrestricted full-PC privileges should not be the initial configuration.

**Gates that remain UNVERIFIED:** The user's personal ChatGPT Plus/Pro account entitlement for custom write tools; Secure MCP Tunnel account-organization association, pricing, permissions; actual CoS behavior on the user's Windows machine; release binary integrity beyond upstream-provided checksums; long-run stability and safety of the browser extension.

**No operational effects:** this audit did not install or run CoS, touch the private control queue, change account permissions, merge to main, or change AB/other research repos.
