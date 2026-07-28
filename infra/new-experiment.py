#!/usr/bin/env python3
"""연구 프로젝트에 date-slug experiment 파일을 생성한다."""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_STATUSES = ("planned", "running")


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

    parser = argparse.ArgumentParser(description="Shared Brain Research experiment 생성")
    parser.add_argument("slug", help="소문자 영문·숫자·하이픈")
    parser.add_argument("--project", required=True, help="research/{project}/ slug")
    parser.add_argument("--title", required=True)
    parser.add_argument("--hypothesis", required=True, help="연결 가설 ID 또는 한 줄 가설")
    parser.add_argument("--status", choices=VALID_STATUSES, default="planned")
    parser.add_argument("--dataset-version", default="TBD")
    parser.add_argument("--code-commit", default="TBD")
    parser.add_argument("--seed-or-repeats", default="TBD")
    parser.add_argument("--artifact", default="TBD")
    parser.add_argument("--date", dest="experiment_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="저장소 루트")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug) or not SLUG_RE.fullmatch(args.project):
        print("[ERROR] project와 slug는 소문자 영문·숫자·하이픈 형식이어야 함", file=sys.stderr)
        return 2

    experiment_date = args.experiment_date or date.today().isoformat()
    if not valid_date(experiment_date):
        print(f"[ERROR] 날짜 형식 위반: {experiment_date}", file=sys.stderr)
        return 2

    try:
        title = one_line(args.title, "title")
        hypothesis = one_line(args.hypothesis, "hypothesis")
        dataset_version = one_line(args.dataset_version, "dataset-version")
        code_commit = one_line(args.code_commit, "code-commit")
        seed_or_repeats = one_line(args.seed_or_repeats, "seed-or-repeats")
        artifact = one_line(args.artifact, "artifact")
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    root = Path(args.root).resolve() if args.root else repo_root()
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] Shared Brain Research 루트가 아님: {root}", file=sys.stderr)
        return 2

    project = root / "research" / args.project
    if not (project / "overview.md").is_file():
        print(
            f"[ERROR] 연구 프로젝트 overview 없음: research/{args.project}/overview.md",
            file=sys.stderr,
        )
        return 2

    experiment_id = f"E{experiment_date}-{args.slug}"
    destination = project / "experiments" / f"{experiment_id}.md"
    if destination.exists():
        print(f"[ERROR] 이미 존재: {destination}", file=sys.stderr)
        return 2
    destination.parent.mkdir(parents=True, exist_ok=True)

    body = f"""---
id: {experiment_id}
title: {title}
project: {args.project}
date: {experiment_date}
status: {args.status}
hypothesis: {hypothesis}
evidence_kind: unverified
dataset_version: {dataset_version}
code_commit: {code_commit}
seed_or_repeats: {seed_or_repeats}
artifact: {artifact}
---

# {title}

## 연구 질문

TODO

## 가설

- 연결 가설: `{hypothesis}`
- 예상:
- **반증 조건:**

## 계획

- 비교 조건:
- 주지표:
- baseline:
- 판단 기준:

## 실행 조건

| 항목 | 값 |
|---|---|
| 코드 커밋 | `{code_commit}` |
| 데이터·버전 | `{dataset_version}` |
| 모델·버전 핀 |  |
| 시드·반복 | `{seed_or_repeats}` |
| 하드웨어 |  |
| artifact | `{artifact}` |

## 실행 로그

- {experiment_date} — 생성

## 결과

TODO

## 해석

- claim candidate:
- 근거 종류: `unverified`
- 이 결과로 말할 수 없는 것:

## 한계

- TODO

## 다음 단계

- [ ]
"""
    destination.write_text(body, encoding="utf-8", newline="\n")
    relative = destination.relative_to(root).as_posix()
    print(f"✓ experiment 생성: {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
