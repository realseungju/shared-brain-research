#!/usr/bin/env python3
"""공통 brain 불변식과 연구·미팅 provenance 계약을 검사한다."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys

ERRORS: list[str] = []

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
PLACEHOLDERS = {"", "-", "todo", "tbd", "pending", "none", "n/a", "미검증"}
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
    for raw in match.group(1).splitlines():
        line = raw.strip().strip("`")
        if not line or line.casefold() in PLACEHOLDERS:
            continue
        if line.startswith("|---") or line in {"- TODO", "- [ ]"}:
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
            error(f"research 필수 디렉터리 없음: {name}")
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
            error(f"research 필수 파일 없음: {name}")


def check_experiment(root: Path, project_slug: str, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    match = EXPERIMENT_FILE.fullmatch(path.name)
    if not match or not valid_date(match.group(1)):
        error(f"experiment 파일명 형식 위반: {relative}")
        return

    experiment_id = path.stem
    text = path.read_text(encoding="utf-8")
    meta = frontmatter(text)
    if meta is None:
        error(f"experiment frontmatter 없음: {relative}")
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
            error(f"experiment 필수 필드 없음 '{field}': {relative}")

    if meta.get("id") != experiment_id:
        error(f"experiment id와 파일명 불일치: {relative}")
    if meta.get("project") != project_slug:
        error(f"experiment project와 디렉터리 불일치: {relative}")
    if meta.get("date") != match.group(1):
        error(f"experiment date와 파일명 불일치: {relative}")
    if meta.get("status") and meta["status"] not in EXPERIMENT_STATUSES:
        error(f"experiment status 값 불량: {relative}")
    if meta.get("evidence_kind") and meta["evidence_kind"] not in EVIDENCE_KINDS:
        error(f"experiment evidence_kind 값 불량: {relative}")

    for section in ("연구 질문", "가설", "계획", "실행 조건", "결과", "해석", "한계", "다음 단계"):
        if f"## {section}" not in text:
            error(f"experiment 섹션 없음 '{section}': {relative}")

    if meta.get("status") in CLOSED_EXPERIMENT_STATUSES:
        for field in (
            "hypothesis",
            "dataset_version",
            "code_commit",
            "seed_or_repeats",
            "artifact",
        ):
            if is_placeholder(meta.get(field, "")):
                error(f"닫힌 experiment 재현 필드 미완 '{field}': {relative}")
        if meta.get("evidence_kind") == "unverified":
            error(f"닫힌 experiment evidence_kind가 unverified: {relative}")
        if not COMMIT_REF.fullmatch(meta.get("code_commit", "")):
            error(f"닫힌 experiment code_commit 형식 불량: {relative}")
        for section in ("결과", "해석", "한계"):
            if not section_has_content(text, section):
                error(f"닫힌 experiment 내용 없음 '{section}': {relative}")


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
            error(f"claim id 불량 또는 중복 '{claim_id}': {relative}")
        seen.add(claim_id)
        fields = record_fields(block)
        for field in ("statement", "status", "evidence", "evidence_kind", "human_reviewed"):
            if not fields.get(field):
                error(f"claim 필수 필드 없음 '{field}' ({claim_id}): {relative}")

        status = fields.get("status", "")
        evidence_kind = fields.get("evidence_kind", "")
        reviewed = fields.get("human_reviewed", "")
        if status and status not in CLAIM_STATUSES:
            error(f"claim status 값 불량 ({claim_id}): {relative}")
        if evidence_kind and evidence_kind not in EVIDENCE_KINDS:
            error(f"claim evidence_kind 값 불량 ({claim_id}): {relative}")
        if reviewed and reviewed not in {"yes", "no"}:
            error(f"claim human_reviewed 값 불량 ({claim_id}): {relative}")

        if status == "supported":
            if is_placeholder(fields.get("statement", "")):
                error(f"supported claim statement 없음 ({claim_id}): {relative}")
            if reviewed != "yes":
                error(f"supported claim 사람 검토 없음 ({claim_id}): {relative}")
            if evidence_kind not in {"measured", "estimated"}:
                error(f"supported claim 근거가 unverified ({claim_id}): {relative}")
            evidence = linked_path(root, fields.get("evidence", ""))
            if evidence is None or not evidence.is_file():
                error(f"supported claim 근거 경로 없음 ({claim_id}): {relative}")
            else:
                expected = (root / "research" / project_slug / "experiments").resolve()
                try:
                    evidence.resolve().relative_to(expected)
                except ValueError:
                    error(f"supported claim 근거가 project experiment 밖임 ({claim_id}): {relative}")
        if status == "rejected":
            if is_placeholder(fields.get("statement", "")):
                error(f"rejected claim statement 없음 ({claim_id}): {relative}")
            if reviewed != "yes":
                error(f"rejected claim 사람 검토 없음 ({claim_id}): {relative}")
            if is_placeholder(fields.get("reason", "")):
                error(f"rejected claim 이유 없음 ({claim_id}): {relative}")

    if not matches:
        error(f"claim 항목 없음: {relative}")


def check_research_projects(root: Path) -> None:
    research = root / "research"
    if not research.is_dir():
        return
    for project in sorted(research.iterdir()):
        if not project.is_dir() or project.name.startswith("_"):
            continue
        if not re.fullmatch(SLUG, project.name):
            error(f"research project slug 형식 위반: {project.relative_to(root).as_posix()}")
            continue
        for name in ("overview.md", "questions.md", "claims.md", "experiments"):
            target = project / name
            if name == "experiments":
                if not target.is_dir():
                    error(f"research project 필수 디렉터리 없음: {target.relative_to(root).as_posix()}")
            elif not target.is_file():
                error(f"research project 필수 파일 없음: {target.relative_to(root).as_posix()}")
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
        error(f"meeting 파일명 형식 위반: {relative}")
        return

    meeting_date = match.group(1)
    text = path.read_text(encoding="utf-8")
    meta = frontmatter(text)
    if meta is None:
        error(f"meeting frontmatter 없음: {relative}")
        return
    for field in ("date", "title", "project", "visibility", "status"):
        if not meta.get(field):
            error(f"meeting 필수 필드 없음 '{field}': {relative}")
    if meta.get("date") != meeting_date:
        error(f"meeting date와 파일명 불일치: {relative}")
    if meta.get("visibility") and meta["visibility"] not in MEETING_VISIBILITY:
        error(f"meeting visibility 값 불량: {relative}")
    if meta.get("status") and meta["status"] not in MEETING_STATUSES:
        error(f"meeting status 값 불량: {relative}")
    for section in ("맥락", "출처 요약", "Feedback", "확정된 결정", "후속 링크"):
        if f"## {section}" not in text:
            error(f"meeting 섹션 없음 '{section}': {relative}")

    matches = list(
        re.finditer(
            r"^### (FB-\d{4}-\d{2}-\d{2}-\d{2})\s*$\n(.*?)(?=^### |^## |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    )
    if not matches:
        error(f"meeting feedback 항목 없음: {relative}")
        return

    seen: set[str] = set()
    final_statuses: list[str] = []
    for item in matches:
        feedback_id, block = item.group(1), item.group(2)
        id_match = FEEDBACK_ID.fullmatch(feedback_id)
        if not id_match or id_match.group(1) != meeting_date or feedback_id in seen:
            error(f"feedback id 불량 또는 중복 '{feedback_id}': {relative}")
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
                error(f"feedback 필수 필드 없음 '{field}' ({feedback_id}): {relative}")
        for field in (
            "linked_artifact",
            "validation",
        ):
            if field not in fields:
                error(f"feedback 필수 필드 없음 '{field}' ({feedback_id}): {relative}")

        scope = fields.get("scope", "")
        kind = fields.get("kind", "")
        source_mode = fields.get("source_mode", "")
        status = fields.get("status", "")
        approved = fields.get("human_approved", "")
        final_statuses.append(status)
        if scope and scope not in FEEDBACK_SCOPES:
            error(f"feedback scope 값 불량 ({feedback_id}): {relative}")
        if kind and kind not in FEEDBACK_KINDS:
            error(f"feedback kind 값 불량 ({feedback_id}): {relative}")
        if source_mode and source_mode not in SOURCE_MODES:
            error(f"feedback source_mode 값 불량 ({feedback_id}): {relative}")
        if status and status not in FEEDBACK_STATUSES:
            error(f"feedback status 값 불량 ({feedback_id}): {relative}")
        if approved and approved not in {"yes", "no"}:
            error(f"feedback human_approved 값 불량 ({feedback_id}): {relative}")

        if status == "captured" and approved == "yes":
            error(f"captured feedback가 승인 상태임 ({feedback_id}): {relative}")
        if status != "captured" and approved != "yes":
            error(f"triage된 feedback 사람 승인 없음 ({feedback_id}): {relative}")
        if status != "captured" and is_placeholder(fields.get("statement", "")):
            error(f"triage된 feedback statement 없음 ({feedback_id}): {relative}")
        if status in {"accepted", "validated"}:
            artifact = linked_path(root, fields.get("linked_artifact", ""))
            if artifact is None or not artifact.is_file():
                error(f"accepted feedback 연결 산출물 없음 ({feedback_id}): {relative}")
        if kind == "decision-candidate" and status in {"accepted", "validated"}:
            if not fields.get("linked_artifact", "").startswith("system/decisions.md"):
                error(f"승인된 decision-candidate가 ADR을 가리키지 않음 ({feedback_id}): {relative}")
        if status == "validated" and is_placeholder(fields.get("validation", "")):
            error(f"validated feedback 검증 결과 없음 ({feedback_id}): {relative}")

    if meta.get("status") == "closed":
        unfinished = {"captured", "accepted", "deferred"}.intersection(final_statuses)
        if unfinished:
            error(f"closed meeting에 미종결 feedback 존재 {sorted(unfinished)}: {relative}")


def check_meetings(root: Path) -> None:
    meetings = root / "feedback" / "meetings"
    if not meetings.is_dir():
        return
    for path in sorted(meetings.glob("*.md")):
        check_meeting(root, path)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"[FATAL] 저장소 루트 없음: {root}", file=sys.stderr)
        return 2
    if run_core_lint(root) != 0:
        return 1

    ERRORS.clear()
    check_required(root)
    check_research_projects(root)
    check_meetings(root)
    for message in ERRORS:
        print(f"[ERROR] {message}")
    if ERRORS:
        print(f"\nresearch-lint: ERROR {len(ERRORS)}")
        return 1
    print("research-lint: 클린 ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
