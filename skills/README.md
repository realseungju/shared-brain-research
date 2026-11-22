# Skills

The extension point for user-defined skills.

## Included skills

| Skill | When |
|---|---|
| [`experiment-claim-check`](experiment-claim-check/SKILL.md) | **Just before an experimental number is recorded as a claim** — in a claim, an interpretation, or a session summary |

`research-lint` checks that evidence *exists*; this skill checks whether the evidence is *valid*.
The two layers do not replace each other (ADR-007).

## A new skill

Copy `_template/SKILL.md` and fill in the name, description, procedure, and what is forbidden.
Where each AI tool discovers skills can differ, so check that tool's documentation.
