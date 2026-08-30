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
title: Example
phase: planning
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("task id does not match filename", result.stdout)

    def test_task_rejects_unknown_phase(self) -> None:
        write(
            self.root / "tasks/backlog/T2026-07-28-example.md",
            """---
id: T2026-07-28-example
title: Example
phase: brainstorming
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid task phase value", result.stdout)

    def test_doing_task_requires_agent_and_started(self) -> None:
        write(
            self.root / "tasks/doing/T2026-07-28-example.md",
            """---
id: T2026-07-28-example
title: Example
phase: implementation
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("doing task field missing 'agent'", result.stdout)
        self.assertIn("doing task field missing 'started'", result.stdout)

    def test_done_task_requires_closure_fields(self) -> None:
        write(
            self.root / "tasks/done/T2026-07-28-example.md",
            """---
id: T2026-07-28-example
title: Example
phase: validation
finished: 2026-07-28
closed_reason: finished-ish
result: abc1234
---
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid done task closed_reason value", result.stdout)

    def test_duplicate_task_id_across_states(self) -> None:
        body = """---
id: T2026-07-28-example
title: Example
phase: planning
---
"""
        write(self.root / "tasks/backlog/T2026-07-28-example.md", body)
        write(self.root / "tasks/doing/T2026-07-28-example.md", body)
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate task id", result.stdout)

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

## What was done

Done.
""",
        )
        write(
            self.root / "system/sessions/index.md",
            f"# Sessions Index\n\n- 2026-07-28 · [example]({name}) — Codex — #demo — hook\n",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("session section missing 'Open and next'", result.stdout)

    def test_index_pointing_at_missing_session(self) -> None:
        write(
            self.root / "system/sessions/index.md",
            "# Sessions Index\n\n- 2026-07-28 · [gone](2026-07-28-gone.md) — Codex — #demo — hook\n",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("points at a file that does not exist", result.stdout)

    def test_entry_stub_must_point_at_rules(self) -> None:
        write(self.root / "CLAUDE.md", "Some unrelated text.\n")
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("entry point does not point at system/RULES.md", result.stdout)

    def test_session_requires_index_entry(self) -> None:
        write(
            self.root / "system/sessions/2026-07-28-example.md",
            """---
date: 2026-07-28
agent: Codex
slug: example
tags: [demo]
---

## What was done

Done.

## Open and next

None.
""",
        )
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertIn("session not listed in index", result.stdout)


if __name__ == "__main__":
    unittest.main()
