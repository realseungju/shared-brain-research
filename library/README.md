# Library

한국어 번역: [`README.ko.md`](README.ko.md)

Find papers, and keep **only the ones a person picked**. This is **Tier 2**, so it is not read at
session start. A task or a session hook points at the trail to continue right now.

It has two layers. The split mirrors Research Rabbit's Library (keeping) and Search (exploring);
the difference is that every exploration step stays behind as a Git file, so another AI can pick
up the search from any step.

| Layer | Where | What it holds |
|---|---|---|
| Library | `papers/L0001.md` | One paper = one record. A preprint and its published version share a record |
| Library | `collections/{slug}.md` | A list of records per project or topic |
| Exploration trail | `trails/YYYY-MM-DD-slug/` | The search for one question. `trail.md` + one `step-NN.md` per search |

## Flow

```text
trail-new (question + seed papers)
→ step: input papers × direction → candidate list   (references · citations · related · search)
→ choose --by human: a person picks                  (if an AI picks, --by ai leaves it only as proposed)
→ choose --save: only what was picked becomes a library record
→ step --from step-NN: that step's inputs + what was chosen become the next input. AI proposals (proposed) are not followed — to use one, --add step-NN#k.
  Branching again from an earlier step never deletes later steps
```

```sh
python infra/library.py trail-new factuality --question "How do we measure LLM factuality?" \
  --seed arxiv:2305.14251 --seed doi:10.18653/v1/2023.emnlp-main.557 --agent Claude
python infra/library.py step 2026-10-27-factuality --direction references --agent Claude
python infra/library.py choose 2026-10-27-factuality step-01 --pick 2,10 --by human \
  --save factuality --agent Claude
python infra/library.py step 2026-10-27-factuality --from step-01 --direction citations \
  --year 2024- --agent Codex
python infra/library.py show 2026-10-27-factuality
python infra/library.py export factuality --bibtex --out refs.bib
python infra/library.py refresh
```

An agent taking over uses `show` to see each step's inputs, filters, and supplementary sources,
then continues with `--from`. On 2026-10-29 Codex used this flow to continue Claude's trail from
step-02 (AC 1).

The user does not type the commands. They say something like "start from these two papers and
widen out through their references"; the agent runs it, shows the candidate table, and **a person
picks the numbers**.

## Versions — the published version comes first

OpenAlex often keeps a paper's arXiv version and its published version as separate works.
Measured on 2026-10-27: the FActScore arXiv version had 0 references and 14 citations; the EMNLP
published version had 46 references and 400 citations.

- If a seed exists only as a preprint, find the published version with exactly the same title and
  use both (`W…+W…`).
- Candidates show the versions merged on one line, and citations are the sum over versions.
- `venue` follows the published version. If none is found, it shows up as `preprint-only`.
- Merging on title alone requires at least one shared author. All authors (up to 50) are compared
  by OpenAlex author ID, or by family name plus the initial at the other end of the name (in both
  orders). `Sewon Min`, `Min Sewon`, and `S. Min` count as the same person; `Wei Zhang` and
  `Wei Wang` do not. Even with the same title, works stay separate if no author overlaps, if they
  carry different published DOIs, or if their years are 3 or more apart. A DOI assigned by a
  preprint server or working-paper series (bioRxiv, SSRN, NBER) does not count as "a different
  published DOI" — it is a version of the same paper. Records already in the library are matched
  by the same rule (on the record side, only the first 3 stored names are used).
- Title comparison keeps every script, including Hangul and CJK characters. Only accents are
  stripped.
- If one same-title preprint matches two papers with different published DOIs, it is attached to
  neither and kept separate. If the preprint arrived before one of the two published versions and
  was already merged, that group is kept (arrival order decides).
- During `refresh`, an old ID that OpenAlex no longer returns (merged or deleted) stays in the
  version table marked `· not returned`. That version is left out of venue, citation, and
  retraction decisions.

## Candidate order and filters

- Order: how many input papers a candidate connects to (`links`) → citations → year. `search`
  keeps OpenAlex's order.
- Retracted papers are excluded by default. They are not hidden: the count is recorded as
  `excluded: retracted=N`.
- `--year`, `--exclude-preprint-only`, `--limit`. The number cut off is recorded as
  `beyond-limit=N`.
- `citations` fetches only the top 200 most-cited works per input. Recent papers can be missed —
  this is written into `filters`. With `--recent` it fetches the 200 newest and shows them newest
  first.
- The input papers themselves and **their other versions** (same title, overlapping authors) are
  removed from the candidates and counted as `input=N`. Measured on 2026-10-29: QJE's "Generative
  AI at Work" listed its own NBER working paper among its references.
- A reference dated more than a year after the paper citing it is not removed; it gets a `⚠` next
  to its year (`after_input`). It may be a wrong link or a wrong year. Measured on 2026-10-29: a
  2024 paper among AlphaFold's (2021) references was a linking error; "Attention Is All You Need"
  listed as 2025 was a year error.

## Supplementing references — Crossref and Semantic Scholar

OpenAlex reference lists have gaps. Measured on 2026-10-29: FActScore's (EMNLP) OpenAlex list
lacked FEVER, GPT-3, and BERTScore. So a `references` step asks two more lists.

| Source | Knows | Does not know |
|---|---|---|
| Crossref | References registered by the publisher (needs a published DOI) | Venues that do not register them, such as the ACL Anthology; items without a DOI |
| Semantic Scholar | Strong on computer science and preprints. If a DOI or arXiv ID finds nothing, it looks up **exactly the same title + an overlapping author** | Without a key, rate limits (429) are frequent. Even with a key, requests are spaced 1.1 seconds apart |

- Of the papers the two lists name by DOI or arXiv ID, only those missing from the OpenAlex list
  are looked up again in OpenAlex and added to the candidates. If OpenAlex does not have one, it is
  not added and is counted as `not found in OpenAlex`. Items with no ID are not guessed at; they
  are counted as `without DOI`.
- Each candidate's `found_by` records which list found it. The step's `supplement` records counts
  and failures per source.
- A step is still written if a supplementary source fails (only an OpenAlex failure blocks the
  step). The failure is recorded in `supplement` as `unavailable`.
- A rate limit (429) is retried after waiting 2, 5, then 10 seconds.
- `--openalex-only` skips the supplementary sources.
- Look twice at a candidate whose `found_by` is only `[semanticscholar]`. On 2026-10-29, across
  6 papers, 5–6 of 61 such candidates appeared to be citation strings linked to the wrong paper
  (for example, a BERT citation resolved to "BERT: A Review of Applications…", or a title of
  "MEETING SUMMARIES"). That judgment was made by eye. Running the same 6 papers 4 times with a key
  gave the same candidate list every time.

Compared with Research Rabbit on the same 4 papers (2026-10-29, matched on the first 8 words of
the title, overlap counted after deduplication):

| Seed paper | Research Rabbit | Overlap before supplement | Overlap after supplement |
|---|---|---|---|
| FActScore | 59 | 41 | 56 |
| AlphaFold | 87 | 77 | 79 |
| GraphCast | 27 | 24 | 25 |
| Generative AI at Work | 77 | 56 | 65 |

## What is enforced (research-lint)

- A step file's candidate list cannot be rewritten after the search (`candidates_sha256`).
- `chosen` only when `chosen_by: human`. `saved` only from within `chosen`.
- A record must appear in the `saved` list of its own `source_step` — no record exists that a
  person did not pick.
- Records and collections must point at each other.
- Library papers are **not experimental evidence.** Using `library:` as evidence for a `supported`
  claim fails.
- A step input `step-NN#k` must be a real candidate number from an earlier step.
- A research document that points at a retracted record, as `library:L0001` or as a link to
  `library/papers/L0001.md`, gets a WARN.

`chosen_by: human` is a provenance record like `human_approved`, not identity authentication.

## Terms of use

Since 2026-02-13, OpenAlex has a daily budget per API key. It works without a key, but the budget
is small; a free key gives 10 times as much. Lookups by ID are free, lists and filters cost $0.10
per 1,000, and search costs $1 per 1,000.

- A person puts the key in the environment variable `OPENALEX_API_KEY`. Never write it into a
  file, a commit, or a prompt.
- `OPENALEX_MAILTO` is optional. The same address is left as a contact with Crossref.
- The Semantic Scholar key is `SEMANTIC_SCHOLAR_API_KEY` (optional). Without it, rate limits are
  frequent.
- Crossref has no key.
- On a quota overrun or network failure, **no step is written** and the failure is reported (exit
  code 3).

## Known limits

- OpenAlex reference links are noisy. On real data, highly cited papers unrelated to the topic
  showed up among the candidates. That is why a person picks.
- `related` is OpenAlex `related_works`. No embedding similarity is used. It mostly returns recent
  follow-up work on the same topic. Research Rabbit's Similar shows papers that are often cited
  together (including classics and tool papers) — a different feature with the same name. In the
  2026-10-29 comparison, all 4 papers overlapped by 0–1 papers. There is no co-citation direction
  yet.
- There is no author direction, Zotero sync, new-paper alert, or citation map view yet.
- No filter by work type (paper, book, dataset, and so on) — decided 2026-10-27. A person looks
  at the candidate table and picks.
- Versions with no author information are not merged by title. Showing two lines is better than a
  wrong merge.
- Fetching PDF full text and verifying quotations are out of scope.
