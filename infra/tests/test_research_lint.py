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

## 연구 질문

baseline보다 나은가.

## 가설

H001

## 계획

세 시드를 비교한다.

## 실행 조건

고정 환경.

## 결과

세 시드 평균 0.81.

## 해석

candidate C001을 검토한다.

## 한계

가상 데이터만 사용했다.

## 다음 단계

- [ ] 외부 데이터 확인
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
title: 주간 리뷰
project: demo-project
visibility: redacted
status: {meeting_status}
---

# 주간 리뷰

## 맥락

연구 진행 검토.

## 출처 요약

역할만 남긴 요약.

## Feedback

### FB-2026-07-28-01

- scope: {scope}
- kind: {kind}
- statement: baseline 비교가 필요하다
- source_mode: paraphrase
- status: {feedback_status}
- human_approved: {approved}
- linked_artifact: {linked_artifact}
- reason: {reason}
- validation: {validation}

## 확정된 결정

없음.

## 후속 링크

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
title: 후속 확인
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
        self.assertIn("필수 파일 없음", result.stdout)
        self.assertIn("필수 디렉터리 없음", result.stdout)

    def test_closed_experiment_requires_reproducibility_fields(self) -> None:
        self.add_experiment(experiment_body(dataset_version="TBD", artifact="TBD"))
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("재현 필드 미완 'dataset_version'", result.stdout)
        self.assertIn("재현 필드 미완 'artifact'", result.stdout)

    def test_closed_experiment_requires_real_commit_reference(self) -> None:
        self.add_experiment(experiment_body(code_commit="latest"))
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("code_commit 형식 불량", result.stdout)

    def test_valid_closed_experiment_passes(self) -> None:
        self.add_experiment()
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_closed_experiment_rejects_scaffold_only_sections(self) -> None:
        body = experiment_body()
        body = body.replace(
            "세 시드 평균 0.81.",
            "| 조건 | 지표 | 값 | N |\n|---|---|---|---|",
        )
        body = body.replace(
            "candidate C001을 검토한다.",
            "- claim candidate:\n- 근거 종류:\n- 이 결과로 말할 수 없는 것:",
        )
        body = body.replace(
            "가상 데이터만 사용했다.",
            "- 미확인 교란:\n- 일반화할 수 없는 범위:",
        )
        self.add_experiment(body)

        result = self.lint()

        self.assertEqual(result.returncode, 1)
        for section in ("결과", "해석", "한계"):
            self.assertIn(f"닫힌 experiment 내용 없음 '{section}'", result.stdout)

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
        for section in ("결과", "해석", "한계"):
            self.assertIn(f"닫힌 experiment 내용 없음 '{section}'", result.stdout)

    def test_supported_claim_rejects_unverified_evidence(self) -> None:
        experiment = self.add_experiment()
        write(
            self.project / "claims.md",
            f"""# Claims

## C001

- statement: baseline보다 우수하다
- status: supported
- evidence: {experiment.relative_to(self.root).as_posix()}
- evidence_kind: unverified
- human_reviewed: yes
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("근거가 unverified", result.stdout)

    def test_supported_claim_rejects_empty_evidence_kind(self) -> None:
        experiment = self.add_experiment()
        write(
            self.project / "claims.md",
            f"""# Claims

## C001

- statement: baseline보다 우수하다
- status: supported
- evidence: {experiment.relative_to(self.root).as_posix()}
- evidence_kind:
- human_reviewed: yes
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("claim 필수 필드 없음 'evidence_kind'", result.stdout)

    def test_supported_claim_requires_human_review(self) -> None:
        experiment = self.add_experiment()
        write(
            self.project / "claims.md",
            f"""# Claims

## C001

- statement: baseline보다 우수하다
- status: supported
- evidence: {experiment.relative_to(self.root).as_posix()}
- evidence_kind: measured
- human_reviewed: no
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("사람 검토 없음", result.stdout)

    def test_supported_claim_requires_project_experiment(self) -> None:
        write(
            self.project / "claims.md",
            """# Claims

## C001

- statement: baseline보다 우수하다
- status: supported
- evidence: UPSTREAM.md
- evidence_kind: measured
- human_reviewed: yes
- reason:
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("project experiment 밖", result.stdout)

    def test_accepted_feedback_requires_human_approval(self) -> None:
        self.add_follow_up_task()
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(approved="no"),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("사람 승인 없음", result.stdout)

    def test_feedback_rejects_empty_core_field(self) -> None:
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(scope="", feedback_status="captured", approved="no", linked_artifact=""),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("feedback 필수 필드 없음 'scope'", result.stdout)

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
                self.assertIn(f"{status} feedback 이유 없음", result.stdout)

    def test_feedback_reason_does_not_use_validation_field(self) -> None:
        for status in ("rejected", "deferred"):
            with self.subTest(status=status):
                write(
                    self.root / "feedback/meetings/2026-07-28-review.md",
                    meeting_body(
                        feedback_status=status,
                        linked_artifact="",
                        reason="사람이 분류한 이유",
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
        self.assertIn("연결 산출물 없음", result.stdout)

    def test_decision_candidate_requires_adr_link(self) -> None:
        self.add_follow_up_task()
        write(
            self.root / "feedback/meetings/2026-07-28-review.md",
            meeting_body(kind="decision-candidate"),
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ADR을 가리키지 않음", result.stdout)

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
        self.assertIn("검증 결과 없음", result.stdout)

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
                        reason="추가 근거 대기" if status == "deferred" else "",
                        meeting_status="closed",
                    ),
                )
                result = self.lint()
                self.assertEqual(result.returncode, 1)
                self.assertIn("closed meeting에 미종결", result.stdout)

    def test_closed_meeting_accepts_terminal_feedback(self) -> None:
        self.add_follow_up_task()
        cases = (
            {
                "feedback_status": "rejected",
                "linked_artifact": "",
                "reason": "범위 밖 요청",
            },
            {
                "feedback_status": "validated",
                "linked_artifact": "tasks/backlog/T2026-07-28-follow-up.md",
                "validation": "재현 확인",
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
