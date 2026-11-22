#!/usr/bin/env python3
"""List lines in public files that still contain Korean (Hangul syllables).

English is canonical for what a cloner and an agent read (ADR-008). Three kinds of line may
keep Korean, and only these:

- Korean translations themselves (`*.ko.md`).
- Test data under `infra/tests/` — e.g. Korean titles in the library merge test.
- A line that links to a Korean translation (`… [README.ko.md](README.ko.md)`).

Usage: python infra/english-check.py [ROOT]   (exit 1 if any line is found)
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

HANGUL = re.compile("[가-힣]")
TRANSLATION_LINK = re.compile(r"\]\([^)]*\.ko\.md\)")
EXEMPT_DIRS = ("infra/tests/",)


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True)
    if result.returncode == 0:
        return [p for p in result.stdout.decode("utf-8").split("\0") if p]
    # Not a Git checkout (e.g. an unpacked archive): fall back to every file.
    return [p.relative_to(root).as_posix() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts]


def korean_lines(root: Path) -> list[tuple[str, int, str]]:
    found = []
    for rel in tracked_files(root):
        if rel.endswith(".ko.md") or rel.startswith(EXEMPT_DIRS):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable — not prose
        for number, line in enumerate(text.splitlines(), 1):
            if HANGUL.search(line) and not TRANSLATION_LINK.search(line):
                found.append((rel, number, line.strip()))
    return found


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else Path(__file__).resolve().parents[1])
    found = korean_lines(root)
    for rel, number, line in found:
        print(f"{rel}:{number}: {line[:100]}")
    files = len({rel for rel, _, _ in found})
    print(f"english-check: {len(found)} Korean line(s) in {files} file(s)")
    return 1 if found else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
