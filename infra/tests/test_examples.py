"""examples/ 의 예시 산출물이 공통·research 스키마를 만족하는지 지킨다.

lint 는 examples/ 를 live 기록으로 검사하지 않는다(그래야 live 트리를 비워 배포할 수 있다).
그래서 스키마가 바뀌면 예시만 조용히 낡는다 — 여기서 예시를 빈 저장소의 제자리에
놓고 lint 를 돌려 그 드리프트를 잡는다.
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
        self.assertTrue(sorted(EXAMPLES.glob("sessions/*.md")), "예시 session 이 없다")
        self.assertTrue(sorted(EXAMPLES.glob("tasks/*.md")), "예시 task 가 없다")
        self.assertTrue(sorted(EXAMPLES.glob("research/*/overview.md")), "예시 research 가 없다")
        self.assertTrue(sorted(EXAMPLES.glob("feedback/meetings/*.md")), "예시 meeting 이 없다")

    def test_examples_pass_lint_in_place(self) -> None:
        index_lines = []
        for path in sorted(EXAMPLES.glob("sessions/*.md")):
            shutil.copy(path, self.root / "system/sessions" / path.name)
            index_lines.append(f"- [{path.stem}]({path.name}) — 예시")
        write(
            self.root / "system/sessions/index.md",
            "# Sessions Index\n\n" + "\n".join(index_lines) + "\n",
        )
        for path in sorted(EXAMPLES.glob("tasks/*.md")):
            shutil.copy(path, self.root / "tasks/done" / path.name)
        shutil.copytree(EXAMPLES / "research", self.root / "research", dirs_exist_ok=True)
        shutil.copytree(EXAMPLES / "feedback", self.root / "feedback", dirs_exist_ok=True)

        result = run_script("research-lint.py", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_live_tree_ships_empty(self) -> None:
        """배포 상태 확인 — 템플릿 복제자가 남의 기록을 물려받지 않아야 한다."""
        sessions = sorted(
            p for p in (REPO / "system/sessions").glob("*.md") if p.name != "index.md"
        )
        self.assertEqual(sessions, [], f"live session 이 남아 있다: {sessions}")
        done = sorted((REPO / "tasks/done").glob("*.md"))
        self.assertEqual(done, [], f"live done task 가 남아 있다: {done}")
        projects = sorted(
            p for p in (REPO / "research").iterdir() if p.is_dir() and not p.name.startswith("_")
        )
        self.assertEqual(projects, [], f"live research project 가 남아 있다: {projects}")
        meetings = sorted((REPO / "feedback/meetings").glob("*.md"))
        self.assertEqual(meetings, [], f"live meeting 이 남아 있다: {meetings}")

    def test_git_tracked_tree_passes_research_lint(self) -> None:
        """Git 이 실제 배포하는 파일만 재구성해 필수 빈 디렉터리 누락을 잡는다."""
        try:
            tracked = subprocess.run(
                ["git", "-C", str(REPO), "ls-files", "-z"],
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            self.skipTest("git 실행 파일이 없다")
        if tracked.returncode != 0:
            self.skipTest("git 저장소가 아닌 환경이다")

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
