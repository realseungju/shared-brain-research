---
project: demo-vision
status: active
canon: research/demo-vision/overview.md
updated: 2026-07-28
---

# Demo Vision

## In one line

An invented colour-classification baseline, used to show research provenance and a
cross-agent handoff.

## Research question

On a pinned `demo-v1`, does the baseline beat chance?

## Success criteria

- Primary metric: Macro-F1
- baseline: chance at 0.50
- Unit of judgement: mean of three seeds

## Where this stands

| Item | Status | Evidence |
|---|---|---|
| Question Q001 | answered | `questions.md` |
| Experiment | completed | `experiments/E2026-07-28-color-baseline.md` |
| Claim C001 | supported | `claims.md` |

## Method

Repeat identical settings over three seeds on an invented dataset that contains no personal
data.

## Evidence so far

- The three-seed mean on `demo-v1` is 0.81 - measured, linked to the experiment.

## Next

- [ ] Revalidate on a different invented distribution

## Related documents

- `questions.md`
- `claims.md`
- `experiments/E2026-07-28-color-baseline.md`
