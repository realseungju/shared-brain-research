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
         related: tuple[str, ...] = ()) -> dict:
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
        "authorships": [{"author": {"display_name": n}} for n in ("Ada Lovelace", "Alan Turing", "Grace Hopper", "Edsger Dijkstra")],
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

    def citing(self, work_id: str, limit: int) -> list[dict]:
        self.calls += 1
        return [self.works[i] for i in self.citers.get(work_id, [])][:limit]

    def search(self, query: str, limit: int) -> list[dict]:
        self.calls += 1
        return [self.works["W14"], self.works["W10"]][:limit]

    def title_matches(self, title: str) -> list[dict]:
        self.calls += 1
        key = library.norm_title(title)
        return [w for w in self.works.values() if library.norm_title(w["display_name"]) == key]


class LibraryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_brain(self.root)
        make_research_project(self.root)
        self.provider = FakeOpenAlex()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_library(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = library.main(["--root", str(self.root), *args], provider=self.provider)
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

    def test_provider_failure_writes_no_step(self) -> None:
        self.start_trail()

        def broken(*_args, **_kwargs):
            raise library.ProviderError("OpenAlex HTTP 429 on /works")

        self.provider.works_by_ids = broken  # type: ignore[assignment]
        code, _, err = self.run_library("step", TRAIL, "--direction", "references", "--agent", "Claude")
        self.assertEqual(code, 3)
        self.assertIn("no step was written", err)
        self.assertFalse(self.step_path("step-01").exists())


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


if __name__ == "__main__":
    unittest.main()
