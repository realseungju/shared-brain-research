---
id: E2026-07-28-color-baseline
title: Colour-classification baseline
project: demo-vision
date: 2026-07-28
status: completed
hypothesis: H001
evidence_kind: measured
dataset_version: demo-v1
code_commit: 1a2b3c4
seed_or_repeats: seeds-1-3
artifact: external/demo/color-baseline.json
---

# Colour-classification baseline

## Research question

On `demo-v1`, does the baseline beat chance?

## Hypothesis

- Linked hypothesis: `H001`
- Expectation: mean Macro-F1 above 0.50.
- **Falsified if:** the three-seed mean is 0.50 or below.

## Plan

- Comparison: identical settings, seeds 1, 2, 3
- Primary metric: Macro-F1
- baseline: 0.50
- Decision rule: mean of three seeds

## Run conditions

| Field | Value |
|---|---|
| Code commit | `1a2b3c4` |
| Dataset and version | `demo-v1` |
| Model and version pin | `demo-classifier-1.0` |
| Seeds and repeats | `seeds-1-3` |
| Hardware | invented example |
| artifact | `external/demo/color-baseline.json` |

## Run log

- 2026-07-28 - recorded an invented three-seed result

## Results

| Arm | Metric | Value | N |
|---|---|---|---|
| baseline | Macro-F1 | 0.81 mean | 3 seeds |

## Interpretation

- claim candidate: C001
- Evidence kind: `measured`
- What this result cannot say: anything beyond `demo-v1`

## Limits

- An invented fixture. It does not represent real model performance.
- No statistical test was run.

## Next

- [ ] Repeat on a different invented distribution
