"""Keep the artifacts in examples/ satisfying the common and research schemas.

lint does not inspect examples/ as live records - that is what lets the live tree ship empty.
So when a schema changes, only the examples rot, silently. Here we drop them into their
real places in an empty repository and run lint to catch that drift.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from support import REPO, make_brain, run_script, write

EXAMPLES = REPO / "examples"


class ExampleArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_examples_directory_is_not_empty(self) -> None:
        self.assertTrue(sorted(EXAMPLES.glob("sessions/*.md")), "no example session")
        self.assertTrue(sorted(EXAMPLES.glob("tasks/*.md")), "no example task")
        self.assertTrue(sorted(EXAMPLES.glob("research/*/overview.md")), "no example research project")
        self.assertTrue(sorted(EXAMPLES.glob("feedback/meetings/*.md")), "no example meeting")
        self.assertTrue(sorted(EXAMPLES.glob("library/trails/*/step-*.md")), "no example library trail")
        self.assertTrue(sorted(EXAMPLES.glob("library/papers/L*.md")), "no example library record")

    def test_examples_pass_lint_in_place(self) -> None:
        index_lines = []
        for path in sorted(EXAMPLES.glob("sessions/*.md")):
            shutil.copy(path, self.root / "system/sessions" / path.name)
            index_lines.append(f"- [{path.stem}]({path.name}) - example")
        write(
            self.root / "system/sessions/index.md",
            "# Sessions Index\n\n" + "\n".join(index_lines) + "\n",
        )
        for path in sorted(EXAMPLES.glob("tasks/*.md")):
            shutil.copy(path, self.root / "tasks/done" / path.name)
        shutil.copytree(EXAMPLES / "research", self.root / "research", dirs_exist_ok=True)
        shutil.copytree(EXAMPLES / "feedback", self.root / "feedback", dirs_exist_ok=True)
        for part in ("trails", "papers", "collections"):
            shutil.copytree(EXAMPLES / "library" / part, self.root / "library" / part, dirs_exist_ok=True)

        result = run_script("research-lint.py", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_live_tree_ships_empty(self) -> None:
        """Shipping state - a template cloner must not inherit someone else's records."""
        sessions = sorted(
            p for p in (REPO / "system/sessions").glob("*.md") if p.name != "index.md"
        )
        self.assertEqual(sessions, [], f"live sessions left behind: {sessions}")
        done = sorted((REPO / "tasks/done").glob("*.md"))
        self.assertEqual(done, [], f"live done tasks left behind: {done}")
        projects = sorted(
            p for p in (REPO / "research").iterdir() if p.is_dir() and not p.name.startswith("_")
        )
        self.assertEqual(projects, [], f"live research projects left behind: {projects}")
        meetings = sorted((REPO / "feedback/meetings").glob("*.md"))
        self.assertEqual(meetings, [], f"live meetings left behind: {meetings}")

    def test_git_tracked_tree_passes_research_lint(self) -> None:
        """Rebuild only what Git actually ships, to catch a missing required empty directory."""
        try:
            tracked = subprocess.run(
                ["git", "-C", str(REPO), "ls-files", "-z"],
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            self.skipTest("no git executable")
        if tracked.returncode != 0:
            self.skipTest("not a git repository")

        shipped = self.root / "shipped"
        for relative in tracked.stdout.decode("utf-8").split("\0"):
            if not relative:
                continue
            source = REPO / relative
            target = shipped / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        result = subprocess.run(
            [sys.executable, str(shipped / "infra/research-lint.py")],
            cwd=shipped,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
