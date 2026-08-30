from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from support import REPO, make_brain, make_research_project, run_script, write


def experiment_body(
    *,
    status: str = "completed",
    evidence_kind: str = "measured",
    dataset_version: str = "demo-v1",
    code_commit: str = "abc1234",
    seed_or_repeats: str = "seeds-1-3",
    artifact: str = "external/demo/result.json",
) -> str:
    return f"""---
id: E2026-07-28-baseline
title: baseline
project: demo-project
date: 2026-07-28
status: {status}
hypothesis: H001
evidence_kind: {evidence_kind}
dataset_version: {dataset_version}
code_commit: {code_commit}
seed_or_repeats: {seed_or_repeats}
artifact: {artifact}
---

# baseline

## Research question

Does it beat the baseline?

## Hypothesis

H001

## Plan

Compare three seeds.

## Run conditions

Pinned environment.

## Results

Mean of three seeds: 0.81.

## Interpretation

Review candidate C001.

## Limits

Invented data only.

## Next

- [ ] Check against external data
"""


def meeting_body(
    *,
    scope: str = "research",
    kind: str = "problem",
    feedback_status: str = "accepted",
    approved: str = "yes",
    linked_artifact: str = "tasks/backlog/T2026-07-28-follow-up.md",
    reason: str = "",
    validation: str = "",
    meeting_status: str = "triaged",
) -> str:
    return f"""---
date: 2026-07-28
title: Weekly review
project: demo-project
visibility: redacted
status: {meeting_status}
---

# Weekly review

## Context

Review of research progress.

## Source summary

Summary with roles only.

## Feedback

### FB-2026-07-28-01

- scope: {scope}
- kind: {kind}
- statement: a baseline comparison is needed
- source_mode: paraphrase
- status: {feedback_status}
- human_approved: {approved}
- linked_artifact: {linked_artifact}
- reason: {reason}
- validation: {validation}

## Decisions

None.

## Follow-ups

- {linked_artifact}
"""


class ResearchLintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)
        self.project = make_research_project(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def lint(self):
        return run_script("research-lint.py", str(self.root))

    def add_experiment(self, body: str | None = None) -> Path:
        path = self.project / "experiments/E2026-07-28-baseline.md"
        write(path, body or experiment_body())
        return path

    def add_follow_up_task(self) -> Path:
        path = self.root / "tasks/backlog/T2026-07-28-follow-up.md"
        write(
            path,
            """---
id: T2026-07-28-follow-up
title: Follow-up check
phase: planning
---
""",
        )
        return path

    def test_minimal_research_brain_is_clean(self) -> None:
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_requires_claims_and_experiments(self) -> None:
        (self.project / "claims.md").unlink()
        (self.project / "experiments").rmdir()
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("required research project file missing", result.stdout)
        self.assertIn("required research project directory missing", result.stdout)

    def test_closed_experiment_requires_reproducibility_fields(self) -> None:
        self.add_experiment(experiment_body(dataset_version="TBD", artifact="TBD"))
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing a reproducibility field 'dataset_version'", result.stdout)
        self.assertIn("missing a reproducibility field 'artifact'", result.stdout)

    def test_closed_experiment_requires_real_commit_reference(self) -> None:
        self.add_experiment(experiment_body(code_commit="latest"))
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid code_commit", result.stdout)

    def test_valid_closed_experiment_passes(self) -> None:
        self.add_experiment()
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_closed_experiment_rejects_scaffold_only_sections(self) -> None:
        body = experiment_body()
        body = body.replace(
            "Mean of three seeds: 0.81.",
            "| Arm | Metric | Value | N |\n|---|---|---|---|",
        )
        body = body.replace(
            "Review candidate C001.",
            "- claim candidate:\n- Evidence kind:\n- What this result cannot say:",
        )
        body = body.replace(
            "Invented data only.",
            "- Unchecked confounds:\n- Where this does not generalise:",
        )
        self.add_experiment(body)

        result = self.lint()

        self.assertEqual(result.returncode, 1)
        for section in ("Results", "Interpretation", "Limits"):
            self.assertIn(f"closed experiment section is empty '{section}'", result.stdout)

    def test_experiment_template_cannot_close_without_content(self) -> None:
        body = (REPO / "research/_template/experiment.md").read_text(encoding="utf-8")
        replacements = {
            "id: EYYYY-MM-DD-slug": "id: E2026-07-28-baseline",
            "project: project-slug": "project: demo-project",
            "date: YYYY-MM-DD": "date: 2026-07-28",
            "status: planned": "status: completed",
            "evidence_kind: unverified": "evidence_kind: measured",
            "dataset_version: TBD": "dataset_version: demo-v1",
            "code_commit: TBD": "code_commit: abc1234",
            "seed_or_repeats: TBD": "seed_or_repeats: seeds-1-3",
            "artifact: TBD": "artifact: external/demo/result.json",
        }
        for old, new in replacements.items():
            body = body.replace(old, new)
        self.add_experiment(body)

        result = self.lint()

        self.assertEqual(result.returncode, 1)
        for section in ("Results", "Interpretation", "Limits"):
            self.assertIn(f"closed experiment section is empty '{section}'", result.stdout)

    def test_supported_claim_rejects_unverified_evidence(self) -> None:
        experiment = self.add_experiment()
        write(
            self.project / "claims.md",
            f"""# Claims

## C001

- statement: it beats the baseline
- status: supported
- evidence: {experiment.relative_to(self.root).as_posix()}
- evidence_kind: unverified
- human_reviewed: yes
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("rests on unverified evidence", result.stdout)

    def test_supported_claim_rejects_empty_evidence_kind(self) -> None:
        experiment = self.add_experiment()
        write(
            self.project / "claims.md",
            f"""# Claims

## C001

- statement: it beats the baseline
- status: supported
- evidence: {experiment.relative_to(self.root).as_posix()}
- evidence_kind:
- human_reviewed: yes
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("claim field missing 'evidence_kind'", result.stdout)

    def test_supported_claim_requires_human_review(self) -> None:
        experiment = self.add_experiment()
        write(
            self.project / "claims.md",
            f"""# Claims

## C001

- statement: it beats the baseline
- status: supported
- evidence: {experiment.relative_to(self.root).as_posix()}
- evidence_kind: measured
- human_reviewed: no
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("has no human review", result.stdout)

    def test_supported_claim_requires_project_experiment(self) -> None:
        write(
            self.project / "claims.md",
            """# Claims

## C001

- statement: it beats the baseline
- status: supported
- evidence: UPSTREAM.md
- evidence_kind: measured
- human_reviewed: yes
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("points outside the project experiments", result.stdout)

    def test_accepted_feedback_requires_human_approval(self) -> None:
        self.add_follow_up_task()
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(approved="no"),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("has no human approval", result.stdout)

    def test_feedback_rejects_empty_core_field(self) -> None:
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(scope="", feedback_status="captured", approved="no", linked_artifact=""),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("feedback field missing 'scope'", result.stdout)

    def test_rejected_and_deferred_feedback_require_reason(self) -> None:
        for status in ("rejected", "deferred"):
            with self.subTest(status=status):
                write(
                    self.root / "feedback/meetings/2026-07-28-review.md",
                    meeting_body(
                        feedback_status=status,
                        linked_artifact="",
                        reason="",
                    ),
                )
                result = self.lint()
                self.assertEqual(result.returncode, 1)
                self.assertIn("feedback has no reason", result.stdout)

    def test_feedback_reason_does_not_use_validation_field(self) -> None:
        for status in ("rejected", "deferred"):
            with self.subTest(status=status):
                write(
                    self.root / "feedback/meetings/2026-07-28-review.md",
                    meeting_body(
                        feedback_status=status,
                        linked_artifact="",
                        reason="reason recorded by a human",
                        validation="",
                    ),
                )
                result = self.lint()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepted_feedback_requires_existing_artifact(self) -> None:
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(linked_artifact="tasks/backlog/T2026-07-28-missing.md"),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("links to no artifact", result.stdout)

    def test_decision_candidate_requires_adr_link(self) -> None:
        self.add_follow_up_task()
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(kind="decision-candidate"),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not point at an ADR", result.stdout)

    def test_valid_accepted_feedback_passes(self) -> None:
        self.add_follow_up_task()
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validated_feedback_requires_validation_result(self) -> None:
        self.add_follow_up_task()
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(feedback_status="validated"),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("has no validation result", result.stdout)

    def test_closed_meeting_rejects_unfinished_feedback(self) -> None:
        self.add_follow_up_task()
        for status in ("captured", "accepted", "deferred"):
            with self.subTest(status=status):
                write(
                    self.root / "feedback/meetings/2026-07-28-review.md",
                    meeting_body(
                        feedback_status=status,
                        approved="no" if status == "captured" else "yes",
                        linked_artifact=(
                            "tasks/backlog/T2026-07-28-follow-up.md"
                            if status == "accepted"
                            else ""
                        ),
                        reason="waiting on more evidence" if status == "deferred" else "",
                        meeting_status="closed",
                    ),
                )
                result = self.lint()
                self.assertEqual(result.returncode, 1)
                self.assertIn("closed meeting still has unfinished feedback", result.stdout)

    def test_closed_meeting_accepts_terminal_feedback(self) -> None:
        self.add_follow_up_task()
        cases = (
            {
                "feedback_status": "rejected",
                "linked_artifact": "",
                "reason": "out of scope",
            },
            {
                "feedback_status": "validated",
                "linked_artifact": "tasks/backlog/T2026-07-28-follow-up.md",
                "validation": "reproduction confirmed",
            },
        )
        for fields in cases:
            with self.subTest(status=fields["feedback_status"]):
                write(
                    self.root / "feedback/meetings/2026-07-28-review.md",
                    meeting_body(meeting_status="closed", **fields),
                )
                result = self.lint()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
