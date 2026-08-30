# RULES — Shared Brain Research

**Work and evidence that aren't written down do not exist for the next agent.**

한국어 번역: [`RULES.ko.md`](RULES.ko.md)

## Starting a session

1. Read this file.
2. Read `system/context.md`.
3. Read the last 3-5 lines of `system/sessions/index.md`.
4. Look at the filenames in `tasks/doing/` — filenames only.
5. Read only the task and spec connected to the work at hand.

Do not read the whole repository every session.

## Reading tiers

| Tier | When | What |
|---|---|---|
| 0 | Every session | `context.md`, the tail of the session index, filenames in `doing/` |
| 1 | Starting a task | That task and the spec it links to |
| 2 | Only when needed | ADRs, knowledge, research, past sessions |

## Workflow

```text
inbox → planning/spec → tasks/backlog → tasks/doing → tasks/done
```

- `inbox/` is for capturing ideas. Do not implement straight from it.
- Write the requirements and the done condition into a spec or a task before building.
- When a task starts, move it to `doing/` and fill in `agent` and `started`.
- When it finishes, move it to `done/` and fill in `finished`, `closed_reason`, `result`.
- One task has one active writer.


The research flow:

```text
research question -> hypothesis -> experiment -> evidence -> claim/decision -> next
```

- Keep results and interpretation apart.
- A failed or invalid experiment is closed, never deleted.
- A `supported` claim needs real experiment evidence and a human review.
- Research files are Tier 2. Point at the active ones from context or a task.
Field names and allowed values are all in `system/conventions.md`. `brain-lint` rejects a
file that leaves them out, so read the table instead of guessing.

## Creating files

Task and session files are never created by hand.

```sh
python infra/new-task.py {slug} --title "Title"
python infra/new-session.py {slug} --agent {name} --tags {tags} \
  --hook "One line the next agent reads to decide whether to open this" \
  --did "What was done" --next "What is next"
python infra/new-experiment.py {slug} --project {project} \
  --title "Experiment title" --hypothesis {hypothesis}
python infra/new-meeting.py {slug} --title "Meeting title" --project {project}
```

Filling in the body of a generated task or session afterwards is expected.

## Closing a session

Leave a session summary if the next agent needs to know about the work.

- Unfinished work belongs in a task, not in the summary.
- Changes to the current state go into `system/context.md`.
- Reusable lessons are promoted to `knowledge/`.
- A typo fix or a wording change can skip the task and the session summary.

## Research records

Research and experiment records live in `research/{project-slug}/`. Conventions and
templates are in `research/README.md`.

- Every project has `overview.md`, `questions.md`, `claims.md`, and `experiments/`.
- **Name one canonical document** and keep the conclusions only there. Execution logs are a
  separate document.
- Research is Tier 2. It is not read during the start procedure — open it when needed.
- Raw data, model weights, and secrets do not go in Git. Record where they are instead.
- A quantitative result records dataset/version, code commit, seeds/repeats, artifact,
  and the kind of evidence.
- `python infra/research-lint.py` checks the experiment, claim, and feedback
  contracts.
- **Just before a number hardens into a claim** — promoting a claim to `supported`,
  closing an experiment, moving a figure into context — apply
  `skills/experiment-claim-check`. Lint sees whether evidence exists; it cannot
  see whether that evidence supports the claim.

## Meeting feedback

Meeting files live in `feedback/meetings/`. The full contract is in `feedback/README.md`.

- `visibility` defaults to `redacted`.
- **What someone said is not a fact and not a decision.** Keep quote, paraphrase, and
  inference apart.
- An AI may extract candidates, but never writes `human_approved: yes` on a person's behalf.
- Feedback becomes `accepted` only with human approval and a linked artifact.
- Shipping something does not make it `validated`. Confirm the problem was actually solved.
- `human_approved` records provenance, not identity. Real approval is established by Git
  review history.

## Optional areas

`personal/` is an empty extension point kept for compatibility with the base starter. It is
not in scope for this distribution.

## Prohibited

- Building a feature with no spec and no done condition
- Recording an unverified claim as `supported`
- Moving feedback to `accepted` or `validated` without human approval
- Recording something said in a meeting, or an AI inference, as a settled decision
- Creating a task or session file without the generator
- Recording an unverified result as complete
- Committing real personal data, tokens, or secrets to a public repository
- Storing large datasets or model files directly in Git
- Committing raw recordings or transcripts to a public repository
