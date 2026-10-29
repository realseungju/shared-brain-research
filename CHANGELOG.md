# Changelog

All notable changes to this project are recorded here. The reasoning behind a decision
lives in `system/decisions.md`; this file records what changed and when.

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). A change to
the record schema — frontmatter fields, enforced section headings, generator output — is a
breaking change.

## [Unreleased]

## [0.1.0] — 2026-10-29

First tagged release, and the first public one. The distribution has been in use since
2026-07-28; this marks the point at which the paper library landed and the repository was
opened. It is derived from [`shared-brain-lite`](https://github.com/realseungju/shared-brain-lite)
0.1.0 (see `UPSTREAM.md`).

### Added

- **Research records.** Questions, hypotheses, experiments, evidence, and claims under
  `research/{project}/`. `research-lint` refuses a `supported` claim without a linked
  experiment, measured or estimated evidence, and `human_reviewed: yes`.
- **Meeting feedback.** `infra/new-meeting.py` captures a redacted meeting; each feedback item
  is accepted, rejected, or deferred by a person before it becomes work.
- **Paper library and exploration trails** (`infra/library.py`). Each search is a step file
  another agent can continue or branch from. Preprint and published versions merge into one
  record shown as published. Retracted papers are excluded and counted. Only papers a person
  picks become records; an AI pick stays `proposed`. A library paper never counts as
  experiment evidence. Collections export to BibTeX.
- **Reference supplement.** A references step also asks Crossref and Semantic Scholar and adds
  what OpenAlex's list missed, recording which list found each candidate. References dated
  more than a year after the citing paper are flagged, not dropped.
- `examples/library/` — a real three-step trail with one saved paper and its BibTeX export.
- `CHANGELOG.md`, `SECURITY.md`, and CI on Ubuntu and Windows with Python 3.10 and the latest.

### Validation

- 99 regression tests and `research-lint` in CI.
- Six rounds of cross-lineage review by Codex on the library, the last one finding nothing
  to block a merge.
- Side-by-side retrieval against Research Rabbit on four papers from NLP, structural biology,
  weather, and labour economics; recorded as observations, not as a ranking.
