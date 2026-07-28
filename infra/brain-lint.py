#!/usr/bin/env python3
"""Shared Brain Lite의 최소 구조 불변식을 읽기 전용으로 검사한다."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import sys

ERRORS: list[str] = []

SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
TASK_FILE = re.compile(rf"^T(\d{{4}}-\d{{2}}-\d{{2}})-({SLUG})\.md$")
SESSION_FILE = re.compile(rf"^(\d{{4}}-\d{{2}}-\d{{2}})-({SLUG})\.md$")
VALID_PHASES = {"planning", "review", "implementation", "validation"}
VALID_CLOSED_REASONS = {"completed", "cancelled", "superseded"}
ENTRY_STUBS = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md")
REQUIRED_DIRS = (
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
)


def error(message: str) -> None:
    ERRORS.append(message)


def valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    except ValueError:
        return False


def frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return result
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return None


def check_required(root: Path) -> None:
    for name in REQUIRED_DIRS:
        if not (root / name).is_dir():
            error(f"필수 디렉터리 없음: {name}")
    for name in ("system/RULES.md", "system/context.md", "system/sessions/index.md"):
        if not (root / name).is_file():
            error(f"필수 파일 없음: {name}")


def check_entry_stubs(root: Path) -> None:
    for name in ENTRY_STUBS:
        path = root / name
        if not path.is_file():
            error(f"진입점 없음: {name}")
        elif "system/RULES.md" not in path.read_text(encoding="utf-8"):
            error(f"진입점이 system/RULES.md를 가리키지 않음: {name}")


def check_tasks(root: Path) -> None:
    seen: set[str] = set()
    for state in ("backlog", "doing", "done"):
        directory = root / "tasks" / state
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            relative = path.relative_to(root).as_posix()
            match = TASK_FILE.fullmatch(path.name)
            if not match or not valid_date(match.group(1)):
                error(f"task 파일명 형식 위반: {relative}")
                continue
            task_id = path.stem
            if task_id in seen:
                error(f"task id 중복: {task_id}")
            seen.add(task_id)

            text = path.read_text(encoding="utf-8")
            meta = frontmatter(text)
            if meta is None:
                error(f"task frontmatter 없음: {relative}")
                continue
            for field in ("id", "title", "phase"):
                if not meta.get(field):
                    error(f"task 필수 필드 없음 '{field}': {relative}")
            if meta.get("id") and meta["id"] != task_id:
                error(f"task id와 파일명 불일치: {relative}")
            if meta.get("phase") and meta["phase"] not in VALID_PHASES:
                error(f"task phase 값 불량: {relative}")

            if state == "doing":
                for field in ("agent", "started"):
                    if not meta.get(field):
                        error(f"doing task 필드 없음 '{field}': {relative}")
                if meta.get("started") and not valid_date(meta["started"]):
                    error(f"doing task started 날짜 불량: {relative}")

            if state == "done":
                for field in ("finished", "closed_reason", "result"):
                    if not meta.get(field):
                        error(f"done task 필드 없음 '{field}': {relative}")
                if meta.get("finished") and not valid_date(meta["finished"]):
                    error(f"done task finished 날짜 불량: {relative}")
                reason = meta.get("closed_reason")
                if reason and reason not in VALID_CLOSED_REASONS:
                    error(f"done task closed_reason 값 불량: {relative}")


def check_sessions(root: Path) -> None:
    sessions = root / "system" / "sessions"
    index = sessions / "index.md"
    if not sessions.is_dir() or not index.is_file():
        return
    index_text = index.read_text(encoding="utf-8")
    existing: set[str] = set()

    for path in sorted(sessions.glob("*.md")):
        if path.name == "index.md":
            continue
        relative = path.relative_to(root).as_posix()
        match = SESSION_FILE.fullmatch(path.name)
        if not match or not valid_date(match.group(1)):
            error(f"session 파일명 형식 위반: {relative}")
            continue
        existing.add(path.name)
        text = path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        if meta is None:
            error(f"session frontmatter 없음: {relative}")
            continue
        for field in ("date", "agent", "slug", "tags"):
            if not meta.get(field):
                error(f"session 필수 필드 없음 '{field}': {relative}")
        if meta.get("date") and meta["date"] != match.group(1):
            error(f"session date와 파일명 불일치: {relative}")
        if meta.get("slug") and meta["slug"] != match.group(2):
            error(f"session slug와 파일명 불일치: {relative}")
        for section in ("한 것", "미완·다음"):
            if f"## {section}" not in text:
                error(f"session 섹션 없음 '{section}': {relative}")
        if f"]({path.name})" not in index_text:
            error(f"session index 미등재: {relative}")

    for linked in re.findall(r"\]\((\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md)\)", index_text):
        if linked not in existing:
            error(f"session index가 없는 파일을 가리킴: {linked}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    ERRORS.clear()
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"[FATAL] 저장소 루트 없음: {root}", file=sys.stderr)
        return 2

    check_required(root)
    check_entry_stubs(root)
    check_tasks(root)
    check_sessions(root)

    for message in ERRORS:
        print(f"[ERROR] {message}")
    if ERRORS:
        print(f"\nbrain-lint: ERROR {len(ERRORS)}")
        return 1
    print("brain-lint: 클린 ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
