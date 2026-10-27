# CLAUDE.md: project schema

Every folder in `1-Projects/<Client>/` follows this schema. It loads when any file under `1-Projects/` is read, together with the project's own `CLAUDE.md`.

## Anatomy

```
<Client>/
  CLAUDE.md          canonical sources map and project memory
  README.md          sponsor, stakeholders with their decision role, stack, milestones
  workbook.md        the living discovery document, one section per capability
  log.md             append-only history
  _raw/              immutable evidence: transcripts, emails, documents
  _curated/
    current-state.md what holds today, by domain
    decisions.md     the decision log, one "## D<n>" heading per decision
    meetings/        one note per meeting, distilled from _raw
    analyses/        answers worth keeping
    _superseded/     curated notes that stopped being true
  deliverables/      what goes to the client
```

## Decisions

Each decision gets the next number and its own heading, so other notes can link to it (`[[decisions#D12]]`). When a new decision makes an older one false, entirely or in part, the older one receives a callout in the same session:

```markdown
> [!superseded] 2026-08-12 · replaced by [[#D12]]
> Was: gold tier grace of 30 days.
```

A decision that says it supersedes, replaces or revokes another, while the other has no callout pointing back, fails the lint. Detail, progress or a new status is not supersession. `scripts/check_contradiction.py` compares a new decision against the log before it is recorded.

## Current state

`_curated/current-state.md` is the projection of what holds today, organized by domain (scope, architecture, integrations, data, open blockers, next milestones). It fits in about 150 lines, is written in the present tense and has no history: when something changes, the line is rewritten, never appended. Its frontmatter carries `canonical: current-state` and `verified-on:`, the date it was last checked against the log. A session that records an ingest or a decision updates the lines that changed and moves `verified-on` forward; the lint fails a current state verified before the latest ingest or decision in the log.

## Canonical sources map

Once a project passes about 15 curated notes, its `CLAUDE.md` opens with a "Canonical sources" table: one row per kind of question, each pointing to the one document that is the truth. The current state is the first row. Every document in the table carries `canonical:` and `verified-on:` in its frontmatter. The lint fails a heavy project without the table.

## Pruning

A curated note that stopped being true does not stay in the reading path with a banner. It moves to `_curated/_superseded/` after whatever was unique in it moves to the canonical note. When a living document has one dead claim inside, mark the claim instead of moving the document.

## Workflows

- INGEST: write the raw file first, discuss the takeaways with the owner applying the authority weighting, then write the meeting note, update decisions, workbook and current state, and log it.
- GENERATE: load the workbook, the decisions and the template, write the deliverable with `[PENDING]` where input is missing, and report the open items. Internal references stay in the Markdown source and are removed from what the client receives.
- QUERY: read the current state, then the canonical document for the subject, then answer with citations, saying what was not checked. Offer to file the answer in `analyses/`.
