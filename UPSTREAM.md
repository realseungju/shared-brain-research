# Upstream

Shared Brain Research is the researcher-facing distribution of `shared-brain-lite`.

| Field | Value |
|---|---|
| upstream | `https://github.com/realseungju/shared-brain-lite` |
| imported commit | `5209e42241b8b8eb0cc5d6423f725be0530f6533` |
| imported date | 2026-07-28 |
| local base commit | `1552b27` |
| last adopted commit | `e01a353` (English canonical core, 2026-08-30) |

## Ownership boundary

Common core:

- AI entry stubs
- The task and session generators and their schema
- `infra/brain-lint.py`
- The Git hook and the shared regression tests
- `system/RULES.md` and `system/conventions.md`, with their `.ko.md` translations

Owned by this distribution:

- The `research/` project, experiment, and claim contract
- The `feedback/` meeting contract
- `infra/new-experiment.py`, `infra/new-meeting.py`, `infra/research-lint.py`
- Research examples, the cross-agent demo, and the platform compatibility document

Upstream changes are never applied automatically. Review them, take only what the common
core needs, and re-run the full suite (core + research) afterwards.

## Not adopted

| Upstream change | Why not |
|---|---|
| Approval-report renderer (`infra/render-report.py`, 2026-08-30) | On a two-week trial in the private brain. Nothing enters a distribution before it survives there. Revisit after 2026-09-13. |
