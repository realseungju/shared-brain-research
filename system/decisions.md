> **English is canonical here.** 한국어 번역본은 없습니다 —
> `system/RULES.ko.md` 와 `system/conventions.ko.md` 가 운영 규칙의 한국어판입니다.

# Decisions

Record an important decision by adding an ADR below, without deleting what is already
there. Reversing a decision is also an addition, not a deletion — why it changed matters as
much as the decision itself.

```markdown
## ADR-000: Decision title
- Date: YYYY-MM-DD
- Status: proposed | accepted | superseded
- Decision:
- Rationale:
- Consequences:
```

---

## ADR-001: research/ ships conventions and templates only, with no automation
- Date: 2026-07-28
- Status: **superseded by ADR-003** for this distribution
- Decision: Ship the `research/{project-slug}/overview.md` layout and an experiment-record
  template. Do not add generators, lint checks, or index automation for them.
- Rationale: Research records differ enormously between projects. Enforcing a structure
  makes people work around it in the projects it does not fit, and once the working around
  starts, trust in every other rule erodes with it.
- Consequences: Inherited from `shared-brain-lite`. This distribution narrows it — see
  ADR-003.

## ADR-002: `personal/` stays empty until it is requested
- Date: 2026-07-28
- Status: **superseded by ADR-004** for this distribution
- Decision: Do not build a structure for personal schedules or idea management.
- Rationale: Personal habits differ from person to person, and a structure nobody uses is
  pure reading cost. It is also a route by which personal data ends up in a public
  repository.
- Consequences: Inherited from `shared-brain-lite`. See ADR-004.

## ADR-003: Only the research provenance core is enforced by generators and lint
- Date: 2026-07-28
- Status: accepted
- Decision: This distribution checks the identifiers, evidence, human-approval provenance,
  and reproducibility fields of experiments, claims, and meeting feedback — through the
  generators and `research-lint`.
- Rationale: The audience is computational and ML researchers. When results blur into
  interpretation, or a remark blurs into a decision, the next AI inherits a wrong claim.
  What is enforced is not a formatting preference; it is the set of fields whose loss
  destroys provenance.
- Consequences: Free-form project documents stay allowed, but a closed experiment, a
  `supported` claim, or `accepted` feedback does not pass the commit gate without its
  minimum evidence.

## ADR-004: personal/ is out of scope for this distribution
- Date: 2026-07-28
- Status: accepted
- Decision: Keep `personal/` as an empty directory for core compatibility, and do not ship
  the opt-in task either.
- Rationale: It blurs the product boundary — research experiments and feedback handoff —
  and raises the risk of personal data in a public repository.
- Consequences: Scheduling and personal ideas belong in another tool, or in a separate
  private extension.

## ADR-005: Promoting feedback requires human approval, and redacted is the default
- Date: 2026-07-28
- Status: accepted
- Decision: A new meeting defaults to `visibility: redacted`. An AI may extract feedback,
  but triaging it to `accepted`, `rejected`, `deferred`, or `validated` requires
  `human_approved: yes`.
- Rationale: What was said in a meeting — and any summary or inference drawn from it — is
  neither a fact nor an agreement. Putting raw sources into public Git leaves personal data
  and confidential research in permanent history.
- Consequences: `accepted` feedback needs a link to a real artifact, and a
  decision-candidate must point at an ADR. Shipping and confirming are separate states.
  `human_approved` does not authenticate who approved — that is established from Git commit
  and PR review history.

## ADR-006: lite is a reference point, not an auto-synced upstream
- Date: 2026-07-28
- Status: accepted
- Decision: Pin the base lite commit and the shared/own file boundary in `UPSTREAM.md`, and
  adopt upstream changes selectively.
- Rationale: Automatic two-way sync either overwrites research-specific rules or blurs the
  two products' scopes back together.
- Consequences: When a common-core change is adopted, the full core and research regression
  suites are run together.

## ADR-007: One claim-validity skill ships with the distribution
- Date: 2026-07-28
- Status: accepted (supersedes the "no real skills shipped" line in `skills/README.md`)
- Decision: Ship `skills/experiment-claim-check` in the default distribution. Every other
  skill remains a user extension point.
- Rationale: `research-lint` checks only that evidence **exists** — a path is present, the
  fields are filled, a human is recorded as having reviewed it. It cannot check whether the
  evidence is **sound**. A sweep that ran into its own boundary, a model read only through
  argmax, a "ceiling" nobody re-measured, a "+N pt" with no test — all of these pass with
  every field filled. For an audience of computational and ML researchers, leaving that
  layer empty makes the provenance contract a formality.
- Consequences: Lint (structure) and the skill (content) form a two-layer gate. The skill
  does not execute, so it has no enforcement — it only fixes the trigger points: promoting
  a claim to `supported`, closing an experiment, moving a number into context. The concrete
  failures behind it come from unpublished research and are generalised into patterns
  rather than copied. A list drawn from one project's operating experience leans toward the
  traps that project hit, so leakage, tuning budget, multiple comparisons, and sources of
  variance are supplemented from standard reproducibility literature, with sources marked
  A/B. It does not replace a full reporting standard such as REFORMS — it stays scoped to a
  gate applied just before something is recorded.

## ADR-008: English is canonical; Korean ships as a sibling translation
- Date: 2026-08-30
- Status: accepted
- Decision: English is canonical for the path an agent and a cloner actually walk — the four
  entry stubs, `system/RULES.md`, `system/conventions.md`, `system/context.md`, this file,
  every `brain-lint` and `research-lint` message, the section headings emitted by all four
  generators, the tests, and `examples/`. Korean is preserved as `system/RULES.ko.md` and
  `system/conventions.ko.md`, each opening with a pointer to the canonical file and the
  commit it was synced from.
- Rationale:
  - Adopted from upstream `shared-brain-lite` ADR-003 through the `UPSTREAM.md` procedure of
    ADR-006, so the two distributions do not diverge on the common core.
  - This is a schema change, not a translation. `new-experiment.py` emitted Korean section
    headings and `research-lint.py` enforced those exact strings; the same coupling ran
    through `new-meeting.py`, `new-session.py`, `new-task.py`, the test assertions, and the
    `demo-vision` example set.
  - The window is now. This repository is private with no external users, so a breaking
    schema change costs nothing today and becomes permanent with one adopter.
- Consequences:
  - Enforced section names changed. Experiments now use `Research question` / `Hypothesis` /
    `Plan` / `Run conditions` / `Results` / `Interpretation` / `Limits` / `Next`; meetings
    use `Context` / `Source summary` / `Feedback` / `Decisions` / `Follow-ups`.
  - Templates under `research/`, `feedback/`, `skills/`, `knowledge/`, `inbox/`, and
    `tasks/`, plus `docs/` and `README.ko.md`, are still Korean. That is a known residue,
    deliberately left for a later pass.
  - Document bodies may be written in any language. Only headings and frontmatter are fixed.
  - The approval-report renderer that upstream built on 2026-08-30 is **not** adopted here.
    It is on a two-week trial in the private brain, and nothing goes into a distribution
    before it survives there.
