from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from support import make_brain, run_script


class GeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_new_task_creates_date_slug_task(self) -> None:
        result = run_script(
            "new-task.py",
            "first-task",
            "--title",
            "First task",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "tasks/backlog/T2026-07-28-first-task.md"
        self.assertTrue(path.is_file())
        self.assertIn("title: First task", path.read_text(encoding="utf-8"))

    def test_new_task_rejects_invalid_slug(self) -> None:
        result = run_script(
            "new-task.py",
            "Bad Slug",
            "--title",
            "Failure",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 2)

    def test_new_task_rejects_duplicate(self) -> None:
        for _ in range(2):
            result = run_script(
                "new-task.py",
                "dup-task",
                "--title",
                "Duplicate",
                "--date",
                "2026-07-28",
                "--root",
                str(self.root),
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("already exists", result.stderr)

    def test_new_task_output_passes_lint(self) -> None:
        run_script(
            "new-task.py",
            "lintable",
            "--title",
            "Lint check",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        lint = run_script("brain-lint.py", str(self.root))
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_new_session_rejects_overlong_hook(self) -> None:
        result = run_script(
            "new-session.py",
            "long-hook",
            "--agent",
            "Codex",
            "--tags",
            "demo",
            "--hook",
            "a" * 101,
            "--did",
            "d",
            "--next",
            "n",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 2)

    def test_new_session_rejects_bad_tag(self) -> None:
        result = run_script(
            "new-session.py",
            "bad-tag",
            "--agent",
            "Codex",
            "--tags",
            "Demo Tag",
            "--hook",
            "hook",
            "--did",
            "d",
            "--next",
            "n",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 2)

    def test_new_session_output_passes_lint(self) -> None:
        run_script(
            "new-session.py",
            "lintable-session",
            "--agent",
            "Codex",
            "--tags",
            "demo",
            "--hook",
            "Lint passes",
            "--did",
            "Generator check",
            "--next",
            "None",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        lint = run_script("brain-lint.py", str(self.root))
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_new_session_creates_file_and_index_entry(self) -> None:
        result = run_script(
            "new-session.py",
            "first-session",
            "--agent",
            "Codex",
            "--tags",
            "demo,lite",
            "--hook",
            "First session",
            "--did",
            "Generator check",
            "--next",
            "Next task",
            "--date",
            "2026-07-28",
            "--root",
            str(self.root),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "system/sessions/2026-07-28-first-session.md"
        self.assertTrue(path.is_file())
        index = (self.root / "system/sessions/index.md").read_text(encoding="utf-8")
        self.assertIn(path.name, index)


if __name__ == "__main__":
    unittest.main()
