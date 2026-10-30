# GPT Chat Local Bridge

> **Status: design / pre-alpha. No local executor has been installed or tested.**

An experimental, community-oriented bridge for dispatching **explicitly authorized** tasks from a conversational AI client to a local computer and returning auditable results.

The first target is **ChatGPT Chat → GitHub → a Windows worker**. GitHub is a transport, not an execution engine. A ChatGPT conversation cannot access your local files or control your desktop merely because you have connected a GitHub repository.

This is an independent project. **It is not an official OpenAI or GitHub product.**

## Goals

- Keep a standard chat conversation as the interface for proposing and reviewing tasks.
- Run a deliberately small allowlist of operations inside a dedicated local workspace.
- Record task identifiers, source revisions, state transitions, stdout/stderr summaries, and result hashes.
- Eventually support reproducible scientific computing and permitted GUI workflows.
- Keep project-specific workflows (research, software development, games) separate from the generic transport and execution mechanisms.

## Architecture (planned, not implemented)

```text
ChatGPT Chat
    |
    | Authorized GitHub connector writes a structured job
    v
Private control repository (queue, status, redacted receipts)
    ^
    | Outbound HTTPS polling; no inbound public port required
    v
Local Windows worker
    |
    +-- policy validation / explicit allowlist
    +-- isolated test workspace
    +-- bounded execution and result capture
    +-- optional browser/desktop adapters (later phase)
```

The **public repository contains source code and documentation only**. A separate **private** control repository is required for real job dispatch; it must not contain secrets, full private data, or broadly executable commands. Do not point a worker at public issues or pull requests as an implicit execution queue.

## First pilot acceptance test

1. The user explicitly authorizes a task in ChatGPT Chat.
2. The chat writes a structured test request into the private control repository.
3. A locally installed worker verifies repository identity, task identity, policy, and allowed workspace.
4. The worker performs **one harmless, predefined operation** inside the test workspace (for example, creating a text file).
5. The worker publishes a redacted receipt and cryptographic hash.
6. The chat reads the receipt and distinguishes successful execution from a proposed or failed task.

**No claims of a working end-to-end connection until all six steps have been observed.**

## Security principles

- **Default deny.** No general-purpose shell endpoint, unrestricted PowerShell, or arbitrary Python execution from remote job content.
- **Least privilege.** The worker runs without administrator rights and cannot reach directories outside its configured workspace by default.
- **Separate authority.** The public source repository is not a trusted job queue. Never execute unreviewed code from public contributions.
- **Controlled inputs.** Use versioned job schemas, operation-specific validators, bounded inputs, and explicit approval policies.
- **No exposed secrets.** Credentials stay local in secure storage; do not commit tokens, personal paths, private datasets, or raw screenshots.
- **Bounded resources.** Apply timeouts, memory/CPU constraints where supported, output limits, and an emergency stop.
- **Auditable outcomes.** Distinguish queued, rejected, running, succeeded, failed and timed-out operations.
- **GUI isolation.** Browser profiles and desktop automation must not silently act in personal authenticated sessions.

A design document is not a security audit. Treat the first release as experimental and do not use it for sensitive accounts or privileged system administration.

## Roadmap

- [ ] Define the job schema, threat model and acceptance tests.
- [ ] Implement a local dry-run validator with no network access.
- [ ] Implement a private GitHub transport and idempotent worker.
- [ ] Demonstrate the Chat → Windows → Chat round trip.
- [ ] Add a sandboxed scientific-computing adapter.
- [ ] Add opt-in Playwright browser tests.
- [ ] Evaluate opt-in Windows UI Automation support.
- [ ] Add portable interfaces for other transports and operating systems.

## Contributing and licensing

Contributions, feedback and security reviews are welcome once the initial repository conventions are established. **No open-source license has been chosen yet.** Until a license is added, do not assume permission to redistribute or reuse the code.

Please do not publish authentication tokens, personal information, or unredacted execution logs in public issues.

---

Maintained as a proposed cross-project infrastructure: scientific research projects can use the bridge, but no project is required to adopt it or relax its own governance rules.
