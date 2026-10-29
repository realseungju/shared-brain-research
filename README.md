# Shared Brain Research

Git-native experiment memory and cross-agent handoff for computational researchers.

한국어 문서: [README.ko.md](README.ko.md)

Shared Brain Research turns a repository into the durable working memory for Claude Code,
Hermes, Orca, Codex CLI, and other coding agents. It keeps research questions, experiment
conditions, evidence, claims, meeting feedback, tasks, and session handoffs in plain
Markdown with a lint gate that rejects unsupported state transitions.

```text
question → hypothesis → experiment → evidence → human-reviewed claim
meeting → atomic feedback → human triage → linked work → validation
```

It is not a note-taking app or a model runner. The repository root is the AI platform's
project or working directory. The agent does the file and Python work; the researcher
sets intent, approves claims and feedback, and reviews the evidence.

## Why it exists

Research handoffs usually lose the details that matter: which commit ran, which dataset
version was used, whether a result was measured or inferred, and which statement was
recorded as human-reviewed. This project keeps those boundaries explicit:

- Every closed experiment records reproducibility fields, results, interpretation, and
  limits.
- Under the lint contract, a claim cannot become `supported` without linked experiment
  evidence and `human_reviewed: yes`.
- Meeting comments remain source material until a human accepts, rejects, or defers each
  atomic feedback item.
- Sessions leave a small indexed handoff, so a different agent can continue without
  loading the whole repository.
- `research-lint` enforces the contract locally and in CI.

## Quick start

Requirements: Git and Python 3.10+ in the agent environment. There are no third-party
Python dependencies.

1. Create a repository from this template or clone it.
2. Open its root as the project, workspace, repository, or working directory in your AI
   platform. It must be the directory containing `AGENTS.md`, `CLAUDE.md`, and `system/`.
3. Start with a natural-language request:

> Read the repository instructions first. Initialize a research project named
> `my-project`, update the current context, record my first research question and
> hypothesis, and create a planned baseline experiment. Ask me before accepting any claim
> or meeting feedback.

4. Keep using the same repository from Claude Code, Hermes, Orca, Codex CLI, or another
   compatible agent. Commit and push when another machine or colleague needs the state.

You normally do **not** type the Python commands yourself. Agents use these canonical
operations while carrying out your requests:

```sh
python infra/new-task.py baseline --title "Run baseline"
python infra/new-experiment.py baseline \
  --project my-project \
  --title "Baseline" \
  --hypothesis H001
python infra/new-meeting.py weekly-review \
  --title "Weekly research review" \
  --project my-project
python infra/new-session.py baseline-result \
  --agent Hermes \
  --tags research,handoff \
  --hook "Open the baseline experiment and C001" \
  --did "Recorded the baseline result" \
  --next "Review whether C001 is supported"
python infra/research-lint.py
```

The commands are documented for agent consistency and manual troubleshooting. Exact
schemas and allowed values live in
[`system/conventions.md`](system/conventions.md).

## Research workflow

Each live project uses this shape:

```text
research/{project}/
  overview.md
  questions.md
  claims.md
  experiments/
    EYYYY-MM-DD-{slug}.md
```

Ask an agent to copy the three files from `research/_template/`, create `experiments/`,
and replace the placeholders. Experiments start as `planned` or `running`. Closing one as
`completed`, `negative-result`, or `invalidated` requires a dataset version, code commit,
seed or repeat condition, artifact location, evidence kind, results, interpretation, and
limits.

Claims are deliberately separate from results. A measured result can still have a narrow
scope or a confound. `supported` therefore requires an existing experiment path,
`measured` or `estimated` evidence, and `human_reviewed: yes`.

See the complete project under
[`examples/research/demo-vision/`](examples/research/demo-vision/) and the
[Claude Code → Hermes handoff fixture](examples/cross-agent-demo/README.md).

## Meeting feedback

Ask the agent to turn a meeting, review, or colleague observation into a redacted meeting
record. The default visibility is `redacted`; participants should be described by role,
and private transcripts or large artifacts should stay outside the public repository.

Each feedback item has one statement and a source mode: quote, paraphrase, or inference.
Every triaged state records `human_approved: yes`; lint checks that provenance marker and
the state transition, but it cannot authenticate who edited the field. Use commit or PR
review and branch protection when approval identity matters. Accepted feedback must point
to a real task, research artifact, claim, or ADR. Rejected and deferred items require a
reason, while `validated` requires an observed verification result.

See [`feedback/README.md`](feedback/README.md) and the
[example meeting](examples/feedback/meetings/2026-07-28-weekly-review.md).

## Paper library

Ask the agent to start from a few papers and widen the search: references, later citations,
related work, or a keyword search. Each search is a step file — a checkpoint another agent
can continue or branch from. The agent shows the candidates; you pick the numbers. Only
picked papers become library records.

Preprint and published versions are merged and the published venue is shown first. In a
real check, the arXiv record of one paper had no references and 14 citations while its
published version had 46 references and 400 — so a preprint-only seed is joined with its
published version by exact title. Retracted papers are excluded by default and counted.
A library paper never counts as experiment evidence for a claim.

Metadata comes from [OpenAlex](https://openalex.org). Its reference lists miss entries, so a
references step also asks Crossref and Semantic Scholar and adds what they name; each candidate
records which list found it. Everything works without keys on small budgets; free keys in
`OPENALEX_API_KEY` and `SEMANTIC_SCHOLAR_API_KEY` raise them. See
[`library/README.md`](library/README.md).

## Layout

```text
system/       operating rules, current context, session handoffs, ADRs
research/     questions, experiments, evidence, and claims by project
library/      chosen papers, collections, and exploration trails
feedback/     redacted meeting records and human-triaged feedback
tasks/        backlog / doing / done
specs/        implementation specifications
inbox/        captured ideas not yet planned
knowledge/    reusable lessons
skills/       agent skills, including the claim-validity checklist
examples/     complete fixtures, never live state
infra/        generators, research lint, tests, and Git hook
personal/     empty compatibility extension point
```

The live task, session, research-project, and meeting areas ship empty. Examples are kept
outside the live tree and are exercised by regression tests.

`system/RULES.md` is the single source of operating rules. Agent entry files are thin
stubs pointing to it, so every supported platform gets the same startup contract.

## Included

- Git-native question, experiment, evidence, and claim records
- Human-review provenance fields for supported claims and meeting feedback
- A claim-validity checklist (`skills/experiment-claim-check`) for the layer lint cannot
  reach: leakage, unequal tuning budgets, boundary-pinned sweeps, untested deltas —
  operational failure modes plus standard checks sourced from the reproducibility literature
- Redacted-by-default meeting capture with accept/reject/defer/validate states
- A paper library with resumable exploration trails, version merging, retraction filtering,
  and BibTeX export
- Cross-agent task and session handoffs
- Claude Code, Hermes, Codex CLI, Orca, Gemini, and Copilot entry points
- Generators for tasks, sessions, experiments, and meetings
- `research-lint` in pre-commit and GitHub Actions
- A tested cross-agent demonstration fixture

## Not included

- Personal schedules or personal idea management
- Raw transcript, participant, or private dataset storage
- Large artifact or model-weight storage
- Experiment execution, model routing, or evaluation infrastructure
- External calendar, issue tracker, or lab-system synchronization
- Automatic truth or quality judgments by an AI

These boundaries are intentional. `personal/` remains an empty compatibility point;
research work and feedback provenance are the product.

## Platform compatibility

The repository contract and installed CLI behavior have been checked for Claude Code,
Hermes, Codex CLI, and Orca. This is structural compatibility, not a model-quality
benchmark. See [`docs/platform-compatibility.md`](docs/platform-compatibility.md).

## Validation

Ask the agent to configure the local hook once:

```sh
git config core.hooksPath infra/hooks
```

Run the same checks manually with:

```sh
python infra/research-lint.py
python -m unittest discover -s infra/tests -v
```

GitHub Actions runs both on pushes and pull requests.

## Upstream and license

Shared Brain Research was derived from
[`shared-brain-lite`](https://github.com/realseungju/shared-brain-lite). The imported
revision and owned-file boundary are recorded in [`UPSTREAM.md`](UPSTREAM.md).

MIT — see [LICENSE](LICENSE).
