# Evidence addendum — ChatGPT Chat to Windows, 2026-10-31

**Purpose:** correct the overly categorical implication that no alternatives exist. Source review only. No installation, deployment, private task dispatch or Windows service initiated.

## Confirmed official Chat-compatible alternative worth testing

**ChatGPT Sites-hosted MCP plugin.** Official OpenAI documentation confirms:
- ChatGPT Sites is available to personal Plus and Pro users: https://help.openai.com/es-es/articles/20001339-creating-and-using-chatgpt-sites
- A Site can host MCP tools; its plugin can be installed and invoked from a ChatGPT **chat**, and Site tooling can be designed for **write/change** actions, subject to application and account permissions: https://help.openai.com/es-es/articles/20001547-hosting-a-plugin-with-chatgpt-sites
- Sites creation/editing invokes Work/Codex quota and Sites runtime/hosting usage is accounted for separately. This does not establish zero additional hosting cost or unlimited plan usage.
- A Site MCP tool needing external effects requires a supported, authenticated external API. For the Windows worker, a legitimate design would require a formally authorized interface, scoped identity and a local device transport; not a generic remote shell. The previous connected GitHub job creation was explicitly blocked; Site hosting does not override this.

**Important distinction:** generic custom remote MCP servers with full write actions remain plan-limited primarily to Business/Enterprise/Edu according to https://help.openai.com/es-es/articles/12584461-connecting-custom-mcp-servers-in-chatgpt . A Site-hosted plugin is a separately documented product path, but it is not proof that a personal account may install arbitrary high-risk local machine tools or avoid action confirmation.

## Discovered open-source implementations

- https://github.com/int04/ChatCmd — cross-platform, local-first Rust runtime with MCP, local terminals/files/Git/process operations, scoped profiles, user approvals and an optional Chromium extension for ChatGPT web conversations. The README says the core has no subscription/API dependency. Requires audit and tests; self-described as independent of OpenAI and includes an **unofficial DOM extension**. This is concrete evidence of a technically plausible architecture, NOT an independently proven/sanctioned Windows/ChatGPT integration for this user.
- https://github.com/Dworrall21/chatgpt-bridge — Chrome extension + local Python bridge that presents authenticated ChatGPT web as an agent-invocable interface without an API key; its primary direction is local agents calling ChatGPT, not necessarily normal ChatGPT initiating Windows actions.
- https://github.com/Tzufucius/web-llm-bridge — browser-hosted ChatGPT session adapter for local agents; self-described alpha. Likewise mostly the reverse direction.

**Terms caveat:** OpenAI Europe consumer terms https://openai.com/es-ES/policies/eu-terms-of-use/ prohibit automatic/programmatic extraction of service data/output and circumventing protective measures. The exact contractual status of any individual extension is not adjudicated here; do not recommend installing or operating an unofficial browser-scraping bridge as a safe, officially supported workaround.

## Updated, evidence-graded conclusion

It is incorrect to say **no ways exist**. A promising official Chat-compatible **Sites MCP plugin** pathway and independent open-source browser bridges are documented and worth evaluation. However **no full zero-touch, unrestricted Windows control on a personal Plus/Pro Chat account has been independently demonstrated here**, and the previously blocked connected GitHub queue write remains unresolved.

**Priority 1:** A harmless, account-specific eligibility test: check whether user can create/use a Sites-hosted MCP plugin in ordinary Chat, with a read-only or mock no-effect tool first; establish whether permitted plugin actions include writes and whether extra usage/hosting costs arise. Never dispatch a local Windows task or activate a service as part of checking eligibility.

**Priority 2:** If official plugin pathway is actually authorized, design a least-privilege, session-scoped Windows bridge with auditing and local kill switch. The user prefers one-time consent and repeated ordinary low-risk operations without prompts; indefinite arbitrary full-PC access should not be granted through a blanket permission.

**Priority 3:** Review (not install) ChatCmd implementation/security as an architectural reference, separating its local MCP runtime from its unofficial browser DOM extension. Do not use an alternate transport to disguise or bypass a platform-blocked action.

No new test results, no code execution, no repo merge and no service activation resulted from this research.
