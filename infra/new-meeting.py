#!/usr/bin/env python3
"""feedback/meetings에 privacy-safe meeting 파일을 생성한다."""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_VISIBILITY = ("public", "private", "redacted")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    except ValueError:
        return False


def one_line(value: str, field: str) -> str:
    result = value.strip()
    if not result or "\n" in result or "\r" in result:
        raise ValueError(f"{field}는 비어 있지 않은 한 줄이어야 함")
    return result


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="Shared Brain Research meeting 생성")
    parser.add_argument("slug", help="소문자 영문·숫자·하이픈")
    parser.add_argument("--title", required=True)
    parser.add_argument("--project", required=True, help="project slug 또는 product")
    parser.add_argument("--visibility", choices=VALID_VISIBILITY, default="redacted")
    parser.add_argument("--date", dest="meeting_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="저장소 루트")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug) or not SLUG_RE.fullmatch(args.project):
        print("[ERROR] project와 slug는 소문자 영문·숫자·하이픈 형식이어야 함", file=sys.stderr)
        return 2

    meeting_date = args.meeting_date or date.today().isoformat()
    if not valid_date(meeting_date):
        print(f"[ERROR] 날짜 형식 위반: {meeting_date}", file=sys.stderr)
        return 2

    try:
        title = one_line(args.title, "title")
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else repo_root()
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] Shared Brain Research 루트가 아님: {root}", file=sys.stderr)
        return 2

    meetings = root / "feedback" / "meetings"
    meetings.mkdir(parents=True, exist_ok=True)
    destination = meetings / f"{meeting_date}-{args.slug}.md"
    if destination.exists():
        print(f"[ERROR] 이미 존재: {destination}", file=sys.stderr)
        return 2

    feedback_id = f"FB-{meeting_date}-01"
    body = f"""---
date: {meeting_date}
title: {title}
project: {args.project}
visibility: {args.visibility}
status: captured
---

# {title}

## 맥락

- 목적:
- 참여 역할:
- 원문 위치: repo 밖 경로 또는 `not-recorded`

## 출처 요약

TODO: 개인정보와 비공개 내용을 제거하고 인용·요약·AI 추론을 구분한다.

## Feedback

### {feedback_id}

- scope: research
- kind: observation
- statement: TODO
- source_mode: inference
- status: captured
- human_approved: no
- linked_artifact:
- validation:

## 확정된 결정

없음. 사람 승인과 `system/decisions.md` 링크 없이는 결정을 만들지 않는다.

## 후속 링크

- 없음
"""
    destination.write_text(body, encoding="utf-8", newline="\n")
    relative = destination.relative_to(root).as_posix()
    print(f"✓ meeting 생성: {relative} (visibility={args.visibility})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
