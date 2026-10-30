# ADR-0003 — One-time local authorization for an autonomous session

**Status:** PROPOSED architecture only. **Date:** 2026-10-30. Not implemented; no persistent service; no live queue dispatch or expanded operating-system permissions authorized.

## User objective

The user prefers to use **ordinary ChatGPT Chat** as the central LLM and interface under an existing Plus or Pro subscription (no separate per-token API billing), authorize the connection to the Windows PC **once**, and permit subsequent computer operations without per-job confirmation.

Distinguish:
- **One-time installation and pairing:** device establishes trust, keys and policy once.
- **One-time per-session authorization:** local user intentionally opens a bounded session and selects capabilities; work within the approved scope can proceed without repeated local prompts.
- **Unrestricted indefinite control:** an unbounded, permanent agent capable of arbitrary changes and actions, including privileged/sensitive operations. **Not recommended** as an initial mode and not implied by the user's approval of a pilot.

No OS permission setting can override ChatGPT connector host restrictions. The connected GitHub app was independently inspected on 2026-10-30: global default **Allow low-risk actions**, app-specific setting **Allow all actions**, yet a later write to the private job queue was blocked by host connection safety controls. Therefore changing app approval level is not a demonstrated fix.

## Proposed local architecture after a supported transport exists

1. **Pairing (once, user-initiated):** a local Windows application generates a device key pair and establishes an approved connection with a *supported* ChatGPT plugin or other officially authorized tool action. Keep private keys in OS-protected storage; no pasted PATs or exposed desktop HTTP server. A direct authorized action path must be demonstrated before proceeding.
2. **Session grant (once per session):** choose a bounded duration (for example 30–60 minutes), a workspace/project directory, allowable capabilities, maximum number of tasks and CPU/disk/network budgets. Present the resulting policy on-screen and obtain one local confirmation.
3. **Multiple low-risk actions without further local prompts:** the agent may inspect and edit files within the granted project scope, run preapproved test/build commands in isolated working folders, and generate receipts. Sequence events by job ID, bind to session ID, authenticate each request, and reject replay, expiry and out-of-scope actions.
4. **High-risk operations are an explicit exception**: credential access, installing software, modifying OS security settings, deleting outside the approved directory, financial transactions, communication on behalf of the user, or elevated privileges. These cannot silently inherit a vague grant of 'use the entire PC'.
5. **Local dashboard + kill switch:** live indication of granted capabilities, action log, time budget, files changed, network destinations and process list. Stop immediately by terminating the listener or invoking a revocation control. A panic stop must not need access to ChatGPT.
6. **Crash/restart behavior:** fail closed on unexpected restart, expired session, lost connectivity or connector authorization; never quietly restore unlimited permissions. Keep durable per-job reservations, independent audit logs, and explicit recovery actions.
7. **Provenance and integrity:** all requests signed or MAC-verified with session-bound nonce/counter, exact schema, immutable payload hash, and authenticated connector identity. GitHub queue authenticity alone does not prove the user or a specific ChatGPT turn authorized the action.
8. **Project isolation:** keep AB/ESBM/PFL/LARP and other scientific repositories out of scope unless separately selected for that session. Prefer OS-level restricted accounts, working-directory allowlists, network restrictions and read-only mounts where feasible. Avoid accepting executable commands from arbitrary repository text or websites.
9. **No background autonomy by default:** Chat can carry out a sequence while a session and conversation actively use available tools. Persistent reasoning or proactive activity across turns requires separately supported scheduling/agent features; installing a listener does not itself make ChatGPT think in the background.

## Capability policy tiers

- **Tier 0 (baseline):** read-only workspace inspection and validated benign fixed-file operation; can run in disposable test workspace.
- **Tier 1 (development):** project-scoped file editing and a local catalogue of predeclared tests/build commands, no arbitrary shell interpolation.
- **Tier 2 (interactive desktop):** screenshots and narrowly approved UI input via locally trusted accessibility/automation primitives; require foreground indicator, sensitive-window exclusions, full audit and additional review.
- **Tier 3 (privileged/high-impact):** OS configuration, program installation, arbitrary shell, credentials, high-impact deletion, payments and outbound messages. **Not in scope of one-time unqualified authorization.**

A broad objective such as 'manage all my PC' should be decomposed into these inspectable capability grants. The model must not treat webpage, document or repository content as a new grant of authority.

## Upstream ChatGPT integration gate (currently unresolved)

**Observed facts:** manual v0 Chat → private GitHub → Windows → receipt succeeded. V1 listener was user-reported ready but the private GitHub job-creation action was explicitly blocked; task and receipt remained absent. The GitHub plugin already had app-specific **Allow all actions**, proving that this setting alone did not override the block. The expanded v1 offline suite passed 65/65 user-run Windows tests.

**Official docs (2026-10-30):**
- [Managing app permissions](https://help.openai.com/en/articles/20001495-managing-app-permissions-in-chatgpt): app-specific Allow all actions removes eligible approval prompts but does **not** override policy, provider access, or safety review.
- [Custom MCP servers](https://help.openai.com/es-es/articles/12584461-connecting-custom-mcp-servers-in-chatgpt): custom write-capable MCP currently belongs to Business and Enterprise/Edu; Pro personal can connect read/fetch-only custom servers. Full write entitlement of this personal Plus/Pro account is not verified.
- [Plugins in ChatGPT](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt): desktop-only local MCP apps may exist, but their usability depends on execution surface.
- [Submit desktop-only plugins](https://developers.openai.com/plugins/deploy/desktop-only): local MCP submission requires an approved partner; local plugins work in locally executed threads, not proof of ordinary Plus/Pro Chat support.

Do not disguise the rejected GitHub write, submit the same job through a substitute transport solely to evade restrictions, or treat local device authorization as permission from OpenAI. Future app/plugin paths require independent, affirmative support and a new explicit approval gate.

## Preferred next action

Investigate the availability of a **supported ChatGPT Chat action interface** that can reach the local agent under the user's plan, or obtain explicit confirmation from the provider. In parallel, draft (but do not deploy) the capability-profile and local session grant UX. **No reason to change the current v1 worker or ask for another Windows test until this upstream dispatch gate is resolved.**

No code, service, remote shell, bridge listener, or additional permission is authorized or activated by this ADR.
