"""examples/ 의 예시 산출물이 실제 스키마를 만족하는지 지킨다.

brain-lint 는 examples/ 를 검사하지 않는다(그래야 live 트리를 비워 배포할 수 있다).
그래서 스키마가 바뀌면 예시만 조용히 낡는다 — 여기서 예시를 빈 저장소의 제자리에
놓고 lint 를 돌려 그 드리프트를 잡는다.
"""
from __future__ import annotations

from pathlib import Path
import shutil
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

        result = run_script("brain-lint.py", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_live_tree_ships_empty(self) -> None:
        """배포 상태 확인 — 템플릿 복제자가 남의 기록을 물려받지 않아야 한다."""
        sessions = sorted(
            p for p in (REPO / "system/sessions").glob("*.md") if p.name != "index.md"
        )
        self.assertEqual(sessions, [], f"live session 이 남아 있다: {sessions}")
        done = sorted((REPO / "tasks/done").glob("*.md"))
        self.assertEqual(done, [], f"live done task 가 남아 있다: {done}")


if __name__ == "__main__":
    unittest.main()
