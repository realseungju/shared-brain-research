from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from support import make_brain, run_script, write


class BrainLintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def lint(self):
        return run_script("brain-lint.py", str(self.root))

    def test_minimal_brain_is_clean(self) -> None:
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_task_requires_matching_id(self) -> None:
        write(
            self.root / "tasks/backlog/T2026-07-28-example.md",
            """---
id: T2026-07-28-wrong
title: 예제
phase: planning
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("id와 파일명 불일치", result.stdout)

    def test_task_rejects_unknown_phase(self) -> None:
        write(
            self.root / "tasks/backlog/T2026-07-28-example.md",
            """---
id: T2026-07-28-example
title: 예제
phase: brainstorming
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("phase 값 불량", result.stdout)

    def test_doing_task_requires_agent_and_started(self) -> None:
        write(
            self.root / "tasks/doing/T2026-07-28-example.md",
            """---
id: T2026-07-28-example
title: 예제
phase: implementation
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("doing task 필드 없음 'agent'", result.stdout)
        self.assertIn("doing task 필드 없음 'started'", result.stdout)

    def test_done_task_requires_closure_fields(self) -> None:
        write(
            self.root / "tasks/done/T2026-07-28-example.md",
            """---
id: T2026-07-28-example
title: 예제
phase: validation
finished: 2026-07-28
closed_reason: finished-ish
result: abc1234
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("closed_reason 값 불량", result.stdout)

    def test_duplicate_task_id_across_states(self) -> None:
        body = """---
id: T2026-07-28-example
title: 예제
phase: planning
---
"""
        write(self.root / "tasks/backlog/T2026-07-28-example.md", body)
        write(self.root / "tasks/doing/T2026-07-28-example.md", body)
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("task id 중복", result.stdout)

    def test_session_requires_body_sections(self) -> None:
        name = "2026-07-28-example.md"
        write(
            self.root / "system/sessions" / name,
            """---
date: 2026-07-28
agent: Codex
slug: example
tags: [demo]
---

## 한 것

완료
""",
        )
        write(
            self.root / "system/sessions/index.md",
            f"# Sessions Index\n\n- 2026-07-28 · [example]({name}) — Codex — #demo — 훅\n",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("session 섹션 없음 '미완·다음'", result.stdout)

    def test_index_pointing_at_missing_session(self) -> None:
        write(
            self.root / "system/sessions/index.md",
            "# Sessions Index\n\n- 2026-07-28 · [gone](2026-07-28-gone.md) — Codex — #demo — 훅\n",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("없는 파일을 가리킴", result.stdout)

    def test_entry_stub_must_point_at_rules(self) -> None:
        write(self.root / "CLAUDE.md", "아무 말이나 적혀 있다.\n")
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("진입점이 system/RULES.md를 가리키지 않음", result.stdout)

    def test_session_requires_index_entry(self) -> None:
        write(
            self.root / "system/sessions/2026-07-28-example.md",
            """---
date: 2026-07-28
agent: Codex
slug: example
tags: [demo]
---

## 한 것

완료

## 미완·다음

없음
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("index 미등재", result.stdout)


if __name__ == "__main__":
    unittest.main()
