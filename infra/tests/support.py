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
        write(root / stub, "Read system/RULES.md first.\n")

    write(root / "feedback/README.md", "# Feedback" + chr(10))
    write(root / "feedback/_template/meeting.md", "# Meeting template" + chr(10))
    for name in ("overview.md", "questions.md", "claims.md", "experiment.md"):
        write(root / "research/_template" / name, "# " + name + chr(10))
    write(root / "UPSTREAM.md", "# Upstream" + chr(10))


def make_research_project(root: Path, slug: str = "demo-project") -> Path:
    project = root / "research" / slug
    (project / "experiments").mkdir(parents=True, exist_ok=True)
    write(project / "overview.md", "# Overview - " + slug + chr(10))
    write(project / "questions.md", "# Questions" + chr(10))
    write(
        project / "claims.md",
        chr(10).join([
            "# Claims",
            "",
            "## C001",
            "",
            "- statement: does it beat the baseline",
            "- status: candidate",
            "- evidence: TBD",
            "- evidence_kind: unverified",
            "- human_reviewed: no",
            "- reason:",
            "",
        ]),
    )
    return project


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO / "infra" / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
