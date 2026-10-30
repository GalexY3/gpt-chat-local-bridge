# Audit of Chat-only Windows bridge alternatives (2026-10-31)

**User requirements:** ordinary ChatGPT Chat as the primary reasoning/UI surface; Plus or Pro subscription, no separately metered LLM API; one local setup/session grant rather than per-job copy/approve; multiple PC actions with logs and revocation. No Work/Codex as the permanent interaction surface. **Research only**: no third-party installation, paid resource, new private job, queue retry, or OS process started.

## Evidence and project baseline

- Previously verified manual v0 Chat → private GitHub queue → Windows worker → GitHub receipt with user physical file hash.
- Bounded v1 listener started and user saw `listener_ready`, but the chat-side new private GitHub write was blocked by host safety controls; both proposed job and receipt missing. It was stopped.
- Windows test transcript reports 65/65 passing offline tests (0.147 sec). Does **not** verify v1 live dispatch.
- Existing GitHub plugin account-specific setting **Allow all actions** did not override the blocked queue write. Do not attempt another connector or disguised job merely to evade it.

## Ranked findings

### 1. Official Sites-hosted MCP plugin — strongest genuine Chat+Plus/Pro research path

- Source: https://help.openai.com/en/articles/20001547-hosting-a-plugin-with-chatgpt-sites
- Source: https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites
- Source: https://learn.chatgpt.com/docs/sites
- Source: https://learn.chatgpt.com/docs/sites/data-and-connections
- Sites is available to Plus and Pro. Hosting is **currently included** under account usage limits. Creating/editing a Site consumes **Codex** allowance; ordinary Chat can subsequently invoke the Site-hosted plugin.
- Official docs explicitly allow MCP tools with read/write behavior and installing/mentioning the resulting plugin in ChatGPT Chat, subject to tool and account permissions. This is a **distinct path** from adding an arbitrary direct custom MCP server, for which full writes are documented primarily for Business/Enterprise/Edu.
- Sites supports D1 persisted relational storage, R2 objects, HTTP/HTTPS and WebSockets, hosted environment variables/secrets, and authenticated identity from ChatGPT sign-in. This makes a small server-side queue plausible in principle.
- **NOT VERIFIED:** a personal Plus/Pro account's exact permission for a custom Site-hosted *write* tool; how an independently running Windows worker could authenticate to a private Site backend endpoint; whether the site runtime allows the required server-to-worker or worker-poll communication, and whether the product will allow this particular type of local-computer operation. Hosting included does not mean unlimited requests, storage, or subscription usage.
- Site-to-private-service **OpenAI tunnel** is separately documented as rolling out only to eligible Enterprise Sites: https://help.openai.com/en/articles/20001606-connecting-chatgpt-sites-to-private-services-with-tunnels . Do not plan to rely on it for personal Plus/Pro.
- Proposed **non-executable feasibility proof**: create an owner-only private Site with D1-backed `ping`/ `enqueue_demo_record` and `read_demo_record` MCP tools that change only a synthetic record in the Site's own database. Invoke the plugin from ordinary Chat, independently check persisted record, usage meters and action approval behavior. Do **not** connect Windows or GitHub at this stage. If the tool is unsupported/blocked, stop, don't retry through a disguised path.
- Only if authorized and passed: design a separate authenticated worker read/status endpoint (if genuinely supported), then bounded local session tasks with allowance profiles, signatures, expiry, audit/kill switch; keep general shell/desktop privileges separate from the benign proof.

### 2. Chat On Steroids (frstich/chat-on-gptmcptodesk) — closest existing Windows capability, hard plan gate

- Source: https://github.com/frstich/chat-on-gptmcptodesk
- Security: https://github.com/frstich/chat-on-gptmcptodesk/blob/main/SECURITY.md
- Code is MIT licensed; solo-maintained, unsigned beta with Windows installers and SHA256SUMS. Has Electron local app, PowerShell/cmd terminal, file patches/search, UI screenshots/mouse/keyboard/clipboard, session history, multi-chat workers, extension, tunnel integration and permission switches. Its optional autonomous goal loop requires an **OpenRouter API key**, so that feature is not included solely in Plus/Pro.
- Its documented *official MCP* setup requires ChatGPT Developer mode and a custom **write-capable** MCP app; the project's own README says full custom MCP is Business/Enterprise/Edu, Pro only read/fetch, so the official normal personal Chat configuration does **not** solve the user's key gate.
- **Critical security findings from author's own disclosure:** new installs enable all capabilities (read-only OFF), including arbitrary commands and desktop control; command execution is not contained within approved roots, desktop control is not folder-limited, and process runs with normal Windows user privileges; installer unsigned; no OS sandbox; session recordings not encrypted by safeStorage. Don't install/enable on a personal production profile without explicit review, backups, permission hardening and a non-sensitive disposable test account.
- Extension browser session manipulation is separate from official MCP and is explicitly experimental/unofficial, potentially subject to terms on automated Chat extraction.
- Recommendation: **do not install now**. Reuse only design ideas (scoped tool contracts, revocation, receipts, session continuity) after reviewing source/license and account eligibility.

### 3. ChatCMD (int04/ChatCmd) — rich open-source runtime, blocked by Chat MCP gate

- Source: https://github.com/int04/ChatCmd
- ChatGPT guide: https://github.com/int04/ChatCmd/blob/main/docs/PLUGIN_SETUP.md
- Extension: https://github.com/int04/ChatCmd/blob/main/chatgpt-extension/README.md
- MIT-licensed Rust MCP server, React console, SQLite task store, scoped access profiles, interactive terminals/files/Git/process, per-task approvals and companion optional Chromium extension. No ChatCMD-hosted subscription/API charge by default. Windows source build requires recent Rust, Node.js, Visual Studio MSVC tools and Git.
- The official ChatGPT flow uses a remote reachable HTTPS tunnel, a custom MCP plugin, and developer-mode eligibility. The optional extension uses **ChatGPT DOM automation**, is unofficial and does not itself establish an authorized Chat-only write permission. UI changes may break selectors. Public tokenized URLs and SQLite recoverable plugin links require careful secret management.
- Recommendation: useful runtime/reference or future backend to reuse **after** an official plugin channel exists. Not a turnkey Plus/Pro Chat fix.

### 4. Dworrall21/chatgpt-bridge — opposite dataflow

- Source: https://github.com/Dworrall21/chatgpt-bridge
- Chrome extension + localhost Python HTTP/WS gateway, primarily **local agents send prompts to the signed-in ChatGPT browser** without a model API key. This is the reverse of ChatGPT Chat issuing authenticated commands to Windows. Requires extension, browser profile and DOM interaction; no proof of reliable normal-Chat actions for the desired direction.
- Recommendation: not a base for our bridge; at most reference for a browser gateway, with contractual and maintenance concerns.

### 5. Tzufucius/web-llm-bridge — opposite dataflow, alpha, copyleft

- Source: https://github.com/Tzufucius/web-llm-bridge
- Python CLI/broker + Chrome/Edge extension; local agent invokes ChatGPT Web, extracts replies and session state. The project labels ChatGPT provider alpha and says DOM changes can break it. License AGPL-3.0-only, which has important redistribution/network-use implications if code is incorporated.
- Recommendation: do not adopt as a Chat → Windows worker; objective is reversed and there are terms risks.

### 6. Other OpenAI features are not equivalent

- Direct custom full write-enabled MCP server: current official documentation limits full MCP beta to Business, Enterprise, Edu; personal Pro read/fetch only. https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt
- Desktop-only local MCP plugin: only for locally executing ChatGPT desktop threads, published after partner approval; does not prove ordinary Chat usage. https://developers.openai.com/plugins/deploy/desktop-only
- ChatGPT built-in browser / browser site tools: documented for Work/Codex, not an ordinary Chat native arbitrary-local-exec channel. https://help.openai.com/en/articles/20001277-using-the-built-in-browser-in-the-chatgpt-desktop-app
- Secure MCP Tunnel is a transport feature, not a grant of custom MCP write capabilities; access controlled by workspace/organization. https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
- Third-party browser DOM automation of ChatGPT conversations raises compatibility and contractual uncertainty: EU terms restrict automatically/programmatically extracting output and bypassing platform protections. https://openai.com/es-ES/policies/eu-terms-of-use/

## Comparison (qualitative rather than unsupported numeric scores)

| Approach | Chat normal | Plus/Pro viability | No extra model API | Multi-action PC control | Crucial blocker |
| --- | --- | --- | --- | --- | --- |
| Official Sites MCP plugin + bounded Windows worker | Official Chat plugin supported | **Promising, account-specific write eligibility untested** | Yes for Chat; Sites hosted under plan limits | Possible after independent secure backend/device transport design | Verify MCP write + Site/backend external access |
| Chat On Steroids official MCP | Yes where custom app allowed | **No confirmed full-write entitlement in personal Plus/Pro** | Basic operations yes; Goal loop OpenRouter separate | Yes, comprehensive | Plan gate; very broad default permissions |
| ChatCMD official MCP | Yes where custom app allowed | Same eligibility gate | Yes for core, no vendor hosted inference | Yes with approvals | Plan and tunnel |
| ChatCMD browser extension alone | ChatGPT web tab, unofficial | Technically plausible DOM workflow | No separate model API | Depends on bridge mode | Terms, reliability, security |
| chatgpt-bridge | ChatGPT consumed by local agent | Browser based | No separate model API | Not its primary direction | Reverse-direction architecture |
| web-llm-bridge | ChatGPT consumed by local agent | Browser based | No separate model API | Not its primary direction | Reverse direction, alpha, AGPL |
| Existing private GitHub queue | Yes | **V0 once succeeded; v1 write explicitly blocked** | Yes | v1 worker technically could, if authorized | Host denied particular action |

## Proposed decision and gates

1. **First**, check account eligibility for Sites and a hosted **mock MCP tool** invoked from an ordinary Chat turn. Public official documentation supports this as an intended workflow. Setup uses Work/Codex for building only, **not** as ongoing reasoning UI.
2. If allowed and no surprising cost, test a fake in-Site queue with a single synthetic record; do not connect PC or existing GitHub private queue.
3. Independently validate a locally authenticated transport (Site HTTP endpoint with machine credentials and nonce/session binding, if runtime and visibility settings allow it). No broad public unauthenticated queue, no personal tokens in prompts. Use least privilege and a kill switch.
4. Add capabilities gradually: first read-only project files and fixed test operations, then project-scoped file edit/test commands, then separately review any GUI/terminal unrestricted feature. User wants one session grant without prompts per task, not repeated blanket authorizations, but highly consequential effects must remain guarded.
5. If the hosted Sites write tool is itself blocked, **stop there**. Do not repurpose other plugins, fake benign metadata or shift the same executable job to a less supervised transport just to bypass a host safety refusal.

**This audit is documentary:** no downloads, code security review beyond docs, independent security audit, Windows compatibility trial or full Chat Sites plugin execution has been performed. Do not claim installability until test results exist.
