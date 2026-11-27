# Platform Compatibility

Checked: first on 2026-07-28, again on 2026-10-29. Windows.

| Platform | Checked | Repository entry contract | Verdict |
|---|---|---|---|
| Claude Code | 2026-10-29, built and verified the library feature in this repository from the desktop app | Root `CLAUDE.md` | Confirmed in real use |
| Codex CLI 0.164.0 | 2026-10-29, `codex --version`; continued a library trail with no prior context (below) | Root `AGENTS.md` | Confirmed in real use |
| Hermes Agent 0.22.5 | 2026-10-29, `hermes --version` | Loads `AGENTS.md` and `CLAUDE.md` from the cwd | Version confirmed (local code checked on 0.17.0) |

**Cross-agent real use (2026-10-29):** Codex, with no earlier conversation, read only the files
and continued a library trail that Claude Code had built, from `step-02`. The per-step inputs,
directions, and proposals Codex reported matched what was really there, the existing step files
were unchanged, and `research-lint` passed.

**Environment needs of the library feature:** it needs network access. OpenAlex and Semantic
Scholar keys are optional and a person puts them in environment variables. Do not let an agent
hand a key to an external model process.

This table records checks of the executable, the working directory, the entry-file contract, and
the real use above. It is not a benchmark of model answer quality or automatic compliance. To
check it yourself, close a session in Claude Code, start Hermes in the same repository, and walk
through `examples/cross-agent-demo/`.

## Common usage

1. Set the repository root as the platform's project, workspace, or working directory.
2. Ask the AI to read the repository instructions first.
3. Ask in plain language for the research work and the record update together.
4. Have the agent run `research-lint` and close the session.

The evidence that Hermes reads context files from the cwd: in the installed Hermes,
`agent/agent_init.py` and the cron workspace initialization code were checked to load
`AGENTS.md` and `CLAUDE.md`.
