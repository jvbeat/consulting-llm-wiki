---
name: ingest
description: Ingest a meeting transcript, an email thread or a document into a client project of the vault, weighting who said what before anything becomes a decision. Use when the user says "ingest the call", "file this transcript", "read the client's reply", "add this document to <client>", or drops material that belongs to a project.
---

# Ingest

The goal is mechanical bookkeeping that stops at the point of judgment: Claude files, the owner decides what is a decision.

## 1. Identify the material and the project

Confirm the project before writing. When the user did not say, infer it from the participants and the subject against the `README.md` of each project, and ask. Never guess silently.

## 2. Write the raw file

Save the material untouched in `1-Projects/<Client>/_raw/` as `YYYY-MM-DD-<topic>.md`, with a frontmatter that records the date, the source and the participants. If a file with the same source already exists, do not duplicate it. Never edit a raw file after writing it.

## 3. Discuss the takeaways (stop here)

Read the material and weigh every candidate item on two axes before showing it to the owner:

- Who said it, according to `_meta/authority-map.md`: the owner of that domain, a specialist, a learner or an outsider.
- What kind of speech act it was: decision, proposal, brainstorm or question. Hedges ("I think", "maybe", "could", "what if") demote an item to proposal.

Present the items in groups: Decided (only a domain owner making a decision, with the literal quote), Proposed, Open items (with owner and due date when said), Risks, and Ambiguities marked `[PENDING]`. An AI meeting summary that lists decisions counts as Proposed until checked against the transcript. Wait for the owner's review.

## 4. Write the curated note

Create `_curated/meetings/YYYY-MM-DD-<topic>.md` from `_meta/templates/meeting-note.md`, with only what the owner confirmed and a link to the raw file.

## 5. Record decisions

For each confirmed decision:

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_contradiction.py" _curated/decisions.md <file with the new decision>` and read both texts for every decision it returns.
2. Add the decision to `_curated/decisions.md` with the next number.
3. Mark every earlier decision that stopped holding, in the same session: `> [!superseded] YYYY-MM-DD · replaced by [[#D<n>]]`, followed by `> Was: <what stopped holding>`. A partial supersession names the part.

## 6. Update the projection

Rewrite the lines of `_curated/current-state.md` that the material changed, move `verified-on` to today, update the workbook status, and add the authority signals you learned to `_meta/authority-map.md`.

## 7. Log and report

Append `## [YYYY-MM-DD] ingest    | <type> | <topic>` to the project `log.md`, and `decision` lines for each new decision. Report what was filed, what stayed `[PENDING]` and the next action.
