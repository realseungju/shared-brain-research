---
name: experiment-claim-check
description: >-
  Fires **just before an experimental number is written down as a claim** — in a claim, an
  experiment's conclusion, or a session summary. Separates a property of the subject from a
  limit of the measuring instrument: a sweep pinned to its boundary, a model read only through
  argmax, a "ceiling" nobody re-measured, a "+N pt" with no test. Do not fire for routine
  bookkeeping or typo fixes.
---

# experiment-claim-check — a measurement check before recording

한국어 번역: [`SKILL.ko.md`](SKILL.ko.md)

> This skill runs no code. It is a gate placed **just before an experimental number hardens
> into a claim**. `research-lint` checks that evidence *exists* (a path, the fields, a human
> review) but cannot see whether the evidence is *valid*. A check by a person and an AI fills
> that layer.

## Why it is needed

A limit of the measuring instrument passes itself off as a property of the subject. Once it is
in a document, **nobody measures it again** — it has become "something we already know". One
wrong number becomes the central claim, several rounds of follow-up design are stacked on it,
and only then does it turn out that a single threshold was the cause. This really happens.

**People fall into this trap even when they know it.** There is a record of someone who found
this trap and warned about it reproducing the same grid bug twenty minutes later. So it has to
be **a checklist with fixed trigger points**, not a matter of discipline.

> **Where the items come from.** Group A (1–6) generalizes failures observed repeatedly while
> running the parent brain — the concrete cases are unpublished research and are not copied
> here. A list drawn from one project's experience leans toward the traps that project hit, so
> group B (7–10) fills in with standard checks from the reproducibility literature. Each item's
> source is linked in the references below.

## When it fires

The points where it meshes with this repository's gates:

- Changing a claim in `research/{project}/claims.md` to `supported`
- Closing an experiment as `completed` or `negative-result` and writing `## Interpretation`
- Moving a number into a session summary or `system/context.md` as a conclusion
- Group B checks design and analysis before the number exists. If they were not confirmed by
  the time of recording, stop and go back to the design or analysis step.

In particular, when you are about to write a sentence of one of these shapes — **each one is a
stop sign**:

- "X is the ceiling / the limit / the upper bound"
- "A beats B by N pt"
- "X is meaningless / has no effect / is the bottleneck"
- "This approach does not work"

## Group A — reading the number (just before recording, quickly)

**1. Is the sweep pinned to a boundary?**
If the optimum sits at the first or last point of the grid, **suspect the grid before the
subject**. Repeated pinning is a strong signal to re-measure, but the true optimum can lie at
the edge of the allowed range, so pinning alone is not proof of a defect. → Widen the range and
re-measure, or record why the boundary is valid by definition along with a control condition.

**2. Was the model read only through argmax?**
Measure a ranking metric (AUC) and a threshold-dependent metric (F1) **together**. If they
diverge sharply, first check whether the **threshold** is broken rather than the skill. On
other data, class imbalance or distribution shift can also be the cause, so hold off on a
capability conclusion until the readout is re-measured. If the probabilities bunch up on one
side, pick threshold candidates from quantiles **on dev only** and confirm on an untouched eval
set.

**3. Was the "limit" or "ceiling" actually measured?**
If not, write **"not measured (current best = X)"**. Do not write "ceiling". Promoting the best
score of the moment to a ceiling is the standard path of this failure.

**4. Was the difference tested?**
Claiming "+N pt better" needs an uncertainty estimate that fits the comparison design. If both
systems predicted the same instances, a paired method such as the **paired bootstrap**
preserves the covariance between predictions and can be more precise than an independent
analysis. Match the resampling unit to the independent unit of the data (subject, group, and
so on). If the CI contains 0, do not claim a **directional advantage** at that confidence
level. The estimate and CI can be reported as "inconclusive"; do not turn that into evidence of
"no effect". **CI width differs between comparisons** — do not borrow one comparison's width
for another.

**5. Is the part read correctly before you compensate for it?**
Before designing "add Y to make up for weak part X", check **whether X is being read
correctly**. To measure Y's contribution, the baseline has to be "X alone, read correctly".
With a broken X as the baseline, Y's contribution is inflated.

**6. Did a hedge get dropped?**
When the source says "may be" and the citation says "is", **a testable hypothesis becomes an
untestable premise**. Carry the hedge along when you cite.

## Group B — before the number exists (at design and analysis time)

Even if everything in group A passes, a hole here means the number cannot answer the question.
At recording time, confirm each check was actually performed; if it was not, do not write the
conclusion.

**7. Is there leakage?**
Reproducibility failures from leakage have been documented across 17 fields and hundreds of
papers. For a quick gate, look at three bundles:

- Was the **train/test split** kept through the **whole pipeline** — preprocessing,
  normalization, feature selection, augmentation, hyperparameter search? Augmenting before the
  split puts variants of one original on both sides.
- Did **illegitimate features** slip in — information that cannot exist at prediction time, or
  proxies for the outcome?
- **Are the evaluation samples independent and representative of the distribution you care
  about?** Check for time reversal, the same subject or original on both sides of the split,
  and source or sampling bias.

Kapoor & Narayanan's detailed taxonomy has eight types. The three bundles above are a
regrouping for a 30-second gate, not a copy of the original taxonomy. The published version
surveyed 294 papers; the latest arXiv version surveys 329.

**8. Is the tuning budget comparison fair?**
State each method's search trials, time, and compute, and decide which budget to match before
comparing. The same number of trials is not the same compute, and mechanically giving every
method the same number does not guarantee fairness either. Where possible, report **performance
as a function of budget**. If only your model was tuned thoroughly and the baseline ran on
defaults, do not attribute the observed difference to the method itself.

**9. Did you look many times and keep only the best?**
Scanning several settings, metrics, seeds, or thresholds and reporting the best one creates
selection bias. For confirmatory claims, use a **multiple-comparison correction** that covers
the whole comparison set, or an independent check on untouched data. Avoid **sequential
overfitting** — reusing the same test set to pick the next setting — and keep the final
evaluation data apart.

**10. Were the important sources of variance included?**
Variation from changing only the seed is uncertainty conditional on a fixed split and search
procedure. Identify which sources could affect the conclusion — data split, initialization,
data order, augmentation, hyperparameter selection — and vary them. This does not mean every
combination must be run. State what you held fixed, and do not use a single-seed "+N pt" as
evidence of a general advantage.

## A guard to put in code (copy into sweeps that expect an interior optimum)

```python
def assert_interior(best, grid, name="tau"):
    """Do not let a sweep optimum on the boundary pass silently without re-measurement or justification."""
    lo, hi = float(min(grid)), float(max(grid))
    if best <= lo or best >= hi:
        raise ValueError(
            f"{name}={best} is pinned to the grid boundary [{lo}, {hi}]. "
            f"This may be a limit of the grid, not a property of the subject — widen the range and re-measure."
        )
```

**This guard is the real automatic check.** Do not copy it blindly into problems where a
boundary solution is valid by definition, such as a mixing weight of 0 or 1. For those sweeps,
state that the boundary may be the conclusion and confirm it with a suitable control
condition. This repository does not run experiments, so `research-lint` cannot catch it — the
guard belongs in the **project code** where the sweep runs.

## How to record after passing

Copy the check result into this repository's fields as is. Do not blur it into prose.

| Check result | `evidence_kind` | How to write it |
|---|---|---|
| Measured and tested | `measured` | `n=1086, 20 seed, +0.093 ± 0.013 (paired bootstrap)` |
| Observed but not tested | `measured`, with "not tested" stated under `## Limits` | `observed +0.021, not tested` |
| Upper bound or extrapolation not measured | `estimated` | `current best 0.59; ceiling not measured` |
| No evidence yet | `unverified` | Keep the claim as `candidate` |

- An experiment cannot be closed, and a claim cannot be raised to `supported`, while it is
  `unverified` — `research-lint` rejects it.
- Do not delete the items a check caught; leave them under the experiment's `## Limits`. The
  point of this record is that the next person does not fall into the same trap.

## Forbidden

- Recording "ceiling, limit, meaningless, +N pt" as a conclusion without the check
- Using a directional difference with no uncertainty estimate as evidence for a `supported` claim
- Adopting a boundary-pinned sweep result without re-measurement or a justification of the boundary
- Settling "no effect" because the CI contains 0
- Attributing a difference from a baseline with an incomparable tuning budget to the method
- Dropping the original source's hedge while citing it

## References — the sources for group B

| What | Where |
|---|---|
| Eight-type leakage taxonomy and its prevalence across 17 fields (item 7) | [Kapoor & Narayanan, *Leakage and the Reproducibility Crisis in ML-based Science*](https://arxiv.org/abs/2207.07048) ([published in Patterns](https://www.cell.com/patterns/fulltext/S2666-3899(23)00159-9)) |
| Augmenting before the split, sequential overfitting, multiple comparisons, baselines (items 7 and 9) | [Lones, *How to avoid machine learning pitfalls*](https://arxiv.org/abs/2108.02497) |
| Conclusions flip with budget; report as a function of budget (item 8) | [Dodge et al., *Show Your Work*](https://aclanthology.org/D19-1224/) |
| Sources of variance such as split, initialization, hyperparameters (item 10) | [Bouthillier et al., *Accounting for Variance in ML Benchmarks*](https://arxiv.org/abs/2103.03098) |
| 32-item reporting standard for ML-based science | [REFORMS](https://www.science.org/doi/10.1126/sciadv.adk3452) |

REFORMS is a standard covering study design, implementation, and reporting as a whole; this
skill is a quick gate at the point where a number becomes a claim. Apply REFORMS separately at
the paper-writing stage.
