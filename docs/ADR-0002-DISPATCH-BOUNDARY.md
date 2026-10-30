# ADR-0002 — Explicit dispatch boundary and fail-closed transport

**Status:** Engineering investigation. 2026-10-30. No workaround authorized or deployed.

## Evidence and limits

The first v0 test succeeded through the private GitHub queue and an explicitly invoked Windows worker; its local file and SHA-256 were checked by the user. In the v1 session, the user reported `listener_ready` from the bounded foreground worker. The attempt by ChatGPT's connected GitHub action to create one additional fixed-file job returned an explicit *security-control block*. Subsequent reads of the proposed pending-job path and receipt path returned 404. The user later confirmed the listener was stopped.

**The evidence places the observed failure at the chat-side write attempt; it does not show a v1 job running or failing on Windows.** The internal reason why the connected GitHub write was blocked is not available. We must not claim that GitHub itself rejected a valid REST request, that there was a worker fault, or that the platform will consistently reject all future dispatches.

## Boundary

A GitHub-connected chat has its own authorization and safety controls. A private repository and user consent do not override the host's decision to block an action. A local CLI being able to write to the repository does not confer a permission on ChatGPT to do the same.

**Do not:**
- reproduce the rejected remote job by calling a different connector, browser, HTTP client, workflow or repository path for the purpose of bypassing that block;
- ask the user to paste a GitHub token or run an alternate command to sneak the same queued operation through;
- retry an explicitly blocked action through disguised content or altered command semantics;
- characterize a queue entry, simulated receipt, local offline test or old v0 result as a successful live v1 round trip.

## Development that remains possible

- Maintain the v1 source and test it locally and offline using mock GitHub responses.
- Improve error handling, bounded lifetime, deduplication, path safety, redacted receipts and auditability.
- Document external preconditions and differentiate **written tests**, **executed tests** and **observed end-to-end operations**.
- Provide a read-only status view of the queue if permitted by the connection, without creating executable jobs.
- Research supported, officially authorized integrations for dispatch, including how permissions, approval and audit trails work. An approved path would need a separate security and product review, not a renamed copy of the blocked dispatch mechanism.

## Current gate

The v1 implementation has passed 55/55 user-run Windows unit tests (with mocked filesystem rejection checks). The bounded listener displayed `listener_ready` during a user-authorized trial, but the platform blocked writing the requested job. That trial **did not satisfy end-to-end acceptance**. No worker is expected to be running now.

Additional mock transport tests may be developed and executed without changing this status. The repository must not contain credentials, personal local paths, private research data or any general remote shell feature.

## Requirement for revisiting live dispatch

A future test can only be scheduled if an explicitly supported, approved connector/action path exists and the user provides new authorization for the specific test. A new trial must confirm the listener is freshly ready, create one authorized short-lived fixed-file job, obtain a legitimate receipt, and compare a real physical-file SHA-256, all without bypassing host controls.

Until then, document the bridge as **manual v0 end-to-end validated; v1 listener unit-tested; live v1 dispatch blocked at chat-side transport**.
