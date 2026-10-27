---
name: generate
description: Generate a client deliverable (business requirements, task cards, status report, meeting minutes) from the project's workbook, decisions and templates. Use when the user asks for a BRD, a backlog, a task card, a status report or any document for the client or the delivery team.
---

# Generate

1. Load, in this order: the project's `current-state.md`, `workbook.md`, `_curated/decisions.md`, the relevant meeting notes, and the template in `_meta/templates/`.
2. Write the deliverable in `1-Projects/<Client>/deliverables/`. In the Markdown source, cite the decision or workbook section behind each requirement.
3. Mark every gap as `[PENDING: what is missing and from whom]`. Never fill a gap with a plausible value.
4. A task card carries only what the executor needs to execute and accept the task: system context, what to do, what is already decided and the definition of done. Project management, stakeholder history and items that do not block stay out of the card.
5. The version that leaves the vault (document, spreadsheet, message) drops internal references. When a reason matters, it becomes plain language ("the client decided", "required by the contest rules").
6. Append `## [YYYY-MM-DD] generate  | <type> | <name>` to the project log and report the open `[PENDING]` items and what the deliverable was checked against.
