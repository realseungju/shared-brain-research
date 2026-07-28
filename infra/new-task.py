#!/usr/bin/env python3
"""tasks/backlog에 date-slug task 파일을 생성한다."""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_PHASES = ("planning", "review", "implementation", "validation")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    except ValueError:
        return False


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="Shared Brain Lite task 생성")
    parser.add_argument("slug", help="소문자 영문·숫자·하이픈")
    parser.add_argument("--title", required=True, help="task 제목")
    parser.add_argument("--phase", choices=VALID_PHASES, default="planning")
    parser.add_argument("--assignee", default="maintainer / agent")
    parser.add_argument("--spec", default="none")
    parser.add_argument("--date", dest="task_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="저장소 루트")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        print(f"[ERROR] slug 형식 위반: {args.slug}", file=sys.stderr)
        return 2
    if not args.title.strip():
        print("[ERROR] title이 비어 있음", file=sys.stderr)
        return 2

    task_date = args.task_date or date.today().isoformat()
    if not valid_date(task_date):
        print(f"[ERROR] 날짜 형식 위반: {task_date}", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else repo_root()
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] Shared Brain Lite 루트가 아님: {root}", file=sys.stderr)
        return 2
    backlog = root / "tasks" / "backlog"
    backlog.mkdir(parents=True, exist_ok=True)

    task_id = f"T{task_date}-{args.slug}"
    destination = backlog / f"{task_id}.md"
    if destination.exists():
        print(f"[ERROR] 이미 존재: {destination}", file=sys.stderr)
        return 2

    body = f"""---
id: {task_id}
title: {args.title.strip()}
phase: {args.phase}
assignee_role: {args.assignee.strip()}
spec: {args.spec.strip()}
agent:
started:
finished:
closed_reason:
result:
---

# {args.title.strip()}

## 할 일

- [ ]

## 완료 조건

-

## 진행 메모

-
"""
    destination.write_text(body, encoding="utf-8", newline="\n")
    print(f"✓ task 생성: tasks/backlog/{destination.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
