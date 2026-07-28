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
        "research/_template",
        "feedback/meetings",
        "feedback/_template",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    write(root / "system/RULES.md", "# Rules\n")
    write(root / "system/context.md", "# Context\n")
    write(root / "system/sessions/index.md", "# Sessions Index\n")
    write(root / "tasks/README.md", "# Tasks\n")
    for stub in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"):
        write(root / stub, "먼저 system/RULES.md를 읽는다.\n")
    write(root / "feedback/README.md", "# Feedback\n")
    write(root / "feedback/_template/meeting.md", "# Meeting template\n")
    for name in ("overview.md", "questions.md", "claims.md", "experiment.md"):
        write(root / "research/_template" / name, f"# {name}\n")
    write(root / "UPSTREAM.md", "# Upstream\n")


def make_research_project(root: Path, slug: str = "demo-project") -> Path:
    project = root / "research" / slug
    (project / "experiments").mkdir(parents=True, exist_ok=True)
    write(project / "overview.md", f"# Overview — {slug}\n")
    write(project / "questions.md", "# Questions\n")
    write(
        project / "claims.md",
        """# Claims

## C001

- statement: baseline보다 나아지는가
- status: candidate
- evidence: TBD
- evidence_kind: unverified
- human_reviewed: no
- reason:
""",
    )
    return project


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO / "infra" / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
