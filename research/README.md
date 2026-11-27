# Research

Questions, experiments, evidence, and claims, per project. This is **Tier 2**: it is not read
during the start procedure, and is opened only when the current task or a session hook points at
it.

## Project layout

```text
research/
  _template/
  {project-slug}/
    overview.md
    questions.md
    claims.md
    experiments/
      EYYYY-MM-DD-{slug}.md
```

To start a new project, ask the AI to set it up. It copies `overview.md`, `questions.md`, and
`claims.md` from `_template/`, creates `experiments/`, and replaces the project slug and the
placeholders.

## Evidence flow

```text
Q001 question
→ H001 hypothesis
→ EYYYY-MM-DD-slug experiment
→ C001 claim candidate
→ human review
→ supported / rejected
```

- Keep `overview.md` short: the current state and links to the canonical files.
- `questions.md` holds each question, why it matters, the hypotheses it links to, and the answer
  with its evidence.
- `experiments/` holds the hypothesis and falsification condition written before the run, together
  with the results, interpretation, and limits written after it.
- `claims.md` holds only claims to be reviewed on the strength of results. A results file is not
  itself a supported claim.

## Experiment rules

Create a new experiment with the generator.

```sh
python infra/new-experiment.py baseline \
  --project my-project \
  --title "Baseline" \
  --hypothesis H001
```

`planned | running` are open states. To close as `completed | negative-result | invalidated`:

- Remove the `TBD` from `dataset_version`, `code_commit`, `seed_or_repeats`, and `artifact`
- Change `evidence_kind` to `measured` or `estimated`
- Write `## Results`, `## Interpretation`, and `## Limits`
- Keep results apart from interpretation, and state what this result cannot tell you

Raw data, model weights, large outputs, and secrets do not go into Git. Record only where they
live outside the repo and how to regenerate them.

## Claim rules

`supported` needs all three of these:

1. An experiment path that really exists in the same project
2. `evidence_kind: measured | estimated`
3. `human_reviewed: yes`

The AI may draft a claim candidate and link its evidence, but it does not approve it as
supported on a person's behalf. The exact frontmatter and item schema are in
`system/conventions.md`.

Apply `skills/experiment-claim-check` before raising a claim to `supported` and before closing an
experiment. Lint checks only that evidence **exists**, not that it is **valid** — a sweep pinned
to its boundary, a model read only through argmax, a "ceiling" nobody re-measured, or a "+N pt"
with no test all pass with every field filled in (ADR-007).

## How this relates to tasks, sessions, and feedback

- `tasks/` is what to do, `research/` is the questions and what was learned, and
  `system/sessions/` is the handoff record.
- Running an experiment is a task; the experiment's conditions and results are the experiment
  file; a conclusion that passed human review is a claim.
- Meeting sources live in `feedback/meetings/`, and accepted items point at the real task or
  research document.
- Only lessons reusable beyond one project go up to `knowledge/`.

For a finished example, see `examples/research/demo-vision/`; for a cross-AI handoff, see
`examples/cross-agent-demo/README.md`.
