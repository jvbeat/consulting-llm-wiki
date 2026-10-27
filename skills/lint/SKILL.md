---
name: lint
description: Check the vault's source locks (superseded claims, unmarked supersessions, stale canonical documents, current state behind the log, missing canonical maps, broken links) and fix the findings. Use when the user says "lint", "check the vault", "is the vault healthy", or before sending a deliverable.
---

# Lint

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py" <vault root>`. Add `--json` for machine-readable output. The exit code is 1 when there is an error, so the same command can gate a CI job.

## What to do with each finding

- `superseded-incomplete`: add the date and the successor link to the callout. If you cannot tell what replaced the claim, ask the owner instead of guessing.
- `superseded-dangling`: the successor does not exist. Fix the link or create the successor note.
- `supersession-unmarked`: add `> [!superseded] <date> · replaced by [[#D<n>]]` to the old decision, with `> Was:` and the part that stopped holding.
- `state-behind-log`: compare the current state with every ingest and decision logged after its `verified-on`, rewrite the lines that changed, and move `verified-on` to today.
- `no-canonical-map`: add the "Canonical sources" table to the project's `CLAUDE.md`, one row per kind of question, with the current state first.
- `canonical-stale` or `canonical-unverified`: check the document against reality (the client, the system, the decision log), then update `verified-on`. Editing the file does not renew it.
- `broken-link`: fix the link to an existing note. Do not guess a target.
- `pending`: report the items that already have an answer somewhere in the vault. Do not invent answers to close them.

Never delete a note to make a finding go away. A note that stopped being true moves to `_curated/_superseded/` after its unique content moves to the canonical note.
