# Repository collaboration notes

This repository is the public source and documentation for an experimental ChatGPT Chat to local-computer bridge.

## Continuity rule

The project owner wants every ChatGPT conversation, including an entirely new conversation with no memory, to be able to resume accurately from GitHub. The canonical record is [CONTINUITY.md](CONTINUITY.md).

At the end of each substantive project exchange, update that file with:
- the precise current state and any changed decision;
- what was actually completed, tested or observed, distinguishing user reports from verified results;
- relevant branch names, commits and blockers;
- the next specific task and the restart prompt.

Before replacing the file, fetch its latest content and blob SHA to avoid overwriting concurrent changes. Verify the write before reporting success. If it cannot be updated, disclose this clearly to the user. Preserve this convention in future handoffs.

## Engineering constraints

Do not conflate GitHub access with local Windows access. Keep the public source and private job transport separate. V0 supports only an explicitly authorized fixed test operation inside a dedicated local workspace; arbitrary command execution and personal desktop access are outside its scope. Never publish credentials, private personal data or local absolute paths. Implementation code belongs on a reviewable feature branch; do not merge to main without authorization.

The bridge is independent of AB, PFL, LARP and Mercados de pareja repositories. Do not change their scientific evidence or authorization records as part of this infrastructure pilot.
