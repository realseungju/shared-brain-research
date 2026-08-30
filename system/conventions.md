# Conventions

한국어 번역: [`conventions.ko.md`](conventions.ko.md)

## Filenames

| Location | Format |
|---|---|
| `tasks/*/` | `TYYYY-MM-DD-{slug}.md` |
| `system/sessions/` | `YYYY-MM-DD-{slug}.md` |
| `specs/` | `{slug}.md` |
| `knowledge/` | `{slug}.md` |
| `research/` | `{project-slug}/{doc-slug}.md` |
| `inbox/` | `YYYYMMDD-{source}-{slug}.md` |
| `research/*/experiments/` | `EYYYY-MM-DD-{slug}.md` |
| `feedback/meetings/` | `YYYY-MM-DD-{slug}.md` |

A slug uses lowercase letters, digits, and hyphens only. Template files whose name starts
with `_template.md` are the exception.

## Task frontmatter

`infra/new-task.py` creates it and `infra/brain-lint.py` checks it. When you move a task
between states by hand, you fill these in yourself.

| Field | Required when | Value |
|---|---|---|
| `id` | Always | Exactly the filename without the extension |
| `title` | Always | One-line title |
| `phase` | Always | `planning` \| `review` \| `implementation` \| `validation` |
| `assignee_role` | Optional | The role responsible, not a person's name |
| `spec` | Optional | The linked `specs/{slug}.md`, or `none` |
| `agent` | In `doing/` | The writer currently holding this task |
| `started` | In `doing/` | `YYYY-MM-DD` |
| `finished` | In `done/` | `YYYY-MM-DD` |
| `closed_reason` | In `done/` | `completed` \| `cancelled` \| `superseded` |
| `result` | In `done/` | A commit hash, PR number, or other checkable artifact |

`phase` is **which stage the task is at**; `backlog/doing/done` is **which directory it is
in**. They are independent — a `planning` task sitting in `doing/` is normal.

## Task states

```text
backlog → doing → done
```

Closing reasons:

- `completed`: the goal was reached
- `cancelled`: stopped with no plan to resume
- `superseded`: replaced by a different approach

## Session frontmatter

`infra/new-session.py` creates it. Do not create one by hand.

| Field | Value |
|---|---|
| `date` | `YYYY-MM-DD` — must match the first part of the filename |
| `agent` | The writer's name |
| `slug` | Must match the rest of the filename |
| `tags` | A list of lowercase-hyphen tags |

The body must contain a `## What was done` section and an `## Open and next` section — both
are checked by lint. `## Decisions and why` and `## Cautions` are written by the generator
but not enforced. Every session file must have a one-line entry in
`system/sessions/index.md`; the generator adds it, so this only matters if you delete a
file.

## Experiment frontmatter

`infra/new-experiment.py` creates it and `infra/research-lint.py` checks it.

| Field | Value |
|---|---|
| `id` | `EYYYY-MM-DD-{slug}`, identical to the filename |
| `title` | One-line title |
| `project` | Same as the parent `research/{project}/` |
| `date` | Same as the date in the filename |
| `status` | `planned` \| `running` \| `completed` \| `negative-result` \| `invalidated` |
| `hypothesis` | A hypothesis id, or the hypothesis in one line |
| `evidence_kind` | `measured` \| `estimated` \| `unverified` |
| `dataset_version` | Dataset name and version |
| `code_commit` | A 7-40 character Git SHA, or `not-applicable` |
| `seed_or_repeats` | Seeds, or the repeat condition |
| `artifact` | Where the output lives outside the repo, or how to regenerate it |

`completed`, `negative-result`, and `invalidated` are closed states. Closing an experiment
means removing every `TBD` from the reproducibility fields, filling in the results,
interpretation, and limits, and not leaving `evidence_kind: unverified`.

## Claim entries

Each `## C001` entry in `research/{project}/claims.md`:

| Field | Value |
|---|---|
| `statement` | One claim, stated so it can be reviewed |
| `status` | `candidate` \| `supported` \| `rejected` |
| `evidence` | Path to an experiment file in the same project |
| `evidence_kind` | `measured` \| `estimated` \| `unverified` |
| `human_reviewed` | `yes` \| `no` |
| `reason` | Why it was rejected |

`supported` needs all three: an experiment that exists, a verified evidence kind, and
`human_reviewed: yes`. **A result file existing is not, by itself, support.**

## Meetings and feedback

Meeting frontmatter:

| Field | Value |
|---|---|
| `date` | Same as the date in the filename |
| `title` | One-line title |
| `project` | A project slug, or `product` |
| `visibility` | `public` \| `private` \| `redacted` — the generator defaults to redacted |
| `status` | `captured` \| `triaged` \| `closed` |

Each `### FB-YYYY-MM-DD-01` entry:

| Field | Value |
|---|---|
| `scope` | `product` \| `research` \| `workflow` |
| `kind` | `request` \| `problem` \| `observation` \| `question` \| `decision-candidate` |
| `statement` | One atomic request or observation |
| `source_mode` | `quote` \| `paraphrase` \| `inference` |
| `status` | `captured` \| `accepted` \| `rejected` \| `deferred` \| `validated` |
| `human_approved` | `yes` \| `no` |
| `linked_artifact` | The task, hypothesis, claim, or ADR file it connects to |
| `reason` | Why it was rejected or deferred |
| `validation` | What confirmed the problem was actually solved, before it became validated |

Any triage beyond `captured` needs human approval. `accepted` and `validated` need a linked
file that exists; `validated` needs a real confirmation. An approved `decision-candidate`
must point at `system/decisions.md#ADR-...`.

`rejected` and `deferred` require a `reason`. Do not put the triage reason in `validation`
instead. A meeting reaches `status: closed` only when every feedback item is `rejected` or
`validated` — one remaining `captured`, `accepted`, or `deferred` keeps it open.

`human_approved` records the provenance of an approval; it does not authenticate who wrote
it. Lint checks field and state consistency. Whether a human really approved is established
by Git commit and PR review history, or by branch protection.

## Commits

Conventional Commits are recommended.

```text
<type>(<scope>): <imperative summary>
```

## Documents

- State the conclusion first.
- Do not copy the same content into several documents.
- Keep current state and reusable knowledge apart.
- Leave what the next agent needs, and no more.
- Meeting sources are Tier 2. Only accepted items are pointed at from active
  context or tasks.
