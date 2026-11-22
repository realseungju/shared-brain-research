# Feedback

Meetings, reviews, and user observations, kept as improvement inputs whose source stays on
record. This is **Tier 2**: whole meetings are not read at session start. `system/context.md` or a
task points only at the accepted feedback being handled now.

## Core rules

Something said in a meeting is neither a fact nor a decision.

```text
meeting source
→ atomic feedback
→ human triage
→ accepted artifact
→ implementation / experiment
→ validation
```

- The AI may draft feedback candidates, but it never records `human_approved: yes` on a person's
  behalf.
- Every status other than `captured` needs `human_approved: yes`. The field is a provenance
  record of approval, not a device that authenticates who approved. Lint checks only the value
  and its consistency with the status, so real human approval is confirmed through commit and PR
  review or branch protection.
- `accepted` needs a `linked_artifact` — the path of a real task, hypothesis, claim, or ADR.
- `rejected` and `deferred` need a `reason` for the classification. `validation` is used only for
  the result of confirming, after the change landed, that the problem is solved.
- Finishing the implementation is not the same as solving the problem. It is `validated` only
  with a confirmation result.
- A `decision-candidate` becomes accepted only after a person approves it and it is recorded in
  `system/decisions.md`.
- A meeting cannot be changed to `closed` while any `captured`, `accepted`, or `deferred` feedback
  remains. Only `rejected`, or `validated` with real confirmation done, are final states.

The exact fields and allowed values are in `system/conventions.md`.

## Privacy defaults

A new meeting's default `visibility` is `redacted`.

- Public Git gets no real names, contact details, unpublished research information, or raw
  transcripts.
- Record participants by role, not by name.
- For recordings and transcripts, note only where they live outside; keep a summary here.
- Use `source_mode` to tell quotes, paraphrases, and AI inferences apart.

## Creating one

Rather than typing the command, ask the AI to write up the meeting. The canonical command the AI
uses:

```sh
python infra/new-meeting.py weekly-review \
  --title "Weekly research review" \
  --project my-project
```

After creation, fill in the atomic feedback in the `feedback/meetings/` file, and a person decides
each status.
