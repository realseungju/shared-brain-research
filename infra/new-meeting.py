#!/usr/bin/env python3
"""Create a privacy-safe meeting file in feedback/meetings."""
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
        raise ValueError(f"{field} must be a single non-empty line")
    return result


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="Create a Shared Brain Research meeting")
    parser.add_argument("slug", help="lowercase letters, digits, and hyphens")
    parser.add_argument("--title", required=True)
    parser.add_argument("--project", required=True, help="project slug, or product")
    parser.add_argument("--visibility", choices=VALID_VISIBILITY, default="redacted")
    parser.add_argument("--date", dest="meeting_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="repository root")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug) or not SLUG_RE.fullmatch(args.project):
        print("[ERROR] project and slug must be lowercase letters, digits, and hyphens", file=sys.stderr)
        return 2

    meeting_date = args.meeting_date or date.today().isoformat()
    if not valid_date(meeting_date):
        print(f"[ERROR] invalid date format: {meeting_date}", file=sys.stderr)
        return 2

    try:
        title = one_line(args.title, "title")
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else repo_root()
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] not a Shared Brain Research root: {root}", file=sys.stderr)
        return 2

    meetings = root / "feedback" / "meetings"
    meetings.mkdir(parents=True, exist_ok=True)
    destination = meetings / f"{meeting_date}-{args.slug}.md"
    if destination.exists():
        print(f"[ERROR] already exists: {destination}", file=sys.stderr)
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

## Context

- Purpose:
- Roles present:
- Source location: a path outside the repo, or `not-recorded`

## Source summary

TODO: strip personal and confidential content, and separate quote, paraphrase, and inference.

## Feedback

### {feedback_id}

- scope: research
- kind: observation
- statement: TODO
- source_mode: inference
- status: captured
- human_approved: no
- linked_artifact:
- reason:
- validation:

## Decisions

None. No decision is made without human approval and a link into `system/decisions.md`.

## Follow-ups

- none
"""
    destination.write_text(body, encoding="utf-8", newline="\n")
    relative = destination.relative_to(root).as_posix()
    print(f"✓ meeting created: {relative} (visibility={args.visibility})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
