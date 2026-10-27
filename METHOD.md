# The consulting LLM wiki

This is the method behind the repository: a knowledge base for consultants who deliver systems for several clients at the same time, operated by an AI agent (Claude Code) and curated by a person. The code here is a small kit that enforces the method. The method matters more than the code, and you can adopt it with any agent that reads files.

## The problem

A consultant who runs delivery for six clients at once makes hundreds of decisions a month, most of them with someone else. A rule agreed in a workshop in April gets refined by email in May, reversed by the sponsor in June, and asked about again in August. The knowledge exists, scattered across transcripts, threads and documents that each looked final when they were written.

An AI agent with access to that material makes it worse before it makes it better. It reads the April note, finds a clear sentence, and answers with confidence. Nothing in the note says the sentence died in June. The most expensive mistake in a consulting knowledge base is not a missing document or a broken link. It is an old decision read as if it were still valid, by a person or by an agent, and repeated to a client.

## The idea

Andrej Karpathy described the LLM wiki: raw material goes in untouched, an agent distills it into a wiki, and a schema tells the agent how to maintain it. Three operations keep it alive: ingest, query and lint. This method starts there and adds what client work needs:

- a separate layer per client, so knowledge from one client never answers a question about another;
- source locks, so a dead claim cannot pass as a living one;
- authority weighting, so brainstorming in a meeting does not become a decision in the log;
- deliverable templates, so the knowledge turns into requirements, task cards and status reports;
- rules enforced by hooks, because a rule written in prose is forgotten exactly when it is needed.

The agent does the bookkeeping. The person decides what matters.

## Layers

The vault follows PARA (projects, areas, resources, archive) with an inbox in front.

```
0-Inbox/        quick capture, swept weekly
1-Projects/     one folder per client: _raw, _curated, deliverables, workbook, log
2-Areas/        ongoing responsibilities
3-Resources/    knowledge that applies to more than one client
4-Archive/      closed projects
_meta/          configuration, templates, authority map, feedback log
```

Each layer has its own `CLAUDE.md`. Claude Code loads it automatically when it reads a file from that layer, so the rule specific to a layer arrives together with the content. The schema is a contract: if a session has not read anything from a layer yet, it opens the schema before writing there.

Inside a project, `_raw/` holds evidence and is never edited after it is written. `_curated/` holds what the agent distilled and the person approved. `deliverables/` holds what goes to the client.

## Four operations

Every interaction with the vault is one of four operations.

- Ingest happens when material arrives. The raw file is written first, untouched. Then the agent reads it, weighs who said what, and discusses the takeaways with the person before anything is written to the curated layer.
- Generate produces a deliverable. It is built from the workbook, the decision log and a template, with every gap marked `[PENDING]` instead of filled with something plausible.
- Query answers a question. The answer starts from the current state and the canonical source of that domain, cites them, and says what was not checked.
- Lint is maintenance. A script checks the source locks and reports what broke.

Every operation ends with a line in the log of the layer it touched, with a fixed prefix (`## [2026-10-01] ingest | transcript | Loyalty workshop`), so the history can be read with one grep.

## Source locks

These are the core of the method. Each one closes a way an old decision gets read as current.

### Canonical sources map

A project that grows past about fifteen curated notes always has two notes about the same subject: the workshop note and the architecture note, the April plan and the September plan. The project's `CLAUDE.md` therefore opens with a table that names the one source of truth per kind of question. The agent reads that row before opening any note. The lint fails a heavy project without the table.

### Claim-level supersession

Moving a dead document out of the reading path solves the easy case. The hard case is a dead claim inside a living document. The line does not announce that it died, and the next reader trusts it. A dead claim therefore carries a callout with two things:

```markdown
> [!superseded] 2026-09-16 · replaced by [[#D4]]
> Was: tiers recalculated every quarter.
```

The date says when it died. The link says what holds now. The lint fails a callout without either one, because announcing a death without naming the successor is worse than silence: the reader learns the line is wrong and has nowhere to go. It also fails a decision that says it supersedes another while the other carries no mark, and a callout whose successor does not exist.

### Canonical freshness

A canonical document declares when it was last checked against reality:

```yaml
---
canonical: integration-architecture
verified-on: 2026-10-20
---
```

The date is not the last edit. Editing a file does not make it true. The date moves only when someone compared the document with the client, the system or the decision log. The lint warns after 45 days.

### Current state as a projection

Logs grow from the top and nobody reads them whole. A fact recorded in July that still holds becomes invisible, and a fact reversed in September keeps sitting there unmarked. Each project therefore keeps `current-state.md`: what holds today, by domain, in the present tense, in about 150 lines. When something changes, the line is rewritten, never appended. The lint fails a current state that was verified before the latest ingest or decision in the log.

## Authority weighting

Not everything said in a meeting is a decision, and not everyone in the room decides everything. Before an item is recorded as decided, the agent weighs it on two axes:

- who said it: the owner of that domain, a specialist without authority there, someone still learning the subject, or an outsider;
- what was said: a decision, a proposal, a brainstorm or a question. Hedges such as "I think", "maybe" and "what if" demote an item to a proposal.

Only a domain owner making a decision becomes DECIDED. Everything else is PROPOSED until confirmed. When in doubt, demote. The map of who decides what lives in `_meta/authority-map.md` and grows with every meeting. The rule applies to the vault's owner too: thinking out loud in a meeting is not a commitment. AI meeting summaries that list "decisions" count as proposals until checked against the transcript.

## Answers declare their basis

Every factual statement in an answer has one of three bases: measured now, read at the source now, or not checked. The third is said in words inside the sentence. A word like "probably" is not a declaration.

When the person contests an answer, the agent reopens the source before replying, and the reply starts with "I keep" and the evidence, or "I change" and the new evidence. Changing position without new evidence is not allowed. Agreeing to end the discussion is worse than holding a position.

## Feedback becomes rules

Every correction the person makes goes into `_meta/feedback-log.md` with what happened, why the correction holds and how to apply it. When the same kind of correction appears three times, it is promoted to a `CLAUDE.md`. The most recent correction wins.

## Rules become hooks

The most important design lesson came from watching rules fail. A rule written in a schema was followed most of the time and forgotten at the worst moment: the end of a long session, when the agent was tired of context and the commit never happened; the middle of a draft, when the writing rule lost to habit. The fix was to move every rule that cost a session out of prose and into a hook:

- the session start hook syncs the vault before anything is written, and reports broken locks;
- the stop hook warns about uncommitted and unpushed work at the end of every turn;
- the writing gate checks every Markdown file the agent writes and hands the offending lines back.

A rule that lives in a hook is applied every time. A rule that lives in prose is applied when someone remembers it.

## What stays private

The vault holds client material and must live in a private repository. What is public here is the method, the kit and a fictional example. The kit itself sends nothing anywhere: the hooks run locally, and the only model call is the optional contradiction check, made through your own Claude Code session. Claude Code does send what it reads to the model provider, under the terms of your account. Check each client's contract and data policy before filing their material in the vault, and keep personal data out of it.

## Where this came from

The method was built over a year of running delivery for several Salesforce, Braze and Insider One clients at the same time, at a partner consultancy in Brazil. Every lock in it exists because its absence cost real time: a decision resurrected in front of a client, a status answered from a stale note, a brainstorm recorded as a commitment.
