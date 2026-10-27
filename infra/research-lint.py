#!/usr/bin/env python3
"""Check the common brain invariants plus the research and meeting provenance contract."""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ERRORS: list[str] = []
WARNINGS: list[str] = []

SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
EXPERIMENT_FILE = re.compile(rf"^E(\d{{4}}-\d{{2}}-\d{{2}})-({SLUG})\.md$")
MEETING_FILE = re.compile(rf"^(\d{{4}}-\d{{2}}-\d{{2}})-({SLUG})\.md$")
FEEDBACK_ID = re.compile(r"^FB-(\d{4}-\d{2}-\d{2})-(\d{2})$")
CLAIM_ID = re.compile(r"^C\d{3}$")

EXPERIMENT_STATUSES = {"planned", "running", "completed", "negative-result", "invalidated"}
CLOSED_EXPERIMENT_STATUSES = {"completed", "negative-result", "invalidated"}
EVIDENCE_KINDS = {"measured", "estimated", "unverified"}
MEETING_VISIBILITY = {"public", "private", "redacted"}
MEETING_STATUSES = {"captured", "triaged", "closed"}
FEEDBACK_SCOPES = {"product", "research", "workflow"}
FEEDBACK_KINDS = {"request", "problem", "observation", "question", "decision-candidate"}
SOURCE_MODES = {"quote", "paraphrase", "inference"}
FEEDBACK_STATUSES = {"captured", "accepted", "rejected", "deferred", "validated"}
CLAIM_STATUSES = {"candidate", "supported", "rejected"}
RECORD_FILE = re.compile(r"^(L\d{4})\.md$")
TRAIL_DIR = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{SLUG}$")
STEP_FILE = re.compile(r"^(step-(\d{2}))\.md$")
STEP_REF = re.compile(r"^(step-\d{2})#(\d+)$")
LIBRARY_REF = re.compile(r"(?:library:|library/papers/)(L\d{4})")
STEP_DIRECTIONS = {"search", "references", "citations", "related"}
VENUE_TYPES = {"journal", "conference", "other", "preprint"}
PLACEHOLDERS = {"", "-", "todo", "tbd", "pending", "none", "n/a", "not-verified"}
COMMIT_REF = re.compile(r"^(?:[0-9a-f]{7,40}|not-applicable)$")


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
        match = re.match(r"^([A-Za-z0-9_]+):[ \t]*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return None


def record_fields(block: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"^-[ \t]+([a-z_]+):[ \t]*(.*)$", block, flags=re.MULTILINE):
        result[match.group(1)] = match.group(2).strip()
    return result


def is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("`").casefold()
    return normalized in PLACEHOLDERS or normalized.startswith("todo:")


def section_has_content(text: str, name: str) -> bool:
    match = re.search(
        rf"^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return False
    lines = match.group(1).splitlines()
    table_scaffold: set[int] = set()

    def table_cells(raw: str) -> list[str] | None:
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            return None
        return [cell.strip().strip("`") for cell in line[1:-1].split("|")]

    def is_table_separator(cells: list[str] | None) -> bool:
        return bool(cells) and all(
            re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells
        )

    for index, raw in enumerate(lines):
        cells = table_cells(raw)
        if cells is None:
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        next_cells = table_cells(lines[next_index]) if next_index < len(lines) else None
        if is_table_separator(next_cells):
            table_scaffold.update({index, next_index})

    for index, raw in enumerate(lines):
        line = raw.strip().strip("`")
        if not line or is_placeholder(line):
            continue
        cells = table_cells(raw)
        if cells is not None:
            if index in table_scaffold or is_table_separator(cells):
                continue
            if all(is_placeholder(cell) for cell in cells):
                continue
            return True
        bullet = re.fullmatch(r"[-*+]\s+(.+)", line)
        if bullet:
            content = bullet.group(1).strip()
            if re.fullmatch(r"\[[ xX]\]\s*", content):
                continue
            plain = content.replace("**", "").strip()
            if ":" in plain and is_placeholder(plain.split(":", 1)[1]):
                continue
        if line in {"- TODO", "- [ ]"}:
            continue
        return True
    return False


def linked_path(root: Path, value: str) -> Path | None:
    cleaned = value.strip().strip("`")
    if is_placeholder(cleaned) or "://" in cleaned:
        return None
    path_text = cleaned.split("#", 1)[0]
    candidate = (root / path_text).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def run_core_lint(root: Path) -> int:
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("brain-lint.py")), str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode


def check_required(root: Path) -> None:
    for name in (
        "feedback/meetings",
        "feedback/_template",
        "research/_template",
    ):
        if not (root / name).is_dir():
            error(f"required research directory missing: {name}")
    for name in (
        "feedback/README.md",
        "feedback/_template/meeting.md",
        "research/_template/overview.md",
        "research/_template/questions.md",
        "research/_template/claims.md",
        "research/_template/experiment.md",
        "UPSTREAM.md",
    ):
        if not (root / name).is_file():
            error(f"required research file missing: {name}")


def check_experiment(root: Path, project_slug: str, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    match = EXPERIMENT_FILE.fullmatch(path.name)
    if not match or not valid_date(match.group(1)):
        error(f"invalid experiment filename format: {relative}")
        return

    experiment_id = path.stem
    text = path.read_text(encoding="utf-8")
    meta = frontmatter(text)
    if meta is None:
        error(f"experiment frontmatter missing: {relative}")
        return

    required = (
        "id",
        "title",
        "project",
        "date",
        "status",
        "hypothesis",
        "evidence_kind",
        "dataset_version",
        "code_commit",
        "seed_or_repeats",
        "artifact",
    )
    for field in required:
        if not meta.get(field):
            error(f"experiment field missing '{field}': {relative}")

    if meta.get("id") != experiment_id:
        error(f"experiment id does not match filename: {relative}")
    if meta.get("project") != project_slug:
        error(f"experiment project does not match its directory: {relative}")
    if meta.get("date") != match.group(1):
        error(f"experiment date does not match filename: {relative}")
    if meta.get("status") and meta["status"] not in EXPERIMENT_STATUSES:
        error(f"invalid experiment status value: {relative}")
    if meta.get("evidence_kind") and meta["evidence_kind"] not in EVIDENCE_KINDS:
        error(f"invalid experiment evidence_kind value: {relative}")

    for section in ("Research question", "Hypothesis", "Plan", "Run conditions", "Results", "Interpretation", "Limits", "Next"):
        if f"## {section}" not in text:
            error(f"experiment section missing '{section}': {relative}")

    if meta.get("status") in CLOSED_EXPERIMENT_STATUSES:
        for field in (
            "hypothesis",
            "dataset_version",
            "code_commit",
            "seed_or_repeats",
            "artifact",
        ):
            if is_placeholder(meta.get(field, "")):
                error(f"closed experiment is missing a reproducibility field '{field}': {relative}")
        if meta.get("evidence_kind") == "unverified":
            error(f"closed experiment still has evidence_kind unverified: {relative}")
        if not COMMIT_REF.fullmatch(meta.get("code_commit", "")):
            error(f"invalid code_commit in closed experiment: {relative}")
        for section in ("Results", "Interpretation", "Limits"):
            if not section_has_content(text, section):
                error(f"closed experiment section is empty '{section}': {relative}")


def check_claims(root: Path, project_slug: str, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    matches = list(
        re.finditer(
            r"^## (C\d{3})\s*$\n(.*?)(?=^## |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    )
    seen: set[str] = set()
    for match in matches:
        claim_id, block = match.group(1), match.group(2)
        if not CLAIM_ID.fullmatch(claim_id) or claim_id in seen:
            error(f"invalid or duplicate claim id '{claim_id}': {relative}")
        seen.add(claim_id)
        fields = record_fields(block)
        for field in ("statement", "status", "evidence", "evidence_kind", "human_reviewed"):
            if not fields.get(field):
                error(f"claim field missing '{field}' ({claim_id}): {relative}")

        status = fields.get("status", "")
        evidence_kind = fields.get("evidence_kind", "")
        reviewed = fields.get("human_reviewed", "")
        if status and status not in CLAIM_STATUSES:
            error(f"invalid claim status value ({claim_id}): {relative}")
        if evidence_kind and evidence_kind not in EVIDENCE_KINDS:
            error(f"invalid claim evidence_kind value ({claim_id}): {relative}")
        if reviewed and reviewed not in {"yes", "no"}:
            error(f"invalid claim human_reviewed value ({claim_id}): {relative}")

        if status == "supported":
            if is_placeholder(fields.get("statement", "")):
                error(f"supported claim has no statement ({claim_id}): {relative}")
            if reviewed != "yes":
                error(f"supported claim has no human review ({claim_id}): {relative}")
            if evidence_kind not in {"measured", "estimated"}:
                error(f"supported claim rests on unverified evidence ({claim_id}): {relative}")
            evidence = linked_path(root, fields.get("evidence", ""))
            if fields.get("evidence", "").strip("`").startswith(("library:", "library/")) or LIBRARY_REF.search(
                fields.get("evidence", "")
            ):
                error(f"supported claim cites a library paper; papers are not experiment evidence ({claim_id}): {relative}")
            elif evidence is None or not evidence.is_file():
                error(f"supported claim has no evidence path ({claim_id}): {relative}")
            else:
                expected = (root / "research" / project_slug / "experiments").resolve()
                try:
                    evidence.resolve().relative_to(expected)
                except ValueError:
                    error(f"supported claim points outside the project experiments ({claim_id}): {relative}")
        if status == "rejected":
            if is_placeholder(fields.get("statement", "")):
                error(f"rejected claim has no statement ({claim_id}): {relative}")
            if reviewed != "yes":
                error(f"rejected claim has no human review ({claim_id}): {relative}")
            if is_placeholder(fields.get("reason", "")):
                error(f"rejected claim has no reason ({claim_id}): {relative}")

    if not matches:
        error(f"no claim entries: {relative}")


def check_research_projects(root: Path) -> None:
    research = root / "research"
    if not research.is_dir():
        return
    for project in sorted(research.iterdir()):
        if not project.is_dir() or project.name.startswith("_"):
            continue
        if not re.fullmatch(SLUG, project.name):
            error(f"invalid research project slug: {project.relative_to(root).as_posix()}")
            continue
        for name in ("overview.md", "questions.md", "claims.md", "experiments"):
            target = project / name
            if name == "experiments":
                if not target.is_dir():
                    error(f"required research project directory missing: {target.relative_to(root).as_posix()}")
            elif not target.is_file():
                error(f"required research project file missing: {target.relative_to(root).as_posix()}")
        if (project / "claims.md").is_file():
            check_claims(root, project.name, project / "claims.md")
        experiments = project / "experiments"
        if experiments.is_dir():
            for path in sorted(experiments.glob("*.md")):
                check_experiment(root, project.name, path)


def check_meeting(root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    match = MEETING_FILE.fullmatch(path.name)
    if not match or not valid_date(match.group(1)):
        error(f"invalid meeting filename format: {relative}")
        return

    meeting_date = match.group(1)
    text = path.read_text(encoding="utf-8")
    meta = frontmatter(text)
    if meta is None:
        error(f"meeting frontmatter missing: {relative}")
        return
    for field in ("date", "title", "project", "visibility", "status"):
        if not meta.get(field):
            error(f"meeting field missing '{field}': {relative}")
    if meta.get("date") != meeting_date:
        error(f"meeting date does not match filename: {relative}")
    if meta.get("visibility") and meta["visibility"] not in MEETING_VISIBILITY:
        error(f"invalid meeting visibility value: {relative}")
    if meta.get("status") and meta["status"] not in MEETING_STATUSES:
        error(f"invalid meeting status value: {relative}")
    for section in ("Context", "Source summary", "Feedback", "Decisions", "Follow-ups"):
        if f"## {section}" not in text:
            error(f"meeting section missing '{section}': {relative}")

    matches = list(
        re.finditer(
            r"^### (FB-\d{4}-\d{2}-\d{2}-\d{2})\s*$\n(.*?)(?=^### |^## |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    )
    if not matches:
        error(f"meeting has no feedback entries: {relative}")
        return

    seen: set[str] = set()
    final_statuses: list[str] = []
    for item in matches:
        feedback_id, block = item.group(1), item.group(2)
        id_match = FEEDBACK_ID.fullmatch(feedback_id)
        if not id_match or id_match.group(1) != meeting_date or feedback_id in seen:
            error(f"invalid or duplicate feedback id '{feedback_id}': {relative}")
        seen.add(feedback_id)
        fields = record_fields(block)
        for field in (
            "scope",
            "kind",
            "statement",
            "source_mode",
            "status",
            "human_approved",
        ):
            if not fields.get(field):
                error(f"feedback field missing '{field}' ({feedback_id}): {relative}")
        for field in (
            "linked_artifact",
            "reason",
            "validation",
        ):
            if field not in fields:
                error(f"feedback field missing '{field}' ({feedback_id}): {relative}")

        scope = fields.get("scope", "")
        kind = fields.get("kind", "")
        source_mode = fields.get("source_mode", "")
        status = fields.get("status", "")
        approved = fields.get("human_approved", "")
        final_statuses.append(status)
        if scope and scope not in FEEDBACK_SCOPES:
            error(f"invalid feedback scope value ({feedback_id}): {relative}")
        if kind and kind not in FEEDBACK_KINDS:
            error(f"invalid feedback kind value ({feedback_id}): {relative}")
        if source_mode and source_mode not in SOURCE_MODES:
            error(f"invalid feedback source_mode value ({feedback_id}): {relative}")
        if status and status not in FEEDBACK_STATUSES:
            error(f"invalid feedback status value ({feedback_id}): {relative}")
        if approved and approved not in {"yes", "no"}:
            error(f"invalid feedback human_approved value ({feedback_id}): {relative}")

        if status == "captured" and approved == "yes":
            error(f"captured feedback is marked approved ({feedback_id}): {relative}")
        if status != "captured" and approved != "yes":
            error(f"triaged feedback has no human approval ({feedback_id}): {relative}")
        if status != "captured" and is_placeholder(fields.get("statement", "")):
            error(f"triaged feedback has no statement ({feedback_id}): {relative}")
        if status in {"accepted", "validated"}:
            artifact = linked_path(root, fields.get("linked_artifact", ""))
            if artifact is None or not artifact.is_file():
                error(f"accepted feedback links to no artifact ({feedback_id}): {relative}")
        if kind == "decision-candidate" and status in {"accepted", "validated"}:
            if not fields.get("linked_artifact", "").startswith("system/decisions.md"):
                error(f"approved decision-candidate does not point at an ADR ({feedback_id}): {relative}")
        if status in {"rejected", "deferred"} and is_placeholder(fields.get("reason", "")):
            error(f"{status} feedback has no reason ({feedback_id}): {relative}")
        if status == "validated" and is_placeholder(fields.get("validation", "")):
            error(f"validated feedback has no validation result ({feedback_id}): {relative}")

    if meta.get("status") == "closed":
        unfinished = {"captured", "accepted", "deferred"}.intersection(final_statuses)
        if unfinished:
            error(f"closed meeting still has unfinished feedback {sorted(unfinished)}: {relative}")


def check_meetings(root: Path) -> None:
    meetings = root / "feedback" / "meetings"
    if not meetings.is_dir():
        return
    for path in sorted(meetings.glob("*.md")):
        check_meeting(root, path)


def list_field(value: str) -> list[str]:
    value = (value or "").strip()
    if value in {"", "none"}:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def step_candidates(text: str) -> list[dict] | None:
    match = re.search(
        r"^## Candidate records\s*$.*?^```json\s*$\n(.*?)^```\s*$",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, list) else None


def candidates_digest(candidates: list[dict]) -> str:
    canonical = json.dumps(candidates, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def candidate_count(meta: dict) -> int:
    value = meta.get("candidates", "")
    return int(value) if is_count(value) else 0


def is_count(value: str) -> bool:
    """ASCII digits only: "²".isdigit() is true but int("²") raises."""
    return bool(re.fullmatch(r"[0-9]+", value or ""))


def check_step(path: Path, trail: str, steps: dict[str, dict], records: dict[str, dict[str, str]], relative: str) -> None:
    meta = steps[path.stem]
    for field in (
        "id", "trail", "parent", "direction", "query", "inputs", "provider", "fetched_at",
        "candidates", "excluded", "candidates_sha256", "proposed", "chosen", "chosen_by", "saved", "agent",
    ):
        if not meta.get(field):
            error(f"step field missing '{field}': {relative}")
    if meta.get("id") != path.stem:
        error(f"step id does not match filename: {relative}")
    if meta.get("trail") != trail:
        error(f"step trail does not match its directory: {relative}")
    if meta.get("direction") and meta["direction"] not in STEP_DIRECTIONS:
        error(f"invalid step direction value: {relative}")
    parent = meta.get("parent", "none")
    if parent != "none" and (parent not in steps or parent >= path.stem):
        error(f"step parent is not an earlier step of this trail: {relative}")

    candidates = step_candidates(path.read_text(encoding="utf-8"))
    if candidates is None:
        error(f"step candidate records block missing or unreadable: {relative}")
        return
    if candidates_digest(candidates) != meta.get("candidates_sha256"):
        error(f"step candidates were edited after the search (candidates_sha256 mismatch): {relative}")
    if meta.get("candidates") != str(len(candidates)):
        error(f"step candidate count does not match its records: {relative}")

    def numbers(field: str) -> list[int]:
        values = list_field(meta.get(field, ""))
        if not all(is_count(v) and 1 <= int(v) <= len(candidates) for v in values):
            error(f"step {field} names a candidate that does not exist: {relative}")
            return []
        return [int(v) for v in values]

    numbers("proposed")
    chosen = numbers("chosen")
    chosen_by = meta.get("chosen_by", "")
    if chosen and chosen_by != "human":
        error(f"step chosen without chosen_by: human (an AI pick belongs in proposed): {relative}")
    if not chosen and chosen_by not in {"none", ""}:
        error(f"step has chosen_by but nothing chosen: {relative}")
    for item in list_field(meta.get("saved", "")):
        number, _, record_id = item.partition("=")
        if not is_count(number) or int(number) not in chosen:
            error(f"step saved a candidate that was not chosen by a human ({item}): {relative}")
        if record_id not in records:
            error(f"step saved into a missing library record ({item}): {relative}")
    for token in list_field(meta.get("inputs", "")):
        ref = STEP_REF.fullmatch(token)
        if ref and (ref.group(1) not in steps or ref.group(1) >= path.stem):
            error(f"step input is not a candidate of an earlier step of this trail ({token}): {relative}")
        elif ref and not 1 <= int(ref.group(2)) <= candidate_count(steps[ref.group(1)]):
            error(f"step input names a candidate that does not exist ({token}): {relative}")
        elif not ref and not re.fullmatch(r"L\d{4}|W\d+(?:\+W\d+)*", token):
            error(f"invalid step input token ({token}): {relative}")
        elif re.fullmatch(r"L\d{4}", token) and token not in records:
            error(f"step input points at a missing library record ({token}): {relative}")


def check_library(root: Path) -> None:
    library = root / "library"
    if not library.is_dir():
        return
    records: dict[str, dict[str, str]] = {}
    for path in sorted((library / "papers").glob("*.md")):
        relative = path.relative_to(root).as_posix()
        if not RECORD_FILE.fullmatch(path.name):
            error(f"invalid library record filename: {relative}")
            continue
        meta = frontmatter(path.read_text(encoding="utf-8"))
        if meta is None:
            error(f"library record frontmatter missing: {relative}")
            continue
        records[path.stem] = meta
        for field in (
            "id", "title", "year", "venue", "venue_type", "openalex", "is_retracted", "cited_by",
            "added", "added_by", "source_step", "collections",
        ):
            if not meta.get(field):
                error(f"library record field missing '{field}': {relative}")
        if meta.get("id") != path.stem:
            error(f"library record id does not match filename: {relative}")
        if meta.get("is_retracted") and meta["is_retracted"] not in {"yes", "no"}:
            error(f"invalid library record is_retracted value: {relative}")
        venue_type = meta.get("venue_type", "")
        if venue_type and venue_type not in VENUE_TYPES:
            error(f"invalid library record venue_type value: {relative}")
        if (venue_type == "preprint") != (meta.get("venue") == "preprint-only"):
            error(f"library record venue and venue_type disagree about preprint-only: {relative}")

    collections: dict[str, list[str]] = {}
    for path in sorted((library / "collections").glob("*.md")):
        relative = path.relative_to(root).as_posix()
        if not re.fullmatch(SLUG, path.stem):
            error(f"invalid collection filename: {relative}")
            continue
        listed = re.findall(r"^- (L\d{4})\b", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
        collections[path.stem] = listed
        for record_id in listed:
            if record_id not in records:
                error(f"collection lists a missing record ({record_id}): {relative}")
            elif path.stem not in list_field(records[record_id].get("collections", "")):
                error(f"collection lists {record_id} but the record does not name this collection: {relative}")

    saved_by_step: dict[str, set[str]] = {}
    trails = library / "trails"
    for trail_dir in sorted(p for p in trails.iterdir() if p.is_dir()) if trails.is_dir() else []:
        trail = trail_dir.name
        trail_relative = trail_dir.relative_to(root).as_posix()
        if not TRAIL_DIR.fullmatch(trail):
            error(f"invalid trail directory name: {trail_relative}")
            continue
        trail_meta = frontmatter((trail_dir / "trail.md").read_text(encoding="utf-8")) if (trail_dir / "trail.md").is_file() else None
        if trail_meta is None:
            error(f"trail.md missing or without frontmatter: {trail_relative}")
            continue
        for field in ("id", "question", "seeds", "created", "agent"):
            if not trail_meta.get(field):
                error(f"trail field missing '{field}': {trail_relative}/trail.md")
        if trail_meta.get("id") != trail:
            error(f"trail id does not match its directory: {trail_relative}/trail.md")
        steps: dict[str, dict] = {}
        for path in sorted(trail_dir.glob("*.md")):
            if path.name == "trail.md":
                continue
            if not STEP_FILE.fullmatch(path.name):
                error(f"invalid step filename: {path.relative_to(root).as_posix()}")
                continue
            meta = frontmatter(path.read_text(encoding="utf-8"))
            if meta is None:
                error(f"step frontmatter missing: {path.relative_to(root).as_posix()}")
                continue
            steps[path.stem] = meta
        for step_id in sorted(steps):
            path = trail_dir / f"{step_id}.md"
            check_step(path, trail, steps, records, path.relative_to(root).as_posix())
            saved_by_step[f"{trail}/{step_id}"] = {
                item.partition("=")[2] for item in list_field(steps[step_id].get("saved", ""))
            }

    for record_id, meta in records.items():
        relative = f"library/papers/{record_id}.md"
        source = meta.get("source_step", "")
        if source and record_id not in saved_by_step.get(source, set()):
            error(f"library record was not saved by a human pick in its source_step ({source}): {relative}")
        for slug in list_field(meta.get("collections", "")):
            if record_id not in collections.get(slug, []):
                error(f"library record names collection '{slug}' that does not list it: {relative}")

    retracted = {record_id for record_id, meta in records.items() if meta.get("is_retracted") == "yes"}
    research = root / "research"
    if retracted and research.is_dir():
        for path in sorted(research.rglob("*.md")):
            if "_template" in path.parts:
                continue
            for record_id in sorted(set(LIBRARY_REF.findall(path.read_text(encoding="utf-8"))) & retracted):
                WARNINGS.append(f"cites retracted paper library:{record_id}: {path.relative_to(root).as_posix()}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"[FATAL] repository root not found: {root}", file=sys.stderr)
        return 2
    if run_core_lint(root) != 0:
        return 1

    ERRORS.clear()
    WARNINGS.clear()
    check_required(root)
    check_research_projects(root)
    check_meetings(root)
    check_library(root)
    for message in WARNINGS:
        print(f"[WARN]  {message}")
    for message in ERRORS:
        print(f"[ERROR] {message}")
    if ERRORS:
        print(f"\nresearch-lint: ERROR {len(ERRORS)}")
        return 1
    print("research-lint: clean ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
