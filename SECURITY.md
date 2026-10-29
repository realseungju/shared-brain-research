# Security

## Reporting a problem

Please report security problems privately through GitHub:
**Security → Report a vulnerability** on this repository. Do not open a public issue.

Examples worth reporting: a way for repository content to make an agent run commands it
should not, a lint or generator path that writes outside the repository, or anything that
could leak an API key.

## What this repository stores

- No secrets. API keys (`OPENALEX_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`) are read from the
  environment and never written to a file. Secret scanning with push protection is on.
- Meeting records default to `redacted`. Raw transcripts, participant details, and private
  datasets stay outside the repository.

The tooling uses only the Python standard library, so there are no third-party packages to
patch.
