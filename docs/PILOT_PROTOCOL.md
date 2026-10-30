# Pilot v0 — Chat → private GitHub queue → Windows worker → Chat

Status: **protocol draft only**. No Windows worker is installed or running; no end-to-end task has been executed.

## Repository boundaries

- Public source/documentation: `GalexY3/gpt-chat-local-bridge`.
- Private job transport: `GalexY3/gpt-chat-local-bridge-control`.
- Local disposable workspace: to be selected on Windows during setup. No personal folders, AB datasets, or other project directories are implicitly authorized.

GitHub connectivity in Chat is already observed. It does **not** demonstrate connectivity to the local computer.

## Version 0 job envelope

A Chat request is written as a UTF-8 JSON file under `jobs/pending/<job_id>.json` in the private repository:

```json
{
  "schema_version": 0,
  "job_id": "pilot-0001",
  "operation": "write_fixed_test_file",
  "workspace_profile": "isolated-pilot",
  "parameters": {},
  "expires_at": "2026-12-31T23:59:59Z"
}
```

This is an **example**, not an active dispatch. Do not enqueue it until the worker and its policy have been reviewed and installed. A real task must use a fresh ID and relevant expiry.

For v0, `operation` is an exact allowlisted symbol, **not** a command or path. The worker itself defines a fixed test filename and content. It must refuse any unexpected fields, unknown operations, expired requests, unsafe job identifiers, and incorrect workspace profiles.

## Worker behavior and receipts

- Poll only the configured private repository using outbound authenticated HTTPS, after a local opt-in.
- Accept only job files in the expected directory and validated schema.
- Run as a non-administrator in a dedicated workspace; do not use personal browser profiles or Windows desktop control in v0.
- Apply single-worker, one-shot execution with locally persisted idempotency state. On a duplicate task, do not repeat side effects.
- Write the known fixed text file only in the disposable local directory.
- Produce `jobs/receipts/<job_id>.json` in the private repository with job ID, state, local filename (relative, not an absolute user path), SHA-256, UTC timestamps, and an error code if needed.
- Distinguish `succeeded`, `failed`, `rejected` and `expired`. A job written to GitHub is not proof of local execution.
- Never publish access tokens, user names, machine identifiers, screenshots or private datasets in receipts.

GitHub repository write authorization is the initial transport trust boundary; it does **not** authenticate any particular ChatGPT turn cryptographically. Limit repository collaborators and authenticate through a fine-grained credential with the minimum necessary repository permissions, stored locally rather than in Git, logs, or chat. Do not use an unattended public self-hosted runner.

## Acceptance criteria

1. The public implementation passes local unit tests for invalid jobs and path escape attempts.
2. The user confirms the local workspace and explicitly starts the v0 worker.
3. Chat writes one new, valid, short-lived job to the private queue.
4. The Windows worker processes it and creates the expected local file.
5. A receipt appears in the private repository, with SHA-256 independently checked against the known expected bytes.
6. Chat reads the receipt and reports the observed result, including any limitations.

Next steps: inspect the Windows environment, implement the validator/worker and tests in the public repository, review the security boundaries, then perform the first real job. Do not add general PowerShell execution or GUI automation until the v0 round trip succeeds.
