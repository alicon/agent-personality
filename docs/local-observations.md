# Local inspection: October 10, 2026

This was a read-only inspection of the current instruction setup and selected metadata from this chat's local session log. No live personality, model catalog, instruction file, or permission was changed.

## Observed

| Item | Observation | What it means |
| --- | --- | --- |
| Global AGENTS.md | 49,550 bytes; references the shared voice contract; writable by the current agent process; no immutable flag observed | Mutation is technically possible. This is not evidence it occurred or caused drift. |
| Human-communication skill and voice contract | Both writable by the current process; no immutable flag observed | Their contents currently rely on instructions and ordinary filesystem access rather than a separate write boundary. |
| Global override | No AGENTS.override.md found | That particular override was absent at inspection time. |
| Workspace guidance | No pre-existing AGENTS.md or AGENTS.override.md in this initially empty checkout | There was no additional local file discovered here before repository setup. The user-supplied instructions still applied. |
| Configured project document limit | 131,072 bytes | The global file alone is below this configured limit. This does not prove the complete request avoided truncation elsewhere. |
| Configuration model | gpt-6.1-sol, high reasoning effort | A named model alias is known; an immutable provider snapshot was not established. |
| Two recorded turn contexts | gpt-6.1-sol, high effort, friendly personality mode | Model and these settings matched across the two available records. This is too little evidence to establish long-term stability. |
| Session record | One base-instruction snapshot and turn-context metadata available | The inspected metadata do not establish every final assembled request or every provider-internal instruction. |
| Current injected guidance | Communication directions appear in several layers, alongside technical-work instructions | Instruction interaction is a plausible hypothesis, not an observed causal explanation. |

## Snapshot fingerprints

These identify the bytes observed at inspection time. They are not evidence of historical stability.

| Source | SHA-256 |
| --- | --- |
| Global AGENTS.md | 119422e717d65228200884f81e01be58295faede946bf0e24108e7ada90bbcc4 |
| Human-communication SKILL.md | 2f584f3701df65186456a64a090181b8cfab1466425f94d4d337625b74ff6061 |
| Shared voice-contract.md | 1af2a0888af8c12386cc1163850426baf258ec11b3efd1889b1df31c40c5e62d |

The session's base-instruction digest was computed over its serialized stored representation, not final outbound prompt bytes. It is omitted from the source-file comparison to avoid implying those boundaries are interchangeable.

## Unresolved

There is no before/after trace around a reported drift episode. We have not established whether a core instruction changed, disappeared, was summarized, was overridden, or stayed intact while behavior changed.

The next diagnostic action is to capture a synthetic session at the request assembly boundary and repeat behavioral probes under controlled history. Do not fetch unrelated work transcripts to fill the gap.

## GitHub tracking

The repository is private and Issues are enabled. Repository creation and issue/label/milestone APIs work.

The CLI's Projects read request failed with: “your authentication token is missing required scopes [read:project]”. This is a confirmed limitation of the current CLI credential, not a general GitHub platform limitation. A Projects board is optional: priority labels, status labels, issue dependencies, and milestones provide the initial queue. The account owner can grant appropriate Projects scopes if a board is wanted.

**Next decision:** None; continue with Issues and establish request observability for the diagnostic pilot.
