#!/usr/bin/env python3
"""Session 요약 파일을 만들고 system/sessions/index.md에 등재한다."""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HOOK_MAX = 100
INDEX_HEADER = """# Sessions Index

최신 session이 아래에 추가된다. 시작할 때 꼬리 3~5줄만 읽고, 필요한 본문만 연다.
생성은 `python infra/new-session.py`를 사용한다.
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

    parser = argparse.ArgumentParser(description="Shared Brain Lite session 요약 생성")
    parser.add_argument("slug")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--tags", required=True, help="쉼표 구분")
    parser.add_argument("--hook", required=True, help=f"{HOOK_MAX}자 이내 index 요약")
    parser.add_argument("--did", required=True, help="한 것")
    parser.add_argument("--next", required=True, dest="next_", help="미완·다음")
    parser.add_argument("--decisions", default="(없음)")
    parser.add_argument("--caution", default="없음")
    parser.add_argument("--date", dest="session_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="저장소 루트")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        print(f"[ERROR] slug 형식 위반: {args.slug}", file=sys.stderr)
        return 2

    session_date = args.session_date or date.today().isoformat()
    if not valid_date(session_date):
        print(f"[ERROR] 날짜 형식 위반: {session_date}", file=sys.stderr)
        return 2

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    if not tags or any(not SLUG_RE.fullmatch(tag) for tag in tags):
        print("[ERROR] tags는 소문자 영문·숫자·하이픈 형식이어야 함", file=sys.stderr)
        return 2

    hook = " ".join(args.hook.split())
    if not hook or len(hook) > HOOK_MAX:
        print(f"[ERROR] hook은 1~{HOOK_MAX}자여야 함", file=sys.stderr)
        return 2
    if not args.agent.strip() or not args.did.strip() or not args.next_.strip():
        print("[ERROR] agent, did, next는 비울 수 없음", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else repo_root()
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] Shared Brain Lite 루트가 아님: {root}", file=sys.stderr)
        return 2

    sessions = root / "system" / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    destination = sessions / f"{session_date}-{args.slug}.md"
    if destination.exists():
        print(f"[ERROR] 이미 존재: {destination}", file=sys.stderr)
        return 2

    body = f"""---
date: {session_date}
agent: {args.agent.strip()}
slug: {args.slug}
tags: [{", ".join(tags)}]
---

# {session_date} — {args.agent.strip()} — {args.slug}

## 한 것

{args.did.strip()}

## 결정·이유

{args.decisions.strip() or "(없음)"}

## 미완·다음

{args.next_.strip()}

## 주의·함정

{args.caution.strip() or "없음"}
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
    print(f"✓ session 생성: system/sessions/{destination.name} (+index)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
