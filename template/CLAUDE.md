# CLAUDE.md: vault root

This vault is a consulting knowledge base operated by Claude Code. It holds every client project, the knowledge that carries across clients, and the ongoing responsibilities of its owner. Claude keeps the books; the owner decides what matters.

Replace this paragraph with who you are, what you deliver and for whom, so every session starts with that context.

## Principles

1. Raw is immutable. Everything under `_raw/` is evidence and is never edited after it is written.
2. Claude writes, the owner curates. Claude proposes and files; the owner decides what is a decision.
3. Schema is contract. Each layer has its own `CLAUDE.md`, loaded when a file of that layer is read. If a session has not read anything from a layer yet, it opens that schema before writing there.
4. Compounding is mandatory. Every useful answer or analysis is filed back into the vault.
5. The workbook is the center of discovery. One living document per project, not parallel artifacts.
6. Status is written in words: OK, PARTIAL, MISSING, OUT OF SCOPE.
7. Every technical decision in a deliverable cites its decision record or workbook section.
8. `[PENDING: what is missing]` is a friend. A gap is marked, never invented.
9. A task card holds only what the executor needs to execute and accept the task.

## Layers

- `0-Inbox/`: quick capture, swept weekly.
- `1-Projects/`: one folder per client project with `_raw/`, `_curated/`, `deliverables/`, `workbook.md` and `log.md`. Schema in `1-Projects/CLAUDE.md`.
- `2-Areas/`: ongoing responsibilities without an end date.
- `3-Resources/`: knowledge that applies to more than one client. Schema in `3-Resources/CLAUDE.md`.
- `4-Archive/`: closed projects.
- `_meta/`: configuration, templates, the authority map and the feedback log.

## Operations

Every interaction is one of four operations.

- INGEST: material arrived (transcript, email, document). It goes to `_raw/` untouched, and the distilled version goes to `_curated/` after the owner reviews the takeaways.
- GENERATE: a deliverable is needed. It is built from the workbook, the decisions and the templates, with `[PENDING]` where input is missing.
- QUERY: a question. The answer starts from the project's current state and canonical sources, and cites them.
- LINT: maintenance. `scripts/lint.py` checks the source locks below; the lint skill explains what to do with each finding.

## The source locks

The expensive mistake in a consulting vault is not a broken link. It is an old decision read as if it were still valid. Three locks prevent it, and the lint checks all of them.

1. Canonical sources map. A project with many curated notes has, at the top of its `CLAUDE.md`, a table that names the one source of truth per kind of question. Read that row before opening any note.
2. Claim-level supersession. A dead claim inside a living document carries a callout with the date and the successor: `> [!superseded] 2026-08-12 · replaced by [[architecture#tier-grace]]`. A callout without date or successor fails the lint, because announcing that something died without saying what holds now is worse than saying nothing.
3. Canonical freshness. A canonical document declares `canonical:` and `verified-on:` in its frontmatter. The date is when it was last checked against reality (the client, the system, the decision log), not when it was edited. The lint warns after 45 days.

## Answers declare their basis

Every factual statement in an answer has one of three bases: measured now, read at the source now, or not checked. The third is said in words inside the sentence ("I did not check this in the org"). A word like "probably" does not replace that declaration. When the owner contests an answer, the source is reopened first, and the reply starts with "I keep" plus the evidence or "I change" plus the new evidence.

## Authority weighting

Not everything said in a meeting is a decision. Before recording a decision, weigh who said it (decision owner of that domain, specialist, learner, outsider) and what kind of speech act it was (decision, proposal, brainstorm, question). Only a domain owner making a decision becomes DECIDED. Everything else is PROPOSED. The map of who decides what lives in `_meta/authority-map.md`.

## Feedback loop

Every correction from the owner becomes an entry in `_meta/feedback-log.md`. Three equal corrections promote the rule to this file or to the layer schema. The most recent correction wins.

## Logging

Every operation ends with an entry in the `log.md` of the layer it touched:

```
## [YYYY-MM-DD] ingest    | <type> | <title>
## [YYYY-MM-DD] decision  | D<n> | <title>
## [YYYY-MM-DD] generate  | <type> | <name>
## [YYYY-MM-DD] query     | <short question>
## [YYYY-MM-DD] lint      | <findings>
```

## Writing

The writing gate checks every Markdown file Claude writes, with the packs listed in `_meta/llm-wiki.json` (`en`, `pt-BR` or your own in `_meta/writing-rules/`). Errors block until fixed; warnings come back as context.

## Sessions

A session that changed the vault ends with commit and push. The session start hook pulls before anything is written, and the stop hook warns about uncommitted or unpushed work.
