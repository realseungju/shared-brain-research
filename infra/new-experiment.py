#!/usr/bin/env python3
"""Create a date-slug experiment file in a research project."""
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
        raise ValueError(f"{field} must be a single non-empty line")
    return result


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="Create a Shared Brain Research experiment")
    parser.add_argument("slug", help="lowercase letters, digits, and hyphens")
    parser.add_argument("--project", required=True, help="research/{project}/ slug")
    parser.add_argument("--title", required=True)
    parser.add_argument("--hypothesis", required=True, help="linked hypothesis id, or the hypothesis in one line")
    parser.add_argument("--status", choices=VALID_STATUSES, default="planned")
    parser.add_argument("--dataset-version", default="TBD")
    parser.add_argument("--code-commit", default="TBD")
    parser.add_argument("--seed-or-repeats", default="TBD")
    parser.add_argument("--artifact", default="TBD")
    parser.add_argument("--date", dest="experiment_date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--root", default=None, help="repository root")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug) or not SLUG_RE.fullmatch(args.project):
        print("[ERROR] project and slug must be lowercase letters, digits, and hyphens", file=sys.stderr)
        return 2

    experiment_date = args.experiment_date or date.today().isoformat()
    if not valid_date(experiment_date):
        print(f"[ERROR] invalid date format: {experiment_date}", file=sys.stderr)
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
        print(f"[ERROR] not a Shared Brain Research root: {root}", file=sys.stderr)
        return 2

    project = root / "research" / args.project
    if not (project / "overview.md").is_file():
        print(
            f"[ERROR] research project overview missing: research/{args.project}/overview.md",
            file=sys.stderr,
        )
        return 2

    experiment_id = f"E{experiment_date}-{args.slug}"
    destination = project / "experiments" / f"{experiment_id}.md"
    if destination.exists():
        print(f"[ERROR] already exists: {destination}", file=sys.stderr)
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

## Research question

TODO

## Hypothesis

- Linked hypothesis: `{hypothesis}`
- Expectation:
- **Falsified if:**

## Plan

- Comparison:
- Primary metric:
- baseline:
- Decision rule:

## Run conditions

| Field | Value |
|---|---|
| Code commit | `{code_commit}` |
| Dataset and version | `{dataset_version}` |
| Model and version pin |  |
| Seeds and repeats | `{seed_or_repeats}` |
| Hardware |  |
| artifact | `{artifact}` |

## Run log

- {experiment_date} - created

## Results

TODO

## Interpretation

- claim candidate:
- Evidence kind: `unverified`
- What this result cannot say:

## Limits

- TODO

## Next

- [ ]
"""
    destination.write_text(body, encoding="utf-8", newline="\n")
    relative = destination.relative_to(root).as_posix()
    print(f"✓ experiment created: {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
