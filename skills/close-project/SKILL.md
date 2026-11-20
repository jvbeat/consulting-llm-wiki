---
name: close-project
description: Close, freeze or hand over a client project at the end of an engagement, leaving a dossier for a future case study or a return of the client, and returning heavy raw files and personal data to the client instead of keeping them. Use when the user says "the project was delivered", "close the X project", "archive X", "the client left", "freeze X", "X is with another lead now", "the client came back", "reopen X".
---

# Close, freeze or hand over a project

A closed project moves to `4-Archive/` with a dossier that answers the two questions that come back later: how to present the case, and how to restart if the client returns. Closing is also when client data leaves your custody.

## 1. Confirm the outcome

Ask the owner, if they have not said it: delivered, left without delivery, frozen (comes back later) or handed over to another lead. A frozen project only gets a notice at the top of its `CLAUDE.md` and stays in `1-Projects/`.

## 2. Write the closing dossier

Create `_curated/closing-dossier.md` from `_meta/templates/closing-dossier.md`, at most two screens, built from the README, the project `CLAUDE.md`, the current state, the decision log and the end of `log.md`. Anything the vault does not hold stays as `[PENDING]`, never inferred.

## 3. Hand the raw material back

- Text evidence (transcripts, emails, meeting notes) stays in the vault: it is small, and it is what search and the case study use.
- An image without text is described in a sibling note before it leaves. Only images whose visual is the information stay as images.
- Heavy binaries (images, video, PDF, spreadsheets) go to storage the client controls. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/raw_offload.py" 1-Projects/<Client> <client folder>` to see the list, then again with `--apply`. Each file is copied, its SHA-256 is checked against the original, it is recorded in `_raw/MANIFEST.md`, and only then deleted from the vault.
- Extractions with personal data (customer contacts, IDs, emails) do not stay after closing: they are returned to the client or deleted, and the owner's decision is written in the project log.

## 4. Move and relink

- Move the folder with `git mv 1-Projects/<Client> 4-Archive/<Client>`.
- Run the lint and fix every link that pointed into the old path.
- Add `## [YYYY-MM-DD] handoff   | project archived` to the project log.

## 5. Reopen

When the client comes back, the folder returns from `4-Archive/` to `1-Projects/`, the dossier is the first thing read, and a new current state is written from it, dated with the restart.
