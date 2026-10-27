#!/usr/bin/env python3
"""Paper library and exploration trails.

The library keeps only papers a human chose. A trail records every search step — inputs,
direction, candidates, and what was picked — so another agent can continue from any step.
Metadata comes from OpenAlex. Preprint and published versions are merged into one record and
the published version is shown first.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TRAIL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
RECORD_RE = re.compile(r"^L(\d{4})$")
STEP_RE = re.compile(r"^step-(\d{2})$")
STEP_REF_RE = re.compile(r"^(step-\d{2})#(\d+)$")
WORK_RE = re.compile(r"^W\d+$")
WORK_GROUP_RE = re.compile(r"^W\d+(?:\+W\d+)*$")
ARXIV_DOI_RE = re.compile(r"^10\.48550/arxiv\.(.+)$", re.IGNORECASE)
ARXIV_URL_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([^/?#]+?)(?:v\d+)?(?:\.pdf)?$", re.IGNORECASE)

DIRECTIONS = ("search", "references", "citations", "related")
PUBLISHED_SOURCE_TYPES = {"journal": "journal", "conference": "conference", "book series": "other", "ebook platform": "other"}
OPENALEX = "https://api.openalex.org"
SELECT = ",".join((
    "id", "doi", "display_name", "publication_year", "cited_by_count", "is_retracted", "type",
    "authorships", "primary_location", "locations", "referenced_works", "related_works",
))
DEFAULT_LIMIT = 25
CITATIONS_PER_INPUT = 200
BATCH = 50
CANDIDATES_HEADING = "## Candidate records"


class ProviderError(RuntimeError):
    pass


class UsageError(ValueError):
    pass


# ---------------------------------------------------------------- provider


class OpenAlex:
    """Keyless works, but a free key raises the daily budget. The key is read from the
    environment and never written to a file."""

    def __init__(self, api_key: str | None = None, mailto: str | None = None, timeout: int = 30) -> None:
        self.api_key = api_key
        self.mailto = mailto
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, str]) -> dict:
        query = dict(params)
        if self.api_key:
            query["api_key"] = self.api_key
        if self.mailto:
            query["mailto"] = self.mailto
        url = f"{OPENALEX}{path}" + (f"?{urllib.parse.urlencode(query)}" if query else "")
        request = urllib.request.Request(url, headers={"User-Agent": "shared-brain-research-library/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            hint = " (daily budget used up? set OPENALEX_API_KEY)" if exc.code in {402, 429} else ""
            raise ProviderError(f"OpenAlex HTTP {exc.code} on {path}{hint}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderError(f"OpenAlex unreachable on {path}: {exc}") from exc

    def work(self, ref: str) -> dict:
        return self._get(f"/works/{urllib.parse.quote(ref, safe=':/')}", {})

    def works_by_ids(self, ids: list[str]) -> list[dict]:
        works: list[dict] = []
        for start in range(0, len(ids), BATCH):
            chunk = ids[start:start + BATCH]
            page = self._get("/works", {
                "filter": "openalex:" + "|".join(chunk),
                "per-page": str(len(chunk)),
                "select": SELECT,
            })
            works.extend(page.get("results", []))
        return works

    def citing(self, work_id: str, limit: int) -> list[dict]:
        page = self._get("/works", {
            "filter": f"cites:{work_id}",
            "sort": "cited_by_count:desc",
            "per-page": str(min(limit, 200)),
            "select": SELECT,
        })
        return page.get("results", [])

    def search(self, query: str, limit: int) -> list[dict]:
        page = self._get("/works", {"search": query, "per-page": str(min(limit, 200)), "select": SELECT})
        return page.get("results", [])

    def title_matches(self, title: str) -> list[dict]:
        cleaned = re.sub(r"[,|:]", " ", title)
        page = self._get("/works", {"filter": f"title.search:{cleaned}", "per-page": "10", "select": SELECT})
        return page.get("results", [])


def default_provider() -> OpenAlex:
    return OpenAlex(os.environ.get("OPENALEX_API_KEY") or None, os.environ.get("OPENALEX_MAILTO") or None)


# ---------------------------------------------------------------- versions and identity


def short_id(value: str | None) -> str:
    return (value or "").rstrip("/").rsplit("/", 1)[-1]


def clean_doi(value: str | None) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", (value or "").strip(), flags=re.IGNORECASE).lower()


def norm_title(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^0-9a-zA-Z]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def work_locations(work: dict) -> list[dict]:
    locations = [work.get("primary_location") or {}]
    locations.extend(work.get("locations") or [])
    return [loc for loc in locations if loc]


def arxiv_id(work: dict) -> str:
    match = ARXIV_DOI_RE.match(clean_doi(work.get("doi")))
    if match:
        return match.group(1)
    for loc in work_locations(work):
        for key in ("landing_page_url", "pdf_url"):
            found = ARXIV_URL_RE.search(loc.get(key) or "")
            if found:
                return found.group(1)
    return ""


def published_source(work: dict) -> tuple[str, str]:
    """The first non-repository venue, or ("", "") when only a preprint exists."""
    for loc in work_locations(work):
        source = loc.get("source") or {}
        kind = PUBLISHED_SOURCE_TYPES.get(source.get("type") or "")
        name = (source.get("display_name") or "").strip()
        if kind and name and "arxiv" not in name.lower():
            return name, kind
    return "", ""


def version_of(work: dict) -> dict:
    doi = clean_doi(work.get("doi"))
    venue, venue_type = published_source(work)
    return {
        "openalex": short_id(work.get("id")),
        "kind": "published" if venue else "preprint",
        "doi": "" if ARXIV_DOI_RE.match(doi) else doi,
        "arxiv": arxiv_id(work),
        "venue": venue,
        "venue_type": venue_type,
        "year": work.get("publication_year"),
        "cited_by": work.get("cited_by_count") or 0,
        "is_retracted": bool(work.get("is_retracted")),
    }


def work_authors(work: dict) -> tuple[list[str], int]:
    names = [
        ((a.get("author") or {}).get("display_name") or "").strip()
        for a in work.get("authorships") or []
    ]
    names = [n for n in names if n]
    return names[:3], len(names)


def matches(entry: dict, version: dict, title_key: str) -> bool:
    """Same paper? Shared IDs first. A matching title links versions only when the two do not
    carry different published DOIs — otherwise two distinct papers with one title would fold."""
    if version["openalex"] and version["openalex"] in entry["openalex"]:
        return True
    if version["doi"] and version["doi"] in entry["dois"]:
        return True
    if version["arxiv"] and version["arxiv"] in entry["arxivs"]:
        return True
    if title_key and title_key == entry["norm"]:
        if version["doi"] and entry["dois"] and version["doi"] not in entry["dois"]:
            return False
        years = [v["year"] for v in entry.get("versions", []) if v.get("year")]
        return not (version["year"] and years and min(abs(version["year"] - y) for y in years) > 2)
    return False


def new_entry(work: dict) -> dict:
    authors, n_authors = work_authors(work)
    title = work.get("display_name") or work.get("title") or ""
    return {
        "title": title, "norm": norm_title(title), "authors": authors, "n_authors": n_authors,
        "versions": [], "openalex": set(), "dois": set(), "arxivs": set(), "via": set(), "rank": None,
    }


def add_version(entry: dict, version: dict) -> None:
    if version["openalex"] in entry["openalex"]:
        return
    entry["versions"].append(version)
    entry["openalex"].add(version["openalex"])
    if version["doi"]:
        entry["dois"].add(version["doi"])
    if version["arxiv"]:
        entry["arxivs"].add(version["arxiv"])


def merge_work(pool: list[dict], work: dict, via: str | None, rank: int | None = None) -> dict:
    version = version_of(work)
    title_key = norm_title(work.get("display_name") or work.get("title") or "")
    entry = next((e for e in pool if matches(e, version, title_key)), None)
    if entry is None:
        entry = new_entry(work)
        pool.append(entry)
    add_version(entry, version)
    if not entry["authors"]:
        entry["authors"], entry["n_authors"] = work_authors(work)
    if via:
        entry["via"].add(via)
    if rank is not None and (entry["rank"] is None or rank < entry["rank"]):
        entry["rank"] = rank
    return entry


def with_published_versions(provider: OpenAlex, ids: list[str], works: dict[str, dict]) -> list[str]:
    """An arXiv record in OpenAlex often has no references and a fraction of the citations of
    its published version. When a paper is known only by preprint IDs, look up the published
    version by exact title and use both."""
    group = [works[i] for i in ids if i in works]
    if not group or any(version_of(w)["kind"] == "published" for w in group):
        return ids
    entry = new_entry(group[0])
    for w in group:
        add_version(entry, version_of(w))
    found = list(ids)
    for w in provider.title_matches(entry["title"]):
        version = version_of(w)
        if version["openalex"] not in found and matches(entry, version, norm_title(w.get("display_name") or "")):
            add_version(entry, version)
            works[version["openalex"]] = w
            found.append(version["openalex"])
    return found


def summarize(entry: dict) -> dict:
    """Display fields: the published version wins; preprint-only is stated, not hidden."""
    published = [v for v in entry["versions"] if v["kind"] == "published"]
    lead = published[0] if published else entry["versions"][0]
    years = [v["year"] for v in entry["versions"] if v["year"]]
    arxivs = sorted(entry["arxivs"])
    return {
        "title": entry["title"],
        "year": lead["year"] or (min(years) if years else None),
        "authors": entry["authors"],
        "n_authors": entry["n_authors"],
        "venue": lead["venue"] if published else "preprint-only",
        "venue_type": lead["venue_type"] if published else "preprint",
        "doi": lead["doi"] if published else "",
        "arxiv": arxivs[0] if arxivs else "",
        "openalex": [v["openalex"] for v in entry["versions"]],
        "cited_by": sum(v["cited_by"] for v in entry["versions"]),
        "connections": len(entry["via"]),
        "is_retracted": any(v["is_retracted"] for v in entry["versions"]),
        "versions": entry["versions"],
    }


# ---------------------------------------------------------------- files


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise UsageError("frontmatter missing")
    meta: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[index + 1:]) + "\n"
        match = re.match(r"^([A-Za-z0-9_]+):[ \t]*(.*)$", line)
        if match:
            meta[match.group(1)] = match.group(2).strip()
    raise UsageError("frontmatter not closed")


def render(meta: dict[str, str], body: str) -> str:
    head = "\n".join(f"{key}: {value}" for key, value in meta.items())
    return f"---\n{head}\n---\n{body}"


def read_md(path: Path) -> tuple[dict[str, str], str]:
    return frontmatter(path.read_text(encoding="utf-8"))


def write_md(path: Path, meta: dict[str, str], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(meta, body), encoding="utf-8", newline="\n")


def split_list(value: str) -> list[str]:
    value = (value or "").strip()
    if value in {"", "none"}:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def join_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def one_line(value: str, field: str) -> str:
    result = (value or "").strip()
    if not result or "\n" in result or "\r" in result:
        raise UsageError(f"{field} must be a single non-empty line")
    return result


def candidates_digest(candidates: list[dict]) -> str:
    canonical = json.dumps(candidates, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def read_candidates(text: str) -> list[dict]:
    match = re.search(
        rf"^{re.escape(CANDIDATES_HEADING)}\s*$.*?^```json\s*$\n(.*?)^```\s*$",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise UsageError("candidate records block missing")
    return json.loads(match.group(1))


def cell(value: object) -> str:
    return str(value if value not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


class Library:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.dir = root / "library"
        self.papers = self.dir / "papers"
        self.collections = self.dir / "collections"
        self.trails = self.dir / "trails"

    # records

    def records(self) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {}
        if self.papers.is_dir():
            for path in sorted(self.papers.glob("L*.md")):
                meta, _ = read_md(path)
                result[meta.get("id", path.stem)] = meta
        return result

    def record_entries(self) -> list[tuple[str, dict]]:
        entries = []
        for record_id, meta in self.records().items():
            entries.append((record_id, {
                "norm": norm_title(meta.get("title", "")),
                "openalex": set(split_list(meta.get("openalex", ""))),
                "dois": {meta["doi"]} if meta.get("doi", "none") != "none" else set(),
                "arxivs": {meta["arxiv"]} if meta.get("arxiv", "none") != "none" else set(),
            }))
        return entries

    def find_record(self, candidate: dict) -> str | None:
        title_key = norm_title(candidate["title"])
        for record_id, entry in self.record_entries():
            for version in candidate["versions"]:
                if matches(entry, version, title_key):
                    return record_id
        return None

    def next_record_id(self) -> str:
        numbers = [int(m.group(1)) for m in (RECORD_RE.match(k) for k in self.records()) if m]
        return f"L{(max(numbers) + 1) if numbers else 1:04d}"

    def write_record(self, record_id: str, data: dict, meta_extra: dict[str, str], notes: str) -> None:
        authors = "; ".join(data["authors"]) or "unknown"
        if data["n_authors"] > len(data["authors"]):
            authors += f" (+{data['n_authors'] - len(data['authors'])})"
        meta = {
            "id": record_id,
            "title": one_line(data["title"], "title"),
            "year": str(data["year"] or "unknown"),
            "authors": authors,
            "venue": data["venue"],
            "venue_type": data["venue_type"],
            "doi": data["doi"] or "none",
            "arxiv": data["arxiv"] or "none",
            "openalex": join_list(data["openalex"]),
            "is_retracted": "yes" if data["is_retracted"] else "no",
            "cited_by": str(data["cited_by"]),
        }
        meta.update(meta_extra)
        rows = "\n".join(
            f"| {v['kind']} | {cell(v['venue'] or 'arXiv' if v['arxiv'] else v['venue'])} | {cell(v['year'])} "
            f"| {cell(('doi:' + v['doi']) if v['doi'] else ('arxiv:' + v['arxiv']) if v['arxiv'] else '')} "
            f"| {v['openalex']} | {v['cited_by']} |"
            for v in data["versions"]
        )
        retracted = "\n> **Retracted.** Keep the record, but do not cite it as support.\n" if data["is_retracted"] else ""
        body = (
            f"\n# {data['title']}\n{retracted}\n## Versions\n\n"
            "| kind | venue | year | id | openalex | cited by |\n|---|---|---|---|---|---|\n"
            f"{rows}\n\n## Notes\n{notes}"
        )
        write_md(self.papers / f"{record_id}.md", meta, body)

    # collections

    def add_to_collection(self, slug: str, record_id: str, title: str, year: object, source: str) -> None:
        path = self.collections / f"{slug}.md"
        if path.is_file():
            meta, body = read_md(path)
        else:
            meta = {"slug": slug, "title": slug, "project": "none"}
            body = f"\n# {slug}\n\n## Papers\n\n"
        if re.search(rf"^- {record_id}\b", body, flags=re.MULTILINE):
            return
        line = f"- {record_id} — {title} ({year or 'n.d.'}) — from {source}\n"
        body = body if body.endswith("\n") else body + "\n"
        write_md(path, meta, body + line)

    def collection_ids(self, slug: str) -> list[str]:
        path = self.collections / f"{slug}.md"
        if not path.is_file():
            raise UsageError(f"collection not found: library/collections/{slug}.md")
        _, body = read_md(path)
        return re.findall(r"^- (L\d{4})\b", body, flags=re.MULTILINE)

    # trails

    def trail_dir(self, trail: str) -> Path:
        path = self.trails / trail
        if not (path / "trail.md").is_file():
            raise UsageError(f"trail not found: library/trails/{trail}/trail.md")
        return path

    def steps(self, trail: str) -> list[str]:
        return sorted(p.stem for p in self.trail_dir(trail).glob("step-*.md") if STEP_RE.match(p.stem))

    def step(self, trail: str, step_id: str) -> tuple[dict[str, str], str, list[dict]]:
        path = self.trail_dir(trail) / f"{step_id}.md"
        if not path.is_file():
            raise UsageError(f"step not found: {trail}/{step_id}")
        text = path.read_text(encoding="utf-8")
        meta, body = frontmatter(text)
        return meta, body, read_candidates(text)

    def resolve_inputs(self, trail: str, tokens: list[str]) -> list[tuple[str, list[str]]]:
        """Each input is one paper: a record (all its versions), a work, or a candidate picked
        in an earlier step."""
        records = self.records()
        resolved = []
        for token in tokens:
            if RECORD_RE.match(token):
                if token not in records:
                    raise UsageError(f"input record not found: {token}")
                resolved.append((token, split_list(records[token].get("openalex", ""))))
            elif WORK_GROUP_RE.match(token):
                resolved.append((token, token.split("+")))
            elif STEP_REF_RE.match(token):
                step_id, number = STEP_REF_RE.match(token).groups()
                _, _, candidates = self.step(trail, step_id)
                index = int(number) - 1
                if not 0 <= index < len(candidates):
                    raise UsageError(f"no candidate {number} in {trail}/{step_id}")
                resolved.append((token, list(candidates[index]["openalex"])))
            else:
                raise UsageError(f"unknown input token: {token}")
        return resolved


def seed_ref(seed: str) -> str:
    seed = seed.strip()
    if seed.lower().startswith("doi:"):
        return f"doi:{clean_doi(seed[4:])}"
    if seed.lower().startswith("arxiv:"):
        return f"doi:10.48550/arXiv.{seed[6:].strip()}"
    if seed.lower().startswith("openalex:"):
        return short_id(seed[9:])
    if WORK_RE.match(seed):
        return seed
    raise UsageError(f"seed must be doi:, arxiv:, or openalex:W…: {seed}")


def parse_years(value: str | None) -> tuple[int | None, int | None]:
    if not value:
        return None, None
    match = re.fullmatch(r"(\d{4})?-(\d{4})?|(\d{4})", value.strip())
    if not match:
        raise UsageError(f"--year must look like 2020-, -2019, 2020-2024, or 2023: {value}")
    if match.group(3):
        return int(match.group(3)), int(match.group(3))
    low, high = match.group(1), match.group(2)
    return (int(low) if low else None), (int(high) if high else None)


def parse_numbers(value: str, upper: int) -> list[int]:
    numbers = sorted({int(part) for part in value.split(",") if part.strip()})
    bad = [n for n in numbers if not 1 <= n <= upper]
    if not numbers or bad:
        raise UsageError(f"--pick must be candidate numbers between 1 and {upper}")
    return numbers


# ---------------------------------------------------------------- commands


def cmd_trail_new(lib: Library, provider: OpenAlex, args: argparse.Namespace) -> int:
    if not SLUG_RE.fullmatch(args.slug):
        raise UsageError("slug must be lowercase letters, digits, and hyphens")
    trail = f"{args.date or date.today().isoformat()}-{args.slug}"
    path = lib.trails / trail / "trail.md"
    if path.exists():
        raise UsageError(f"already exists: library/trails/{trail}/trail.md")
    question = one_line(args.question, "question")
    seeds: list[str] = []
    labels: list[str] = []
    for seed in args.seed or []:
        work = provider.work(seed_ref(seed))
        work_id = short_id(work.get("id"))
        group = "+".join(with_published_versions(provider, [work_id], {work_id: work}))
        seeds.append(group)
        added = f" (+ published version {group.split('+', 1)[1]})" if "+" in group else ""
        labels.append(f"- {group} — {work.get('display_name') or ''} ({work.get('publication_year') or 'n.d.'}) ← `{seed}`{added}")
    for slug in args.collection or []:
        for record_id in lib.collection_ids(slug):
            if record_id not in seeds:
                seeds.append(record_id)
                labels.append(f"- {record_id} — from collection `{slug}`")
    meta = {
        "id": trail,
        "question": question,
        "project": args.project or "none",
        "seeds": join_list(seeds),
        "created": args.date or date.today().isoformat(),
        "agent": one_line(args.agent, "agent"),
    }
    body = (
        f"\n# {question}\n\n## Seeds\n\n" + ("\n".join(labels) if labels else "- none (start with a search step)")
        + "\n\n## Steps\n\n"
    )
    write_md(path, meta, body)
    print(f"✓ trail created: library/trails/{trail}/trail.md")
    return 0


def gather(provider: OpenAlex, direction: str, inputs: list[tuple[str, list[str]]],
           input_works: dict[str, dict], query: str | None, limit: int) -> list[dict]:
    pool: list[dict] = []
    if direction == "search":
        for rank, work in enumerate(provider.search(query or "", limit * 2), start=1):
            merge_work(pool, work, None, rank)
        return pool
    neighbours: dict[str, set[str]] = {}
    citing_works: dict[str, dict] = {}
    for token, ids in inputs:
        found: set[str] = set()
        for work_id in ids:
            if direction == "citations":
                for work in provider.citing(work_id, CITATIONS_PER_INPUT):
                    citing_works[short_id(work.get("id"))] = work
                    found.add(short_id(work.get("id")))
            else:
                field = "referenced_works" if direction == "references" else "related_works"
                found.update(short_id(ref) for ref in (input_works.get(work_id) or {}).get(field) or [])
        for work_id in found:
            neighbours.setdefault(work_id, set()).add(token)
    if direction == "citations":
        works = list(citing_works.values())
    else:
        works = provider.works_by_ids(sorted(neighbours))
    for work in works:
        work_id = short_id(work.get("id"))
        entry = merge_work(pool, work, None)
        entry["via"].update(neighbours.get(work_id, set()))
    return pool


def cmd_step(lib: Library, provider: OpenAlex, args: argparse.Namespace) -> int:
    trail_dir = lib.trail_dir(args.trail)
    trail_meta, trail_body = read_md(trail_dir / "trail.md")
    existing = lib.steps(args.trail)
    step_id = f"step-{(int(existing[-1][5:]) + 1) if existing else 1:02d}"
    if args.direction == "search":
        if not args.query:
            raise UsageError("a search step needs --query")
        tokens: list[str] = []
    else:
        if args.query:
            raise UsageError("--query is only for --direction search")
        if args.parent:
            parent_meta, _, _ = lib.step(args.trail, args.parent)
            chosen = [f"{args.parent}#{n}" for n in split_list(parent_meta.get("chosen", ""))]
            tokens = split_list(parent_meta.get("inputs", "")) + chosen
        else:
            tokens = split_list(trail_meta.get("seeds", ""))
        tokens += [t for t in (args.add or []) if t not in tokens]
        if not tokens:
            raise UsageError("no inputs: pick candidates in the parent step, pass --add, or seed the trail")
    low, high = parse_years(args.year)
    inputs = lib.resolve_inputs(args.trail, tokens)
    input_works: dict[str, dict] = {}
    if inputs:
        all_ids = [work_id for _, ids in inputs for work_id in ids]
        input_works = {short_id(w.get("id")): w for w in provider.works_by_ids(all_ids)}
        inputs = [(token, with_published_versions(provider, ids, input_works)) for token, ids in inputs]

    pool = gather(provider, args.direction, inputs, input_works, args.query, args.limit)

    input_ids = {work_id for _, ids in inputs for work_id in ids}
    input_records = {t for t, _ in inputs if RECORD_RE.match(t)}
    excluded: dict[str, int] = {}
    kept: list[dict] = []
    for entry in pool:
        data = summarize(entry)
        data["library"] = lib.find_record(data) or ""
        reason = None
        if input_ids & entry["openalex"] or data["library"] in input_records:
            reason = "input"
        elif data["is_retracted"] and not args.include_retracted:
            reason = "retracted"
        elif args.exclude_preprint_only and data["venue_type"] == "preprint":
            reason = "preprint-only"
        elif (low and (data["year"] or 0) < low) or (high and (data["year"] or 9999) > high):
            reason = "year"
        if reason:
            excluded[reason] = excluded.get(reason, 0) + 1
            continue
        data["rank"] = entry["rank"]
        kept.append(data)
    if args.direction == "search":
        kept.sort(key=lambda d: (d["rank"] or 0, d["title"]))
    else:
        kept.sort(key=lambda d: (-d["connections"], -d["cited_by"], -(d["year"] or 0), d["title"]))
    if len(kept) > args.limit:
        excluded["beyond-limit"] = len(kept) - args.limit
        kept = kept[:args.limit]

    candidates = []
    for number, data in enumerate(kept, start=1):
        data.pop("rank", None)
        candidates.append({"n": number, **data})

    filters = ["exclude-retracted" if not args.include_retracted else "include-retracted"]
    if args.exclude_preprint_only:
        filters.append("exclude-preprint-only")
    if args.year:
        filters.append(f"year {args.year}")
    if args.direction == "citations":
        filters.append(f"top {CITATIONS_PER_INPUT} citing works per input by citations")
    meta = {
        "id": step_id,
        "trail": args.trail,
        "parent": args.parent or "none",
        "direction": args.direction,
        "query": one_line(args.query, "query") if args.query else "none",
        "inputs": join_list(tokens),
        "input_versions": join_list(["+".join(ids) for _, ids in inputs]),
        "filters": "; ".join(filters),
        "provider": "openalex",
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pool": str(len(pool)),
        "candidates": str(len(candidates)),
        "excluded": join_list([f"{k}={v}" for k, v in sorted(excluded.items())]),
        "candidates_sha256": candidates_digest(candidates),
        "proposed": "none",
        "chosen": "none",
        "chosen_by": "none",
        "saved": "none",
        "agent": one_line(args.agent, "agent"),
    }
    rows = "\n".join(
        f"| {c['n']} | {cell(c['title'])} | {cell(c['year'])} | {cell(c['venue'])} | {c['connections']} "
        f"| {c['cited_by']} | {cell(c['library'])} |"
        for c in candidates
    )
    origin = f" ← {args.parent}" if args.parent else ""
    body = (
        f"\n# {step_id} · {args.direction}{origin}\n\n"
        f"Inputs: {join_list(tokens)}" + (f" · query `{args.query}`" if args.query else "") + "\n"
        + (f"OpenAlex works used: {meta['input_versions']}\n" if inputs else "") + "\n"
        "`links` = how many inputs this paper connects to. `venue` shows the published version; "
        "`preprint-only` means no published version was found.\n\n"
        "## Candidates\n\n| # | title | year | venue | links | cited by | library |\n|---|---|---|---|---|---|---|\n"
        f"{rows}\n\n{CANDIDATES_HEADING}\n\n"
        "Written by `infra/library.py`. Do not edit — research-lint checks `candidates_sha256`.\n\n"
        f"```json\n{json.dumps(candidates, ensure_ascii=False, indent=1)}\n```\n"
    )
    write_md(trail_dir / f"{step_id}.md", meta, body)
    line = (
        f"- {step_id}{origin or ' ← seeds' if args.direction != 'search' else origin} · {args.direction}"
        f" · {len(candidates)} candidates · {meta['agent']}\n"
    )
    write_md(trail_dir / "trail.md", trail_meta, trail_body + line)
    print(f"✓ step created: library/trails/{args.trail}/{step_id}.md ({len(candidates)} candidates, excluded {meta['excluded']})")
    if not pool:
        print(f"  ! OpenAlex returned no {args.direction} for these inputs — the record may lack them; try another direction")
    return 0


def cmd_choose(lib: Library, provider: OpenAlex, args: argparse.Namespace) -> int:
    path = lib.trail_dir(args.trail) / f"{args.step}.md"
    meta, body, candidates = lib.step(args.trail, args.step)
    picks = parse_numbers(args.pick, len(candidates))
    agent = one_line(args.agent, "agent")
    if args.by == "ai":
        if args.save:
            raise UsageError("only a human pick can be saved to the library; an AI pick stays proposed")
        proposed = sorted({int(n) for n in split_list(meta.get("proposed", ""))} | set(picks))
        meta["proposed"] = join_list([str(n) for n in proposed])
        write_md(path, meta, body)
        print(f"✓ proposed {', '.join(map(str, picks))} in {args.trail}/{args.step} (not chosen until a human picks)")
        return 0

    chosen = sorted({int(n) for n in split_list(meta.get("chosen", ""))} | set(picks))
    meta["chosen"] = join_list([str(n) for n in chosen])
    meta["chosen_by"] = "human"
    if args.save:
        if not SLUG_RE.fullmatch(args.save):
            raise UsageError("collection slug must be lowercase letters, digits, and hyphens")
        saved = dict(item.split("=", 1) for item in split_list(meta.get("saved", "")))
        source = f"{args.trail}/{args.step}"
        today = date.today().isoformat()
        for number in picks:
            data = candidates[number - 1]
            record_id = lib.find_record(data)
            if record_id:
                old, old_body = read_md(lib.papers / f"{record_id}.md")
                collections = split_list(old.get("collections", ""))
                if args.save not in collections:
                    collections.append(args.save)
                old["collections"] = join_list(collections)
                known = set(split_list(old.get("openalex", "")))
                new_ids = [i for i in data["openalex"] if i not in known]
                if new_ids:
                    old["openalex"] = join_list(split_list(old.get("openalex", "")) + new_ids)
                write_md(lib.papers / f"{record_id}.md", old, old_body)
                print(f"  {number} → {record_id} (already in the library; collection added)")
            else:
                record_id = lib.next_record_id()
                lib.write_record(record_id, data, {
                    "added": today,
                    "added_by": agent,
                    "source_step": source,
                    "collections": args.save,
                    "refreshed": today,
                }, "\n")
                print(f"  {number} → {record_id} (new record)")
            saved[str(number)] = record_id
            lib.add_to_collection(args.save, record_id, data["title"], data["year"], source)
        meta["saved"] = join_list([f"{n}={saved[n]}" for n in sorted(saved, key=int)])
    write_md(path, meta, body)
    print(f"✓ chosen {meta['chosen']} in {args.trail}/{args.step}" + (f", saved to {args.save}" if args.save else ""))
    return 0


def cmd_show(lib: Library, provider: OpenAlex, args: argparse.Namespace) -> int:
    trail_meta, _ = read_md(lib.trail_dir(args.trail) / "trail.md")
    print(f"{args.trail} — {trail_meta.get('question', '')}")
    print(f"seeds: {trail_meta.get('seeds', 'none')}")
    for step_id in lib.steps(args.trail):
        meta, _, _ = lib.step(args.trail, step_id)
        print(
            f"  {step_id} ← {meta.get('parent')} · {meta.get('direction')} · {meta.get('candidates')} candidates"
            f" · chosen {meta.get('chosen')} ({meta.get('chosen_by')}) · proposed {meta.get('proposed')}"
            f" · saved {meta.get('saved')} · {meta.get('agent')}"
        )
    return 0


def cmd_refresh(lib: Library, provider: OpenAlex, args: argparse.Namespace) -> int:
    records = lib.records()
    targets = args.ids or list(records)
    for record_id in targets:
        if record_id not in records:
            raise UsageError(f"record not found: {record_id}")
        meta, body = read_md(lib.papers / f"{record_id}.md")
        works = provider.works_by_ids(split_list(meta.get("openalex", "")))
        if not works:
            raise ProviderError(f"no OpenAlex works returned for {record_id}")
        # Every listed work is a version of this record by definition — no identity test.
        entry = new_entry(works[0])
        for work in works:
            add_version(entry, version_of(work))
        if summarize(entry)["venue_type"] == "preprint":
            for work in provider.title_matches(meta.get("title", "")):
                version = version_of(work)
                if matches(entry, version, norm_title(work.get("display_name") or "")):
                    add_version(entry, version)
        data = summarize(entry)
        before = (meta.get("venue"), meta.get("is_retracted"))
        extra = {k: meta[k] for k in ("added", "added_by", "source_step", "collections") if k in meta}
        extra["refreshed"] = date.today().isoformat()
        notes = body.split("## Notes", 1)[1] if "## Notes" in body else "\n"
        lib.write_record(record_id, data, extra, notes)
        after = (data["venue"], "yes" if data["is_retracted"] else "no")
        change = []
        if before[0] != after[0]:
            change.append(f"venue {before[0]} → {after[0]}")
        if before[1] != after[1]:
            change.append("NOW RETRACTED" if after[1] == "yes" else "retraction cleared")
        print(f"  {record_id}: " + ("; ".join(change) if change else "no change in venue or retraction"))
    print(f"✓ refreshed {len(targets)} record(s)")
    return 0


def bibtex_key(meta: dict[str, str], used: set[str]) -> str:
    first = meta.get("authors", "").split(";")[0].strip()
    last = norm_title(first.split(" ")[-1] if first else "anon").replace(" ", "") or "anon"
    word = next((w for w in norm_title(meta.get("title", "")).split() if len(w) > 3), "paper")
    base = f"{last}{meta.get('year', '')}{word}"
    key, suffix = base, 1
    while key in used:
        suffix += 1
        key = f"{base}{chr(ord('a') + suffix - 2)}"
    used.add(key)
    return key


def bibtex_entry(meta: dict[str, str], key: str) -> str:
    names = [n.strip() for n in re.sub(r"\s*\(\+\d+\)$", "", meta.get("authors", "")).split(";") if n.strip()]
    author = " and ".join(names + (["others"] if re.search(r"\(\+\d+\)$", meta.get("authors", "")) else []))
    fields = [("title", "{" + meta.get("title", "") + "}"), ("author", author), ("year", meta.get("year", ""))]
    kind = meta.get("venue_type", "other")
    if kind == "journal":
        entry_type = "article"
        fields.append(("journal", meta.get("venue", "")))
    elif kind == "conference":
        entry_type = "inproceedings"
        fields.append(("booktitle", meta.get("venue", "")))
    else:
        entry_type = "misc"
        if kind != "preprint":
            fields.append(("howpublished", meta.get("venue", "")))
    if meta.get("doi", "none") != "none":
        fields.append(("doi", meta["doi"]))
    if meta.get("arxiv", "none") != "none":
        fields += [("eprint", meta["arxiv"]), ("archivePrefix", "arXiv")]
    if meta.get("is_retracted") == "yes":
        fields.append(("note", "RETRACTED"))
    body = ",\n".join(f"  {name} = {{{value}}}" for name, value in fields if value)
    return f"@{entry_type}{{{key},\n{body}\n}}\n"


def cmd_export(lib: Library, provider: OpenAlex, args: argparse.Namespace) -> int:
    records = lib.records()
    used: set[str] = set()
    entries = []
    for record_id in lib.collection_ids(args.collection):
        if record_id not in records:
            raise UsageError(f"collection lists a missing record: {record_id}")
        entries.append(bibtex_entry(records[record_id], bibtex_key(records[record_id], used)))
    text = "\n".join(entries)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"✓ exported {len(entries)} entries to {args.out}")
    else:
        sys.stdout.write(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shared Brain Research paper library and exploration trails")
    parser.add_argument("--root", default=None, help="repository root")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("trail-new", help="start a trail for one question")
    p.add_argument("slug")
    p.add_argument("--question", required=True)
    p.add_argument("--seed", action="append", help="doi:…, arxiv:…, or openalex:W… (repeatable)")
    p.add_argument("--collection", action="append", help="seed with every record in a collection")
    p.add_argument("--project", default=None, help="research/{project} slug this trail serves")
    p.add_argument("--agent", required=True)
    p.add_argument("--date", default=None, help="YYYY-MM-DD")
    p.set_defaults(func=cmd_trail_new)

    p = sub.add_parser("step", help="run one search step (a checkpoint)")
    p.add_argument("trail")
    p.add_argument("--direction", required=True, choices=DIRECTIONS)
    p.add_argument("--from", dest="parent", default=None, help="parent step; its inputs plus its chosen papers become the inputs")
    p.add_argument("--add", action="append", help="extra input: L0001, W…, or step-NN#k")
    p.add_argument("--query", default=None, help="keywords for --direction search")
    p.add_argument("--year", default=None, help="2020-, -2019, 2020-2024")
    p.add_argument("--include-retracted", action="store_true")
    p.add_argument("--exclude-preprint-only", action="store_true")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_step)

    p = sub.add_parser("choose", help="record which candidates were picked, and optionally save them")
    p.add_argument("trail")
    p.add_argument("step")
    p.add_argument("--pick", required=True, help="candidate numbers, e.g. 1,4,7")
    p.add_argument("--by", required=True, choices=("human", "ai"), help="who picked; an AI pick is only proposed")
    p.add_argument("--save", default=None, help="collection slug to save the picked papers into")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_choose)

    p = sub.add_parser("show", help="print a trail's steps for handoff")
    p.add_argument("trail")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("refresh", help="re-read records: new published version, citations, retraction")
    p.add_argument("ids", nargs="*")
    p.set_defaults(func=cmd_refresh)

    p = sub.add_parser("export", help="export a collection")
    p.add_argument("collection")
    p.add_argument("--bibtex", action="store_true", required=True)
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_export)
    return parser


def main(argv: list[str] | None = None, provider: OpenAlex | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    if not (root / "system" / "RULES.md").is_file():
        print(f"[ERROR] not a Shared Brain Research root: {root}", file=sys.stderr)
        return 2
    if getattr(args, "limit", 1) < 1:
        print("[ERROR] --limit must be at least 1", file=sys.stderr)
        return 2
    try:
        return args.func(Library(root), provider or default_provider(), args)
    except UsageError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    except ProviderError as exc:
        print(f"[ERROR] {exc} — no step was written", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
