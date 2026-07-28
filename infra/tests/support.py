from __future__ import annotations

from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_brain(root: Path) -> None:
    for directory in (
        "system/sessions",
        "tasks/backlog",
        "tasks/doing",
        "tasks/done",
        "specs",
        "inbox",
        "knowledge",
        "skills",
        "personal",
        "research",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    write(root / "system/RULES.md", "# Rules\n")
    write(root / "system/context.md", "# Context\n")
    write(root / "system/sessions/index.md", "# Sessions Index\n")
    write(root / "tasks/README.md", "# Tasks\n")
    for stub in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"):
        write(root / stub, "먼저 system/RULES.md를 읽는다.\n")


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO / "infra" / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
