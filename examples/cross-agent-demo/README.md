# Claude Code → Hermes handoff demo

This fixture is not a model performance benchmark. It reproduces **whether the repository
contract makes a handoff possible**.

## Turn 1 — Claude Code

1. Start at the repository root and read `CLAUDE.md` → Tier 0.
2. Record Q001, H001, and the plan for the baseline experiment.
3. Leave the path the next agent should open in the session hook.

Example: `examples/sessions/2026-07-28-claude-baseline-plan.md`

## Turn 2 — Hermes

1. Open the same repository as the working directory; Hermes reads `AGENTS.md`.
2. Through the latest session hook in Tier 0 and the doing task, it opens only the experiment in
   addition.
3. It records results, limits, and a claim candidate, and after human review changes the claim to
   supported.

Example: `examples/sessions/2026-07-28-hermes-baseline-result.md`

## Feedback link

Meeting item FB-01 is linked to a task after human approval. FB-02 is rejected, FB-03 is
deferred. The next AI does not read the whole meeting as Tier 0; it traces back from the
accepted task to the source.

## Reproduce

The regression test copies the examples' research, meeting, task, and session files into the
live locations of an empty brain, then runs `research-lint`.

```sh
python -m unittest infra.tests.test_examples -v
```
