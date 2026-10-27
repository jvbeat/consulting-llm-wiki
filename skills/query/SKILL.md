---
name: query
description: Answer a question about a client project or about cross-client knowledge from the vault, starting from the canonical sources and declaring the basis of every statement. Use when the user asks what was decided, what the status is, how something works in a project, or what the vault knows about a topic.
---

# Query

1. Read the project's `_curated/current-state.md`. It says what holds today and points to the canonical document of each domain.
2. Read the row of the "Canonical sources" table in the project's `CLAUDE.md` and open the document it names. Use other notes only for what the table does not cover.
3. If the question names a decision, a card or a document, read it whole before answering. Redo any arithmetic in writing.
4. Answer with citations (`[[decisions#D12]]`, `[[2026-10-01-loyalty-workshop]]`). Give every factual statement its basis: measured now, read at the source now, or not checked, and say the third one in words inside the sentence.
5. Before answering from a canonical document, look at its `verified-on`. If it is older than the limit in `_meta/llm-wiki.json`, say so in the answer.
6. Offer to file the answer in `_curated/analyses/<short-question>.md`, and log it if filed.

When the user contests an answer, reopen the source first. Start the reply with "I keep" and the evidence, or "I change" and the new evidence. Changing position without new evidence is not allowed.
