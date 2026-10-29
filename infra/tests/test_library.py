from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import re
import tempfile
import unittest

from support import REPO, make_brain, make_research_project, run_script, write

SPEC = importlib.util.spec_from_file_location("library", REPO / "infra" / "library.py")
library = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(library)

TRAIL = "2026-10-27-factuality"


def work(work_id: str, title: str, year: int, *, doi: str = "", venue: str = "", venue_type: str = "journal",
         arxiv: str = "", cited_by: int = 0, retracted: bool = False, refs: tuple[str, ...] = (),
         related: tuple[str, ...] = (),
         authors: tuple[str, ...] = ("Ada Lovelace", "Alan Turing", "Grace Hopper", "Edsger Dijkstra")) -> dict:
    locations = []
    if venue:
        locations.append({"source": {"display_name": venue, "type": venue_type}})
    if arxiv:
        locations.append({
            "landing_page_url": f"https://arxiv.org/abs/{arxiv}v2",
            "source": {"display_name": "arXiv (Cornell University)", "type": "repository"},
        })
    return {
        "id": f"https://openalex.org/{work_id}",
        "doi": f"https://doi.org/{doi}" if doi else None,
        "display_name": title,
        "publication_year": year,
        "cited_by_count": cited_by,
        "is_retracted": retracted,
        "authorships": [{"author": {"display_name": n}} for n in authors],
        "primary_location": locations[0] if locations else None,
        "locations": locations,
        "referenced_works": [f"https://openalex.org/{r}" for r in refs],
        "related_works": [f"https://openalex.org/{r}" for r in related],
    }


class FakeOpenAlex:
    """Two seeds (W1, W2). Both cite W10 (published) whose arXiv preprint is a separate work W11;
    W1 also cites W12 (retracted) and W13 (preprint only); W2 cites W14."""

    def __init__(self) -> None:
        self.works = {w["id"].rsplit("/", 1)[-1]: w for w in (
            work("W1", "Seed paper one", 2023, doi="10.1/seed1", venue="ACL", venue_type="conference",
                 refs=("W10", "W11", "W12", "W13")),
            work("W2", "Seed paper two", 2024, doi="10.1/seed2", venue="TACL", refs=("W10", "W14")),
            work("W10", "Measuring Factual Precision", 2023, doi="10.18653/v1/factual", venue="EMNLP",
                 venue_type="conference", cited_by=300),
            work("W11", "Measuring factual precision", 2023, doi="10.48550/arxiv.2305.14251",
                 arxiv="2305.14251", cited_by=15),
            work("W12", "A retracted result", 2021, doi="10.1/retracted", venue="Some Journal", retracted=True,
                 cited_by=50),
            work("W13", "Only on arXiv", 2022, arxiv="2201.00001", cited_by=40),
            work("W14", "Older baseline", 2019, doi="10.1/old", venue="NeurIPS", venue_type="conference",
                 cited_by=900),
            work("W20", "Later follow-up", 2025, doi="10.1/later", venue="ICLR", venue_type="conference",
                 cited_by=5),
        )}
        self.citers = {"W10": ["W20"], "W11": ["W20"]}
        self.calls = 0

    def work(self, ref: str) -> dict:
        self.calls += 1
        if ref.startswith("doi:"):
            doi = ref[4:].lower()
            return next(w for w in self.works.values() if (w["doi"] or "").lower().endswith(doi))
        return self.works[ref]

    def works_by_ids(self, ids: list[str]) -> list[dict]:
        self.calls += 1
        return [self.works[i] for i in ids if i in self.works]

    def citing(self, work_id: str, limit: int, recent: bool = False) -> list[dict]:
        self.calls += 1
        found = [self.works[i] for i in self.citers.get(work_id, [])]
        if recent:
            found.sort(key=lambda w: -w["publication_year"])
        return found[:limit]

    def works_by_dois(self, dois: list[str]) -> list[dict]:
        self.calls += 1
        return [w for w in self.works.values() if library.work_ids(w) & set(dois)]

    def search(self, query: str, limit: int) -> list[dict]:
        self.calls += 1
        return [self.works["W14"], self.works["W10"]][:limit]

    def title_matches(self, title: str) -> list[dict]:
        self.calls += 1
        key = library.norm_title(title)
        return [w for w in self.works.values() if library.norm_title(w["display_name"]) == key]


class FakeSource:
    """Another reference list: names works by DOI, some OpenAlex already lists, one it lacks,
    one it cannot find, and two entries with no DOI at all."""

    name = "fakesource"

    def __init__(self, refs: dict[str, set[str]] | None = None, fail: bool = False, fail_after: int | None = None) -> None:
        self.refs = refs if refs is not None else {"10.1/seed1": {"10.1/old", "10.1/extra", "10.1/nowhere"}}
        self.fail = fail
        self.fail_after = fail_after
        self.asked: list[list[str]] = []

    def references(self, dois: list[str], arxivs: list[str], title: str = "", authors: list[str] | None = None):
        self.asked.append(dois)
        if self.fail or (self.fail_after is not None and len(self.asked) > self.fail_after):
            raise library.ProviderError("Semantic Scholar HTTP 429")
        found = [self.refs[d] for d in dois if d in self.refs]
        return (set().union(*found), 2) if found else None


class LibraryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)
        make_research_project(self.root)
        self.provider = FakeOpenAlex()
        self.sources: list | None = None

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_library(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = library.main(["--root", str(self.root), *args], provider=self.provider, sources=self.sources)
        return code, out.getvalue(), err.getvalue()

    def lint(self):
        return run_script("research-lint.py", str(self.root))

    def start_trail(self) -> None:
        code, _, err = self.run_library(
            "trail-new", "factuality", "--question", "How is factuality measured?", "--seed", "doi:10.1/seed1",
            "--seed", "openalex:W2", "--agent", "Claude", "--date", "2026-10-27",
        )
        self.assertEqual(code, 0, err)

    def step_path(self, step: str) -> Path:
        return self.root / "library/trails" / TRAIL / f"{step}.md"

    def candidates(self, step: str) -> list[dict]:
        return library.read_candidates(self.step_path(step).read_text(encoding="utf-8"))

    def references_step(self) -> list[dict]:
        self.start_trail()
        code, _, err = self.run_library("step", TRAIL, "--direction", "references", "--agent", "Claude")
        self.assertEqual(code, 0, err)
        return self.candidates("step-01")


class LibraryTests(LibraryCase):
    def test_preprint_and_published_merge_into_one_candidate_shown_as_published(self) -> None:
        candidates = self.references_step()
        factual = [c for c in candidates if "factual precision" in c["title"].lower()]
        self.assertEqual(len(factual), 1)
        self.assertEqual(factual[0]["venue"], "EMNLP")
        self.assertEqual(factual[0]["doi"], "10.18653/v1/factual")
        self.assertEqual(factual[0]["arxiv"], "2305.14251")
        self.assertEqual(factual[0]["cited_by"], 315)

    def test_candidates_connected_to_more_inputs_rank_first(self) -> None:
        candidates = self.references_step()
        self.assertEqual(candidates[0]["connections"], 2)
        self.assertIn("factual precision", candidates[0]["title"].lower())
        self.assertEqual([c["n"] for c in candidates], list(range(1, len(candidates) + 1)))

    def test_retracted_paper_is_excluded_but_counted(self) -> None:
        candidates = self.references_step()
        self.assertFalse(any(c["is_retracted"] for c in candidates))
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertIn("retracted=1", meta["excluded"])

    def test_preprint_only_is_labelled_not_hidden(self) -> None:
        candidates = self.references_step()
        arxiv_only = next(c for c in candidates if c["title"] == "Only on arXiv")
        self.assertEqual(arxiv_only["venue"], "preprint-only")

    def test_ai_pick_is_only_proposed_and_cannot_save(self) -> None:
        self.references_step()
        code, _, err = self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "ai", "--save", "core",
                                        "--agent", "Claude")
        self.assertEqual(code, 2)
        self.assertIn("only a human pick", err)
        code, _, _ = self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "ai", "--agent", "Claude")
        self.assertEqual(code, 0)
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertEqual((meta["proposed"], meta["chosen"]), ("1", "none"))
        self.assertFalse((self.root / "library/papers").exists())

    def test_human_save_creates_record_collection_and_passes_lint(self) -> None:
        self.references_step()
        code, _, err = self.run_library("choose", TRAIL, "step-01", "--pick", "1,2", "--by", "human", "--save",
                                        "core", "--agent", "Claude")
        self.assertEqual(code, 0, err)
        record = (self.root / "library/papers/L0001.md").read_text(encoding="utf-8")
        self.assertIn("venue: EMNLP", record)
        self.assertIn("source_step: 2026-10-27-factuality/step-01", record)
        self.assertIn("- L0001", (self.root / "library/collections/core.md").read_text(encoding="utf-8"))
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_saving_a_known_paper_again_adds_collection_not_record(self) -> None:
        self.references_step()
        self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "human", "--save", "core", "--agent", "Claude")
        code, out, _ = self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "human", "--save",
                                        "reading", "--agent", "Codex")
        self.assertEqual(code, 0)
        self.assertIn("already in the library", out)
        self.assertEqual(len(list((self.root / "library/papers").glob("*.md"))), 1)
        self.assertIn("collections: core, reading", (self.root / "library/papers/L0001.md").read_text(encoding="utf-8"))
        self.assertEqual(self.lint().returncode, 0)

    def test_child_step_inherits_inputs_plus_chosen_and_branching_keeps_both(self) -> None:
        self.references_step()
        self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "human", "--agent", "Claude")
        code, _, err = self.run_library("step", TRAIL, "--from", "step-01", "--direction", "citations", "--agent", "Codex")
        self.assertEqual(code, 0, err)
        meta, _ = library.read_md(self.step_path("step-02"))
        self.assertEqual(meta["inputs"], "W1, W2, step-01#1")
        self.assertIn("Later follow-up", [c["title"] for c in self.candidates("step-02")])
        code, _, err = self.run_library("step", TRAIL, "--from", "step-01", "--direction", "related", "--agent", "Claude")
        self.assertEqual(code, 0, err)
        self.assertTrue(self.step_path("step-02").is_file() and self.step_path("step-03").is_file())
        trail = (self.root / "library/trails" / TRAIL / "trail.md").read_text(encoding="utf-8")
        self.assertIn("step-02 ← step-01 · citations", trail)
        self.assertIn("step-03 ← step-01 · related", trail)
        self.assertEqual(self.lint().returncode, 0)

    def test_arxiv_seed_is_joined_with_its_published_version(self) -> None:
        # Seen on real OpenAlex data: the arXiv record had no references; the published one had 46.
        self.provider.works["W40"] = work("W40", "Preprint seed", 2023, doi="10.48550/arxiv.2401.00040",
                                          arxiv="2401.00040")
        self.provider.works["W41"] = work("W41", "Preprint Seed", 2023, doi="10.1/seed-published", venue="ACL",
                                          venue_type="conference", refs=("W14",))
        code, _, err = self.run_library("trail-new", "factuality", "--question", "q", "--seed", "arxiv:2401.00040",
                                        "--agent", "Claude", "--date", "2026-10-27")
        self.assertEqual(code, 0, err)
        trail = (self.root / "library/trails" / TRAIL / "trail.md").read_text(encoding="utf-8")
        self.assertIn("seeds: W40+W41", trail)
        self.run_library("step", TRAIL, "--direction", "references", "--agent", "Claude")
        self.assertEqual([c["title"] for c in self.candidates("step-01")], ["Older baseline"])
        self.assertEqual(self.lint().returncode, 0)

    def test_same_title_years_apart_is_not_merged(self) -> None:
        entry = library.new_entry(self.provider.works["W14"])
        library.add_version(entry, library.version_of(self.provider.works["W14"]))
        other = library.version_of(work("W99", "Older baseline", 2025))
        self.assertFalse(library.matches(entry, other, library.norm_title("Older baseline")))

    def test_search_step_keeps_provider_order(self) -> None:
        self.start_trail()
        code, _, err = self.run_library("step", TRAIL, "--direction", "search", "--query", "factuality",
                                        "--agent", "Claude")
        self.assertEqual(code, 0, err)
        self.assertEqual([c["title"] for c in self.candidates("step-01")], ["Older baseline", "Measuring Factual Precision"])

    def test_year_filter_and_limit_are_recorded(self) -> None:
        self.start_trail()
        self.run_library("step", TRAIL, "--direction", "references", "--year", "2022-", "--limit", "1", "--agent", "Claude")
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertEqual(meta["candidates"], "1")
        self.assertIn("year=1", meta["excluded"])
        self.assertIn("beyond-limit=1", meta["excluded"])

    def test_bibtex_export_uses_published_version(self) -> None:
        self.references_step()
        self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "human", "--save", "core", "--agent", "Claude")
        code, out, _ = self.run_library("export", "core", "--bibtex")
        self.assertEqual(code, 0)
        self.assertIn("@inproceedings{", out)
        self.assertIn("booktitle = {EMNLP}", out)
        self.assertIn("doi = {10.18653/v1/factual}", out)
        self.assertIn("eprint = {2305.14251}", out)
        self.assertIn("Grace Hopper and others", out)

    def test_refresh_finds_published_version_of_preprint_only_record(self) -> None:
        self.references_step()
        number = next(c["n"] for c in self.candidates("step-01") if c["title"] == "Only on arXiv")
        self.run_library("choose", TRAIL, "step-01", "--pick", str(number), "--by", "human", "--save", "core",
                         "--agent", "Claude")
        self.provider.works["W30"] = work("W30", "Only on arXiv", 2023, doi="10.1/now-published",
                                          venue="JMLR", cited_by=3)
        code, out, _ = self.run_library("refresh", "L0001")
        self.assertEqual(code, 0)
        self.assertIn("venue preprint-only → JMLR", out)
        record = (self.root / "library/papers/L0001.md").read_text(encoding="utf-8")
        self.assertIn("openalex: W13, W30", record)
        self.assertEqual(self.lint().returncode, 0)

    def save_titled(self, title: str) -> None:
        self.references_step()
        number = next(c["n"] for c in self.candidates("step-01") if c["title"] == title)
        code, _, err = self.run_library("choose", TRAIL, "step-01", "--pick", str(number), "--by", "human", "--save",
                                        "core", "--agent", "Claude")
        self.assertEqual(code, 0, err)

    def test_saved_record_is_matched_by_the_same_rule_as_candidates(self) -> None:
        # Codex review (1): stored records skipped the year rule, so a 2025 paper joined a 2019 record.
        self.save_titled("Older baseline")
        lib = library.Library(self.root)

        def candidate(work_id: str, year: int) -> dict:
            entry = library.new_entry(work(work_id, "Older baseline", year))
            library.add_version(entry, library.version_of(work(work_id, "Older baseline", year)))
            return library.summarize(entry)

        self.assertIsNone(lib.find_record(candidate("W99", 2025)))
        self.assertEqual(lib.find_record(candidate("W98", 2020)), "L0001")

    def test_same_title_different_authors_is_not_merged(self) -> None:
        # Codex review (2)
        pool: list[dict] = []
        library.merge_work(pool, work("W50", "A common title", 2023, venue="Workshop A", authors=("Kim Lee",)), None)
        library.merge_work(pool, work("W51", "A common title", 2023, venue="Journal B", authors=("Ola Nordmann",)), None)
        self.assertEqual(len(pool), 2)
        library.merge_work(pool, work("W52", "A common title", 2023, arxiv="2301.00052", authors=("Kim Lee",)), None)
        self.assertEqual(sorted(len(e["versions"]) for e in pool), [1, 2])

    def test_work_that_bridges_two_entries_joins_them(self) -> None:
        # Codex review (3)
        pool: list[dict] = []
        library.merge_work(pool, work("W60", "Title one", 2023, doi="10.1/a", venue="J"), "W1")
        library.merge_work(pool, work("W61", "Title two", 2023, arxiv="2301.00001"), "W2")
        bridge = work("W62", "Title three", 2023, doi="10.1/a", arxiv="2301.00001")
        library.merge_work(pool, bridge, None)
        self.assertEqual(len(pool), 1)
        self.assertEqual(pool[0]["openalex"], {"W60", "W61", "W62"})
        self.assertEqual(pool[0]["via"], {"W1", "W2"})

    def test_korean_and_chinese_titles_merge_versions(self) -> None:
        # Codex review (4): the title key used to be empty for non-Latin titles.
        for title in ("한국어 연구", "中文研究"):
            self.assertNotEqual(library.norm_title(title), "")
            pool: list[dict] = []
            library.merge_work(pool, work("W70", title, 2023, arxiv="2301.00070"), None)
            library.merge_work(pool, work("W71", title, 2023, doi="10.1/w71", venue="KCI"), None)
            self.assertEqual(len(pool), 1, title)
            self.assertEqual(library.summarize(pool[0])["venue"], "KCI")

    def test_refresh_keeps_ids_openalex_no_longer_returns(self) -> None:
        # Codex review (5): spec edge case — old IDs stay in versions.
        self.save_titled("Only on arXiv")
        self.provider.works["W13"] = work("W200", "Only on arXiv", 2022, arxiv="2201.00001", cited_by=41)
        code, _, err = self.run_library("refresh", "L0001")
        self.assertEqual(code, 0, err)
        meta, body = library.read_md(self.root / "library/papers/L0001.md")
        self.assertEqual(library.split_list(meta["openalex"]), ["W200", "W13"])
        self.assertEqual(meta["cited_by"], "41")
        self.assertIn("| preprint · not returned |", body)
        self.assertEqual(library.Library(self.root).find_record({"title": "x", "versions": [
            {"openalex": "W13", "doi": "", "arxiv": "", "year": None}]}), "L0001")
        self.run_library("refresh", "L0001")
        self.assertEqual(library.split_list(library.read_md(self.root / "library/papers/L0001.md")[0]["openalex"]),
                         ["W200", "W13"])
        self.assertEqual(self.lint().returncode, 0)

    def test_line_breaks_in_metadata_cannot_add_fields(self) -> None:
        # Codex review (6)
        self.provider.works["W14"]["authorships"] = [{"author": {"display_name": "Alice\nyear: 1900"}},
                                                     {"author": {"display_name": "Bob venue: Fake"}}]
        self.save_titled("Older baseline")
        meta, _ = library.read_md(self.root / "library/papers/L0001.md")
        self.assertEqual((meta["year"], meta["venue"]), ("2019", "NeurIPS"))
        self.assertEqual(meta["authors"], "Alice year: 1900; Bob venue: Fake")
        self.assertEqual(self.lint().returncode, 0)
        code, _, err = self.run_library("trail-new", "other", "--question", "q year: 1900", "--seed", "openalex:W1",
                                        "--agent", "Claude", "--date", "2026-10-27")
        self.assertEqual(code, 2)
        self.assertIn("single non-empty line", err)

    def test_bibtex_escapes_tex_specials_and_keys_never_run_out(self) -> None:
        # Codex review (7)(8)
        meta = {"title": "A { brace & 50% $cost_", "authors": "Jürgen Müller; 김철수", "year": "2023",
                "venue": "A&B", "venue_type": "journal", "doi": "10.1/x_y", "arxiv": "none", "is_retracted": "no"}
        entry = library.bibtex_entry(meta, "k")
        self.assertIn(r"\textbraceleft{} brace \& 50\% \$cost\_", entry)
        self.assertIn(r"journal = {A\&B}", entry)
        self.assertIn("doi = {10.1/x_y}", entry)
        self.assertEqual(entry.count("{"), entry.count("}"))
        used: set[str] = set()
        keys = [library.bibtex_key(meta, used) for _ in range(28)]
        self.assertEqual((keys[0], keys[1], keys[26], keys[27]), ("muller2023brace", "muller2023bracea",
                                                                  "muller2023bracez", "muller2023braceaa"))
        self.assertTrue(all(re.fullmatch(r"[a-z0-9]+", k) for k in keys))
        self.assertEqual(library.bibtex_key({"authors": "김철수", "title": "한국어 연구", "year": "2023"}, set()),
                         "anon2023paper")

    def test_title_bridge_does_not_join_two_published_dois(self) -> None:
        # Codex re-review: a preprint matching two same-title papers by title joined their DOIs.
        # Third check: it then followed input order. Ambiguous, so it stays apart in any order.
        works = {
            "W80": work("W80", "Same title", 2023, doi="10.1/a", venue="J", authors=("Alice Smith",)),
            "W81": work("W81", "Same title", 2023, doi="10.1/b", venue="K", authors=("Alice Smith",)),
            "W82": work("W82", "Same title", 2023, arxiv="2301.00403", authors=("Alice Smith",)),
        }
        for order in (("W80", "W81", "W82"), ("W81", "W80", "W82")):
            pool: list[dict] = []
            for work_id in order:
                library.merge_work(pool, works[work_id], None)
            self.assertEqual(sorted(sorted(e["openalex"]) for e in pool), [["W80"], ["W81"], ["W82"]], order)

    def test_step_written_with_older_author_keys_still_finds_the_record(self) -> None:
        # Codex fourth check: a candidate whose versions carry old-format keys missed L0001.
        self.save_titled("Older baseline")
        candidate = library.summarize((lambda e: (library.add_version(e, library.version_of(
            work("W900", "Older baseline", 2019))), e)[1])(library.new_entry(work("W900", "Older baseline", 2019))))
        for version in candidate["versions"]:
            version["authors"] = ["lovelace", "turing", "hopper"]  # surname-only keys of an earlier commit
        self.assertEqual(library.Library(self.root).find_record(candidate), "L0001")

    def test_shared_given_name_alone_is_not_the_same_author(self) -> None:
        # Codex third check: first-token keys made "Wei Zhang" and "Wei Wang" one author.
        for one, other in (("Wei Zhang", "Wei Wang"), ("Li Chen", "Li Zhao"), ("David Smith", "David Jones")):
            pool: list[dict] = []
            library.merge_work(pool, work("W95", "Common title", 2023, arxiv="2301.00095", authors=(one,)), None)
            library.merge_work(pool, work("W96", "Common title", 2023, doi="10.1/w96", venue="J", authors=(other,)), None)
            self.assertEqual(len(pool), 2, (one, other))
        self.assertTrue(library.name_keys("S. Min") & library.name_keys("Sewon Min") & library.name_keys("Min Sewon"))

    def test_reversed_name_order_and_reordered_authors_still_join(self) -> None:
        # Codex re-review: surname = last token missed "Min Sewon"; comparing three authors missed reordering.
        for arxiv_authors, published_authors in (
            (("Min Sewon",), ("Sewon Min",)),
            (("Al Alpha", "Bo Beta", "Cy Gamma", "Di Delta", "Ed Epsilon", "Fa Zeta"),
             ("Di Delta", "Ed Epsilon", "Fa Zeta", "Al Alpha", "Bo Beta", "Cy Gamma")),
        ):
            pool: list[dict] = []
            library.merge_work(pool, work("W90", "Joined paper", 2023, arxiv="2301.00090", authors=arxiv_authors), None)
            library.merge_work(pool, work("W91", "Joined paper", 2023, doi="10.1/w91", venue="ACL",
                                          venue_type="conference", authors=published_authors), None)
            self.assertEqual(len(pool), 1, arxiv_authors)
            self.provider.works["W90"] = work("W90", "Joined paper", 2023, arxiv="2301.00090", authors=arxiv_authors)
            self.provider.works["W91"] = work("W91", "Joined paper", 2023, doi="10.1/w91", venue="ACL",
                                              venue_type="conference", authors=published_authors)
            found = library.with_published_versions(self.provider, ["W90"], {"W90": self.provider.works["W90"]})
            self.assertEqual(found, ["W90", "W91"], arxiv_authors)

    def test_refresh_does_not_grow_the_notes_section(self) -> None:
        self.save_titled("Older baseline")
        path = self.root / "library/papers/L0001.md"
        before = path.read_text(encoding="utf-8").split("## Notes", 1)[1]
        self.run_library("refresh", "L0001")
        self.run_library("refresh", "L0001")
        self.assertEqual(path.read_text(encoding="utf-8").split("## Notes", 1)[1], before)

    def test_provider_failure_writes_no_step(self) -> None:
        self.start_trail()

        def broken(*_args, **_kwargs):
            raise library.ProviderError("OpenAlex HTTP 429 on /works")

        self.provider.works_by_ids = broken  # type: ignore[assignment]
        code, _, err = self.run_library("step", TRAIL, "--direction", "references", "--agent", "Claude")
        self.assertEqual(code, 3)
        self.assertIn("no step was written", err)
        self.assertFalse(self.step_path("step-01").exists())


    def test_another_version_of_a_seed_is_not_its_own_reference(self) -> None:
        # Seen 2026-10-29: the QJE "Generative AI at Work" listed its NBER working paper as a reference.
        self.provider.works["W15"] = work("W15", "Seed paper two", 2023, doi="10.3386/w2", venue="NBER Working Papers",
                                          venue_type="repository")
        self.provider.works["W2"]["referenced_works"].append("https://openalex.org/W15")
        candidates = self.references_step()
        self.assertNotIn("Seed paper two", [c["title"] for c in candidates])
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertIn("input=1", meta["excluded"])

    def test_preprint_with_its_own_doi_joins_the_published_version(self) -> None:
        # bioRxiv, SSRN, and NBER mint DOIs for preprints; that DOI must not split the paper.
        self.provider.works["W16"] = work("W16", "Older Baseline", 2018, doi="10.1101/2018.01.01.000001",
                                          venue="bioRxiv", venue_type="repository", cited_by=7)
        self.provider.works["W2"]["referenced_works"].append("https://openalex.org/W16")
        baseline = [c for c in self.references_step() if c["title"].lower() == "older baseline"]
        self.assertEqual(len(baseline), 1)
        self.assertEqual((baseline[0]["venue"], baseline[0]["doi"], baseline[0]["cited_by"]), ("NeurIPS", "10.1/old", 907))

    def test_reference_newer_than_the_citing_paper_is_flagged_not_dropped(self) -> None:
        # Seen 2026-10-29: a wrong link (a 2024 paper among AlphaFold's 2021 references) and a wrong
        # year ("Attention Is All You Need" dated 2025). The data cannot tell them apart.
        self.provider.works["W21"] = work("W21", "Database update", 2025, doi="10.1/db2025", venue="NAR",
                                          authors=("Someone Else",))
        self.provider.works["W1"]["referenced_works"].append("https://openalex.org/W21")
        candidates = self.references_step()
        late = next(c for c in candidates if c["title"] == "Database update")
        self.assertTrue(late["after_input"])
        self.assertFalse(any(c["after_input"] for c in candidates if c is not late))
        text = self.step_path("step-01").read_text(encoding="utf-8")
        self.assertIn("| 2025 ⚠ |", text)
        self.assertIn("`⚠` (1) = dated more than a year after", text)

    def test_other_sources_add_references_openalex_missed(self) -> None:
        self.provider.works["W30"] = work("W30", "A dataset OpenAlex forgot", 2018, doi="10.1/extra", venue="NAACL",
                                          venue_type="conference", authors=("Someone Else",))
        self.sources = [FakeSource()]
        candidates = self.references_step()
        extra = next(c for c in candidates if c["title"] == "A dataset OpenAlex forgot")
        self.assertEqual(extra["found_by"], ["fakesource"])
        # OpenAlex lists W14 only under W2; the other source names it under W1 too.
        baseline = next(c for c in candidates if c["title"] == "Older baseline")
        self.assertEqual((baseline["found_by"], baseline["connections"]), (["fakesource", "openalex"], 2))
        self.assertEqual(len([c for c in candidates if c["title"] == "Older baseline"]), 1)
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertIn("fakesource listed 5 (2 without DOI)", meta["supplement"])
        self.assertIn("added 1 not in OpenAlex's list, 1 not found in OpenAlex", meta["supplement"])
        self.assertIn("references also from fakesource", meta["filters"])
        self.assertEqual(self.lint().returncode, 0)

    def test_semantic_scholar_falls_back_to_an_exact_title_match(self) -> None:
        # FActScore: Semantic Scholar does not know the EMNLP DOI, only the arXiv paper.
        calls: list[str] = []

        def fake_http(url: str, headers: dict, label: str, timeout: int = 30):
            calls.append(url)
            if "/search/match" in url:
                return {"data": [{"paperId": "abc123", "title": "FActScore: Fine-grained Atomic Evaluation",
                                  "authors": [{"name": "Sewon Min"}, {"name": "Kalpesh Krishna"}]}]}
            if "/paper/abc123/references" in url:
                return {"data": [{"citedPaper": {"externalIds": {"DOI": "10.1/A"}}},
                                 {"citedPaper": {"externalIds": {"ArXiv": "2005.14165"}}},
                                 {"citedPaper": {"externalIds": {}}}]}
            return None

        original, sleep = library.http_json, library.time.sleep
        library.http_json, library.time.sleep = fake_http, lambda _s: None
        try:
            source = library.SemanticScholar()
            source.MIN_INTERVAL = 0
            found = source.references(["10.18653/v1/x"], [], "FActScore: fine-grained atomic evaluation", ["Min Sewon"])
            self.assertEqual(found, ({"10.1/a", "10.48550/arxiv.2005.14165"}, 1))
            self.assertIsNone(source.references(["10.1/none"], [], "A different title", ["Sewon Min"]))
            # Same title, no shared author: another paper, not this one.
            self.assertIsNone(source.references(["10.1/none"], [], "FActScore: fine-grained atomic evaluation",
                                                ["Wei Zhang"]))
        finally:
            library.http_json, library.time.sleep = original, sleep
        self.assertIn("DOI:10.18653/v1/x/references", calls[0])

    def test_semantic_scholar_spaces_its_requests(self) -> None:
        # A key allows one request a second; back-to-back DOI, arXiv, match, and references calls drew 429s.
        clock = [100.0]
        slept: list[float] = []

        def sleep(seconds: float) -> None:
            slept.append(round(seconds, 2))
            clock[0] += seconds

        original = (library.http_json, library.time.sleep, library.time.monotonic)
        library.http_json = lambda *_a, **_k: None
        library.time.sleep, library.time.monotonic = sleep, lambda: clock[0]
        try:
            library.SemanticScholar().references(["10.1/a", "10.1/b"], ["2401.00001"])
        finally:
            library.http_json, library.time.sleep, library.time.monotonic = original
        self.assertEqual(slept, [1.1, 1.1])

    def test_failing_source_is_noted_and_the_step_is_still_written(self) -> None:
        self.sources = [FakeSource(fail=True)]
        candidates = self.references_step()
        self.assertTrue(candidates)
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertIn("fakesource unavailable (Semantic Scholar HTTP 429)", meta["supplement"])

    def test_source_failing_on_a_later_input_keeps_what_it_added_and_says_so(self) -> None:
        self.provider.works["W30"] = work("W30", "A dataset OpenAlex forgot", 2018, doi="10.1/extra", venue="NAACL",
                                          venue_type="conference", authors=("Someone Else",))
        self.sources = [FakeSource(fail_after=1)]
        candidates = self.references_step()
        self.assertIn("A dataset OpenAlex forgot", [c["title"] for c in candidates])
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertIn("fakesource unavailable after 1 of 2 inputs, which listed 5", meta["supplement"])
        self.assertIn("added 1 not in OpenAlex's list", meta["supplement"])

    def test_another_paper_with_the_seed_title_is_kept_when_its_published_doi_differs(self) -> None:
        # Codex check 5: a different paper's preprint alone passed the title rule, so the whole
        # candidate was dropped as an input version.
        self.provider.works["W17"] = work("W17", "Seed paper two", 2024, doi="10.9/other", venue="JMLR")
        self.provider.works["W18"] = work("W18", "Seed paper two", 2024, doi="10.2139/ssrn.1", venue="SSRN",
                                          venue_type="repository")
        self.provider.works["W1"]["referenced_works"] += ["https://openalex.org/W17", "https://openalex.org/W18"]
        candidates = self.references_step()
        same_title = [c for c in candidates if c["title"] == "Seed paper two"]
        self.assertEqual(len(same_title), 1)
        self.assertEqual(same_title[0]["doi"], "10.9/other")
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertNotIn("input=", meta["excluded"])

    def test_openalex_only_does_not_ask_other_sources(self) -> None:
        source = FakeSource()
        self.sources = [source]
        self.start_trail()
        code, _, err = self.run_library("step", TRAIL, "--direction", "references", "--openalex-only", "--agent", "Claude")
        self.assertEqual(code, 0, err)
        self.assertEqual(source.asked, [])
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertEqual(meta["supplement"], "none")
        self.assertIn("openalex only", meta["filters"])

    def test_recent_citations_order_by_full_date_within_a_year(self) -> None:
        # Codex check 5: sorting by year alone put a January paper with more citations first.
        self.provider.works["W23"] = dict(work("W23", "October paper", 2026, doi="10.1/oct", cited_by=0),
                                          publication_date="2026-10-29")
        self.provider.works["W24"] = dict(work("W24", "January paper", 2026, doi="10.1/jan", cited_by=999),
                                          publication_date="2026-01-01")
        self.provider.citers = {"W1": ["W23", "W24"]}
        self.start_trail()
        code, _, err = self.run_library("step", TRAIL, "--direction", "citations", "--recent", "--limit", "1",
                                        "--agent", "Claude")
        self.assertEqual(code, 0, err)
        self.assertEqual([c["title"] for c in self.candidates("step-01")], ["October paper"])
        self.assertNotIn("date", self.candidates("step-01")[0])

    def test_recent_citations_put_the_newest_first(self) -> None:
        self.provider.works["W22"] = work("W22", "Newest follow-up", 2026, doi="10.1/newest", venue="ACL",
                                          venue_type="conference", cited_by=0)
        self.provider.citers = {"W1": ["W20", "W22"]}
        self.start_trail()
        code, _, err = self.run_library("step", TRAIL, "--direction", "citations", "--recent", "--agent", "Claude")
        self.assertEqual(code, 0, err)
        self.assertEqual([c["title"] for c in self.candidates("step-01")], ["Newest follow-up", "Later follow-up"])
        meta, _ = library.read_md(self.step_path("step-01"))
        self.assertIn("citing works per input newest", meta["filters"])
        code, _, err = self.run_library("step", TRAIL, "--direction", "references", "--recent", "--agent", "Claude")
        self.assertEqual(code, 2)
        self.assertIn("--recent is only for --direction citations", err)


class LibraryLintTests(LibraryCase):
    def saved_library(self) -> None:
        self.references_step()
        self.run_library("choose", TRAIL, "step-01", "--pick", "1", "--by", "human", "--save", "core", "--agent", "Claude")
        self.assertEqual(self.lint().returncode, 0)

    def edit(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assert_lint_fails(self, message: str) -> None:
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(message, result.stdout)

    def test_edited_candidates_are_rejected(self) -> None:
        self.saved_library()
        self.edit(self.step_path("step-01"), '"cited_by": 315', '"cited_by": 9999')
        self.assert_lint_fails("candidates_sha256 mismatch")

    def test_chosen_without_human_is_rejected(self) -> None:
        self.saved_library()
        self.edit(self.step_path("step-01"), "chosen_by: human", "chosen_by: ai")
        self.assert_lint_fails("chosen without chosen_by: human")

    def test_saved_that_was_not_chosen_is_rejected(self) -> None:
        self.saved_library()
        self.edit(self.step_path("step-01"), "saved: 1=L0001", "saved: 1=L0001, 2=L0001")
        self.assert_lint_fails("saved a candidate that was not chosen")

    def test_record_without_matching_save_is_rejected(self) -> None:
        self.saved_library()
        write(self.root / "library/papers/L0002.md", (self.root / "library/papers/L0001.md").read_text(encoding="utf-8")
              .replace("id: L0001", "id: L0002").replace("collections: core", "collections: none"))
        self.assert_lint_fails("was not saved by a human pick")

    def test_supported_claim_citing_a_paper_is_rejected(self) -> None:
        self.saved_library()
        self.edit(self.root / "research/demo-project/claims.md", "- status: candidate\n- evidence: TBD\n"
                  "- evidence_kind: unverified\n- human_reviewed: no",
                  "- status: supported\n- evidence: library:L0001\n- evidence_kind: measured\n- human_reviewed: yes")
        self.assert_lint_fails("papers are not experiment evidence")

    def test_citing_a_retracted_record_warns_without_failing(self) -> None:
        self.saved_library()
        self.edit(self.root / "library/papers/L0001.md", "is_retracted: no", "is_retracted: yes")
        write(self.root / "research/demo-project/questions.md", "# Questions\n\nPrior work: library:L0001\n")
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(result.stdout, re.compile(r"\[WARN\].*retracted paper library:L0001"))

    def test_step_input_must_be_a_candidate_of_an_earlier_step(self) -> None:
        # Codex review (9)
        self.saved_library()
        self.run_library("step", TRAIL, "--from", "step-01", "--direction", "citations", "--agent", "Codex")
        self.edit(self.step_path("step-02"), "step-01#1", "step-01#999")
        self.assert_lint_fails("names a candidate that does not exist (step-01#999)")
        self.edit(self.step_path("step-02"), "step-01#999", "step-02#1")
        self.assert_lint_fails("is not a candidate of an earlier step of this trail (step-02#1)")

    def test_non_ascii_digit_count_is_an_error_not_a_crash(self) -> None:
        # Codex re-review: "²".isdigit() is true and int("²") raised inside lint.
        self.saved_library()
        self.run_library("step", TRAIL, "--from", "step-01", "--direction", "citations", "--agent", "Codex")
        self.edit(self.step_path("step-01"), "candidates: ", "candidates: ²")
        self.edit(self.step_path("step-01"), "proposed: none", "proposed: ²")
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("names a candidate that does not exist (step-01#1)", result.stdout)
        self.assertIn("step proposed names a candidate that does not exist", result.stdout)

    def test_citing_a_retracted_record_by_path_warns(self) -> None:
        # Codex review (10)
        self.saved_library()
        self.edit(self.root / "library/papers/L0001.md", "is_retracted: no", "is_retracted: yes")
        write(self.root / "research/demo-project/questions.md",
              "# Questions\n\n[prior work](../../library/papers/L0001.md)\n")
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(result.stdout, re.compile(r"\[WARN\].*retracted paper library:L0001"))


if __name__ == "__main__":
    unittest.main()
