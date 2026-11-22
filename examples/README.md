# Examples — Shared Brain Research

**These are examples to read. The files here are not live records.**

If `system/sessions/` and `tasks/done/` shipped filled in, someone cloning this repository as a
template would find another person's records mixed into their own Tier 0. So the real-looking
outputs live here, only to show their shape, and the live tree ships empty.

| Path | What |
|---|---|
| `research/demo-vision/` | A fictional study that runs all the way from question → experiment → evidence → supported claim |
| `feedback/meetings/` | A redacted meeting showing accepted, rejected, and deferred once each |
| `sessions/` | Two sessions: Claude Code plans, Hermes takes over |
| `tasks/` | A task closed with an experiment result path |
| `cross-agent-demo/` | Steps to reproduce a cross-AI handoff |
| `library/` | A library trail that was really run (prior work for `demo-vision`): references → branching into citations (newest first) and related works, one paper a person picked, BibTeX |

## Notes

- Every number, commit, and dataset is a fictional fixture. None of it is real model performance
  or a real research result.
- Exception: `library/` is the real output of OpenAlex, Crossref, and Semantic Scholar on
  2026-10-29. The paper data is real, but as of that day. The `chosen_by: human` in `step-01` was
  picked by a person (Deep RL That Matters). The `⚠` on item 13 of `step-01`, "Datasheets for
  datasets", is a real case — the 2019 paper cited the 2018 arXiv version, but OpenAlex linked the
  2021 CACM version.
- Do not copy these files to use as live records; create them with the generators:

```sh
python infra/new-task.py {slug} --title "Title"
python infra/new-session.py {slug} --agent {name} --tags {tags} \
  --hook "One-line summary for the index" --did "What was done" --next "What is next"
python infra/new-experiment.py {slug} --project {project} \
  --title "Experiment title" --hypothesis {hypothesis}
python infra/new-meeting.py {slug} --title "Meeting title" --project {project}
```

- Lint does not check `examples/` as live records. Instead, a regression test copies these files
  into the live locations of an empty repository and runs `research-lint`, so when the schema
  changes the examples break along with it and the breakage shows
  (`infra/tests/test_examples.py`).
