#!/usr/bin/env python3
"""Create a session summary file and register it in system/sessions/index.md."""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HOOK_MAX = 100
INDEX_HEADER = """# Sessions Index

The newest session is appended below. At the start of a session read only the last 3-5
lines, then open just the bodies you need. Create entries with
`python infra/new-session.py`.
"""


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

    parser = argparse.ArgumentParser(description="Create a Shared Brain Research session summary")
    parser.add_argument("slug")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--tags", required=True, help="comma-separated")
    parser.add_argument("--hook", required=True, help=f"index summary, at most {HOOK_MAX} characters")
    parser.add_argument("--did", required=True, help="what was done")
    parser.add_argument("--next", required=True, dest="next_", help="open items and what is next")
    parser.add_argument("--decisions", default="(none)")
    parser.add_argument("--caution", default="none")
    parser.add_argument("--date", dest="session_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="repository root")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        print(f"[ERROR] invalid slug format: {args.slug}", file=sys.stderr)
        return 2

    session_date = args.session_date or date.today().isoformat()
    if not valid_date(session_date):
        print(f"[ERROR] invalid date format: {session_date}", file=sys.stderr)
        return 2

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    if not tags or any(not SLUG_RE.fullmatch(tag) for tag in tags):
        print("[ERROR] tags must be lowercase letters, digits, and hyphens", file=sys.stderr)
        return 2

    hook = " ".join(args.hook.split())
    if not hook or len(hook) > HOOK_MAX:
        print(f"[ERROR] hook must be 1 to {HOOK_MAX} characters", file=sys.stderr)
        return 2
    if not args.agent.strip() or not args.did.strip() or not args.next_.strip():
        print("[ERROR] agent, did, and next cannot be empty", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else repo_root()
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] not a Shared Brain Research root: {root}", file=sys.stderr)
        return 2

    sessions = root / "system" / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    destination = sessions / f"{session_date}-{args.slug}.md"
    if destination.exists():
        print(f"[ERROR] already exists: {destination}", file=sys.stderr)
        return 2

    body = f"""---
date: {session_date}
agent: {args.agent.strip()}
slug: {args.slug}
tags: [{", ".join(tags)}]
---

# {session_date} — {args.agent.strip()} — {args.slug}

## What was done

{args.did.strip()}

## Decisions and why

{args.decisions.strip() or "(none)"}

## Open and next

{args.next_.strip()}

## Cautions

{args.caution.strip() or "none"}
"""
    destination.write_text(body, encoding="utf-8", newline="\n")

    index = sessions / "index.md"
    current = index.read_text(encoding="utf-8") if index.exists() else INDEX_HEADER
    tag_text = " ".join(f"#{tag}" for tag in tags)
    line = (
        f"- {session_date} · [{args.slug}]({destination.name}) — "
        f"{args.agent.strip()} — {tag_text} — {hook}"
    )
    index.write_text(current.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")
    print(f"✓ session created: system/sessions/{destination.name} (+index)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
