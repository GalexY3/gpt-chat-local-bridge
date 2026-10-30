# Transport support research — 2026-10-30

**Status:** Documentary assessment, not a deployment decision or permission to dispatch. The chat-side creation of the v1 job was blocked and the listener was stopped.

## Official primary sources

- [OpenAI Help Center: Connecting GitHub to ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt): documents GitHub repository reading and code analysis. Its FAQ currently says the standard ChatGPT GitHub app is read-only and directs editing and pushing code to Codex.
- [OpenAI Help Center: Developer mode and MCP apps](https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt): documents custom MCP apps with permissible write/modify actions, confirmations, and current Business/Enterprise/Edu full-MCP plan/workspace limitations.
- [OpenAI Help Center: Connecting custom MCP servers](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt): documents custom MCP integrations, administrator permissions, possible write-action blocks, and remote or supported secure tunnel connectivity.

These are product documentation statements, not evidence that the user's individual account has access to custom write-enabled MCP integrations. This research did not configure or deploy any connector.

## Observations to distinguish

- Previously, the connected GitHub tools DID create/update project files and DID create the harmless v0 job in the private repository, with a separately observed Windows result. These are historical successes, not unlimited future write authorization.
- The newer v1 queue write was explicitly blocked by host connection security controls. Follow-up GitHub reads found neither the intended new task nor its receipt. The exact internal reason was not provided; it cannot be verified.
- The official statement that the *standard* GitHub ChatGPT app is read-only does not establish that every other available GitHub plugin surface must be read-only. A tool's existence is not proof that a particular requested write will be authorized.
- Separate gates: reading GitHub, having a write-capable connector action, receiving host approval for a particular write, and locally executing a validated task on Windows.

## Design boundary

Do not retry the rejected private queue write through disguised requests, alternate transports, different repositories, browser automation or copying user credentials. Continue with supported read-only observation, documentation and offline engineering.

A permissioned custom MCP server could theoretically expose a narrow fixed-task submission action with user approval and rate limits. **That is only a future architecture candidate, not a proposed bypass or an enabled feature.** It would need an eligible ChatGPT workspace, app approval, security analysis, supported hosting and explicit user authorization before development or deployment.

## Current decision

Manual v0 round trip: verified. V1 offline tests: 65/65 user-run passes. V1 foreground listener: readiness observed, then stopped. V1 live dispatch: blocked at chat-side job creation, not verified on Windows. Do not claim a working unattended/automatic bridge until a supported, approved transport is demonstrated.
