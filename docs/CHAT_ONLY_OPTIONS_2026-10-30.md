# Chat-only zero-marginal-API bridge: alternatives and decision memo

**As of:** 2026-10-30. **Objective:** ordinary ChatGPT **Chat** as primary interface under a personal **Plus/Pro** subscription, without additional OpenAI API inference billing. Windows local execution must be user-authorized, bounded and auditable. Research only: no live queue dispatch, no deployment, no service, and no merge.

## Baseline: observed evidence

- Manual v0: ChatGPT's connected GitHub action successfully created one harmless private queue item, the Windows worker explicitly executed it, and GitHub receipt and physical Windows SHA-256 matched. This is a **single observed success**, not an unconditional future authorization.
- V1: bounded listener displayed `listener_ready`, but a subsequent connected GitHub task creation was **blocked by host security controls** before a job appeared in the private queue. Reads of that job and its receipt were 404. User stopped listener.
- User-run full offline test suite: **65/65 PASS**, 0 failures/skips, 0.147 s, Python 3.14.3. These tests do not establish live v1 dispatch.
- User does **not** want Work/Codex or a separately billed model API to serve as the primary chat/LLM.

## Current published product constraints (official sources)

1. OpenAI's **ChatGPT Plus** FAQ explicitly says ordinary API usage is separate from the subscription: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus
2. **Personal Free/Go/Plus/Pro accounts cannot create new custom GPTs** as of October 2026; existing GPTs are scheduled for retirement **Dec 11, 2026** (subject to notice): https://help.openai.com/en/articles/8554397-creating-and-editing-gpts and https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq
3. **GPT Actions** technically support OpenAPI HTTP actions and API key/OAuth, but only in eligible existing GPTs and **not in Pro mode**; actions do not automatically migrate to plugins: https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts
4. **Custom MCP servers with full write/modify actions** are documented for Business and Enterprise/Edu workspaces; personal Pro was previously documented as read/fetch, and personal Plus/Pro are not established as eligible for full custom MCP writes: https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
5. **Plugin directory** works in Chat, Work and Codex, but capability depends on the chosen app, plan, region, permissions and action confirmations. Installing a plugin never overrides connector or provider controls: https://help.openai.com/en/articles/20001256-plugins-in-chatgpt
6. **Desktop-only local MCP plugins** are supported for locally executing threads, and publishing local MCP plugins is restricted to approved partners. This does **not** verify that *ordinary* Chat mode on a personal Plus/Pro account can invoke such a local executable: https://developers.openai.com/plugins/deploy/desktop-only
7. The ChatGPT desktop **built-in browser / WebMCP site tools** can expose actions, but the documented browser entry explicitly requires opening a **Work or Codex** chat: https://help.openai.com/en/articles/20001277-using-the-built-in-browser-in-the-chatgpt-desktop-app and https://help.openai.com/en/articles/20001423-using-site-tools-in-the-chatgpt-desktop-app
8. **Sign in with ChatGPT / token sharing** can let participating partner apps consume an eligible subscriber's included **Work/Codex usage**, without separately providing an OpenAI API key; such apps can have their own fees and don't keep standard Chat as their UI: https://help.openai.com/en/articles/20001542-using-your-chatgpt-plan-in-other-apps-and-sites
9. The EU terms prohibit **automatic/programmatic extraction of service data/output** and circumvention of safety measures. Browser extensions that scrape the ChatGPT DOM to auto-dispatch commands raise contractual and security risks; we have not verified a permitted exception: https://openai.com/es-ES/policies/eu-terms-of-use/
10. Cloudflare Workers Free is advertised as **100,000 requests/day**, but free hosting is not a ChatGPT write-action entitlement: https://developers.cloudflare.com/workers/platform/limits/

## Decision matrix

| Option | Chat UI | Extra OpenAI inference billing | Real automatic dispatch | Feasibility under constraints |
| --- | --- | --- | --- | --- |
| Existing connected GitHub action, strictly authorized | Yes | None for Chat turns | Possible only if host approves each permitted write | V0 worked once; v1 attempt blocked; cannot assume permission |
| Existing preapproved write-capable plugin | Yes if available for plan/account | None for Chat turns | Possible within allowed app actions | Investigate approved actions; not a general PC executor |
| Custom GPT + Actions | Separate GPT chat | None for Chat turns | Historically possible | New personal GPT creation unavailable; near retirement |
| Custom remote MCP write app | Chat interface where eligible | No extra Chat inference | Technically yes | Full custom writes not established for personal Plus/Pro |
| Local MCP desktop-only plugin | Local thread | Depends on local Work/Codex usage | Yes in supported local execution | Not verified for **ordinary Chat**; public submissions approval-gated |
| Built-in browser WebMCP site tools | Work/Codex | Draws on relevant entitlement/usage | Yes | Does not meet Chat-only constraint |
| Sign in with ChatGPT participating app | External app UI | Can consume plan Work/Codex allowance | Possible | Not Chat UI and may have vendor fees/limits |
| Plain Chat visible job + explicit copy/paste to local worker | **Yes** | **None** | No: at least one user action | **Immediately designable; strongest compliant fallback** |
| Plain Chat visible job + user-clicked launch/deep link | **Yes** | **None** | Not zero-touch; one local handoff click | Plausible; handler/localhost URI behavior must be tested and authorized |
| Downloaded task file + local watcher with approval | **Yes** | **None** | One download/approval | Plausible; requires safe allowlisted schema, user-directed download |
| Browser DOM scraping/extension → localhost | Chat web | None | Potentially automated | **Not recommended:** EU terms and safety/fragility concerns |
| Direct paid OpenAI API + local agent | Independent UI unless integrated | **Additional billable API usage** | Yes | Excluded by user's cost/Chat constraints |

## Preferred research and implementation direction

**Track A: minimum-friction, explicitly user-mediated Chat-to-Windows transfer, not an alternate hidden transport for a rejected remote write.**

- Preserve the current Plus/Pro **Chat** conversation and worker protocol. Chat formats a human-readable strict JSON operation description (fixed task type, expiration, immutable ID, no arbitrary command or path) with a copy control. The user explicitly selects/copies it and approves it in a small local Windows intake UI. A simple, nonpersistent local intake process accepts only the fixed allowlisted operation; do not read ChatGPT pages or authentication cookies.
- The worker writes its receipt to the existing private control GitHub repository if that locally authenticated operation remains allowed; ChatGPT may then read the receipt using authorized read-only GitHub access. If receipt upload fails, surface user-readable output; never re-execute on receipt failure.
- Later, assess whether a user-clicked deep link or file-download handoff can reduce friction further **without automatic ChatGPT DOM extraction**. The Chat platform might not permit clickable non-HTTP protocols or localhost; do not assume it works.
- Security gates: exact schema, no script/PowerShell parameters, explicit local confirmation, fixed workspace, per-job output isolation, TTL, idempotency, no admin privileges, no startup service, no arbitrary shell, provenance clearly marked as user-submitted rather than cryptographically chat-authenticated.
- This architecture is **a design proposal, not built or demonstrated**. It does not meet the fully automatic zero-touch goal, but preserves Chat and zero incremental model API costs.

**Track B: official native write capability review.**

- Retain the connected GitHub plugin as a *conditionally* available option; the earlier host block must not be bypassed by changing transport, disguising the executable task, or moving the queue to a different app.
- Use supported product feedback/support to ask whether a deliberately narrow, non-executable task is supported under the current ChatGPT plan/tool policy. Record permissions and approval behavior, not assumptions.
- Consider future custom MCP tools or officially published local integrations **only if** the account/plan and Chat surface are confirmed eligible. A custom plugin/Plugin Creator skill cannot grant new action rights.

## Immediate action plan

1. No more broad simulation for the existing 65-test worker; no new live queue writes without an approved path and separately scoped test authorization.
2. If the user accepts *one user-initiated transfer per job*, design a minimal local intake flow and tests in a **separate reviewable feature branch**, retaining user approval and no arbitrary execution.
3. If the user strictly requires zero-touch **automatic** execution, document the current limitation: no verified native custom dispatch entitlement in personal Plus/Pro Chat. Prioritize official app/provider permissions and support, not scraping or contract-violating automation.
4. Do not merge to main, touch scientific repositories, install services, or expose personal credentials.

**Epistemic notes:** Product terms and entitlements may change. We have not verified the user's account-specific admin settings, whether any locally executing Chat thread can invoke local MCP, or why the specific v1 connected job creation was blocked. No claim of full zero-touch viability is made.
