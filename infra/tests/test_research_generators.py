from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from support import make_brain, make_research_project, run_script


class ResearchGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)
        make_research_project(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_new_experiment_creates_date_slug_file(self) -> None:
        result = run_script(
            "new-experiment.py",
            "baseline",
            "--project",
            "demo-project",
            "--title",
            "첫 baseline",
            "--hypothesis",
            "H001",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "research/demo-project/experiments/E2026-07-28-baseline.md"
        self.assertTrue(path.is_file())
        self.assertIn("evidence_kind: unverified", path.read_text(encoding="utf-8"))

    def test_new_experiment_requires_project_overview(self) -> None:
        result = run_script(
            "new-experiment.py",
            "baseline",
            "--project",
            "missing-project",
            "--title",
            "실패",
            "--hypothesis",
            "H001",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("overview 없음", result.stderr)

    def test_new_experiment_rejects_bad_slug(self) -> None:
        result = run_script(
            "new-experiment.py",
            "Bad Slug",
            "--project",
            "demo-project",
            "--title",
            "실패",
            "--hypothesis",
            "H001",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 2)

    def test_new_experiment_output_passes_research_lint(self) -> None:
        run_script(
            "new-experiment.py",
            "lintable",
            "--project",
            "demo-project",
            "--title",
            "lint 통과",
            "--hypothesis",
            "H001",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        result = run_script("research-lint.py", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_new_meeting_defaults_to_redacted(self) -> None:
        result = run_script(
            "new-meeting.py",
            "weekly-review",
            "--title",
            "주간 리뷰",
            "--project",
            "demo-project",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "feedback/meetings/2026-07-28-weekly-review.md"
        self.assertIn("visibility: redacted", path.read_text(encoding="utf-8"))

    def test_new_meeting_output_passes_research_lint(self) -> None:
        run_script(
            "new-meeting.py",
            "lintable",
            "--title",
            "lint 통과",
            "--project",
            "demo-project",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        result = run_script("research-lint.py", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_new_meeting_rejects_duplicate(self) -> None:
        for _ in range(2):
            result = run_script(
                "new-meeting.py",
                "duplicate",
                "--title",
                "중복",
                "--project",
                "demo-project",
                "--date",
                "2026-07-28",
                "--root",
                str(self.root),
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("이미 존재", result.stderr)


if __name__ == "__main__":
    unittest.main()
