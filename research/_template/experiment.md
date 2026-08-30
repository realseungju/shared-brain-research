---
id: EYYYY-MM-DD-slug
title: Experiment title
project: project-slug
date: YYYY-MM-DD
status: planned
hypothesis: H001
evidence_kind: unverified
dataset_version: TBD
code_commit: TBD
seed_or_repeats: TBD
artifact: TBD
---

# Experiment title

## Research question

What do you want to know is true? One sentence.

## Hypothesis

- Linked hypothesis: `H001`
- Expectation:
- **Falsified if:**

Write the falsification condition before running. Decide it after seeing the result and everything is a success.

## Plan

- Comparison:
- Primary metric:
- baseline:
- Decision rule:

## Run conditions

| Field | Value |
|---|---|
| Code commit | frontmatter `code_commit` |
| Dataset and version | frontmatter `dataset_version` |
| Model and version pin |  |
| Seeds and repeats | frontmatter `seed_or_repeats` |
| Hardware |  |
| artifact | frontmatter `artifact` |

Only what reproduction needs. What cannot be reproduced is an anecdote, not a result.

## Run log

- YYYY-MM-DD - what was run, and what broke

## Results

TODO: add the observed rows.

| Arm | Metric | Value | N |
|---|---|---|---|

## Interpretation

- claim candidate: TODO
- Evidence kind: TODO
- The metric's floor and ceiling, and where this value sits: TODO
- What this result **cannot** say: TODO

## Limits

- Unchecked confounds: TODO
- Where this does not generalise: TODO

## Next

- [ ]
