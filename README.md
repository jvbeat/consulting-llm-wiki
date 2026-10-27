# consulting-llm-wiki

[![Tests](https://github.com/jvbeat/consulting-llm-wiki/actions/workflows/tests.yml/badge.svg)](https://github.com/jvbeat/consulting-llm-wiki/actions/workflows/tests.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An LLM wiki for consultants who deliver for many clients at once. Claude Code keeps the books, you curate, and an old decision can no longer pass as a current one.

[Português](README.pt-BR.md) · [The method](METHOD.md)

## Why

A consultant running six projects makes hundreds of decisions a month, and a good share of them get refined, reversed or replaced later. An AI agent reading the vault finds the April note, trusts it and repeats it to the client in August. The most expensive mistake in a consulting knowledge base is not a missing document. It is a dead decision read as a living one.

This repository takes Karpathy's [LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) idea and adds what client delivery needs: a layer per client, source locks that a linter enforces, authority weighting when meetings are ingested, deliverable templates, and hooks that apply the rules instead of hoping someone remembers them.

## What is different

- **Source locks:** A dead claim carries `[!superseded]` with a date and a link to what replaced it, a decision that supersedes another must mark the old one, canonical documents declare when they were last checked against reality, and each project keeps a current state that must be re-verified after every ingest. The lint fails when any of these breaks.
- **Authority weighting:** When a meeting is ingested, every item is weighed by who said it (the domain owner, a specialist, someone learning the subject) and what kind of speech it was (decision, proposal, brainstorm). Only an owner deciding becomes DECIDED.
- **A layer per client:** Raw evidence, curated knowledge and deliverables live inside each project, with a canonical sources map that tells the agent which note is the truth for each kind of question.
- **Deliverables:** Templates for requirements, task cards, meeting notes and status reports, generated from the decision log with `[PENDING]` wherever input is missing.
- **Rules as hooks:** The vault syncs before a session writes, warns about unpushed work when it ends, and checks every Markdown file the agent writes against your writing rules (English and Brazilian Portuguese packs included).

## Quick start

Install the plugin in Claude Code:

```
/plugin marketplace add jvbeat/consulting-llm-wiki
/plugin install consulting-llm-wiki@consulting-llm-wiki
```

Then ask Claude to create your vault:

```
create my vault in ~/consulting-vault
```

The `new-vault` skill copies the template, writes the `.llm-wiki` marker that turns the hooks on for that folder only, and initializes git. Keep the vault in a private repository, because it will hold client material. Claude Code sends what it reads to the model provider, so check each client's contract and data policy before filing their material, and keep personal data out.

Without the plugin, run `python3 scripts/new_vault.py ~/consulting-vault` and copy the skills you want into `.claude/skills/`.

## See the locks work

The repository ships a fictional client, Northwind Grocers, with four problems planted on purpose:

```
$ python3 scripts/lint.py examples/northwind-vault

ERROR (3)
  1-Projects/Northwind-Grocers/workbook.md:7  [superseded-incomplete] superseded callout without date and successor link: say when it died and what replaced it
  1-Projects/Northwind-Grocers/_curated/decisions.md:9  [supersession-unmarked] D5 supersedes D2, but D2 has no [!superseded] callout pointing to D5
  1-Projects/Northwind-Grocers/_curated/current-state.md:1  [state-behind-log] current state verified on 2026-09-20, but the log records an ingest or decision on 2026-10-01

WARN (1)
  1-Projects/Northwind-Grocers/_curated/integration-architecture.md:1  [canonical-stale] canonical "integration-architecture" last verified 103 days ago (limit 45)
```

The current state still says "points never expire", although decision D5 made them expire after twelve months. That is exactly the answer an agent would have given the client. The lint exits with 1, so the same command can gate a CI job.

## What is inside

| Piece | What it does |
|---|---|
| `skills/new-vault` | Creates a vault or adds a client project. |
| `skills/ingest` | Files a transcript, email or document, weighs who said what, and records decisions with supersession. |
| `skills/query` | Answers from the current state and the canonical sources, declaring what was not checked. |
| `skills/generate` | Builds deliverables from the decision log and the templates. |
| `skills/lint` | Runs the source-lock lint and explains how to fix each finding. |
| `hooks` | Session start sync and lock report, stop-time commit warning, writing gate on every Markdown write. |
| `scripts/check_contradiction.py` | Asks a small model which earlier decisions a new one makes false, before it is recorded. |
| `template/` | The vault skeleton with the layer schemas, the project template and the deliverable templates. |
| `METHOD.md` | The method, written so you can adopt it with any agent. |

The hooks act only inside a folder that has the `.llm-wiki` marker, so the plugin never touches your other repositories.

## Configuration

`_meta/llm-wiki.json` in your vault sets the projects folder, how many days a canonical document stays fresh, how many curated notes make a project heavy enough to need a canonical map, and which writing packs apply. To add your own writing rules, drop a pack in `_meta/writing-rules/<name>.json` with the same shape as [writing-rules/en.json](writing-rules/en.json).

## Tests

```
python3 -m unittest discover -s tests
```

The tests prove that the template lints clean, that every planted problem in the example is caught, and that the hooks stay silent outside a vault.

## Credits

The LLM wiki idea comes from [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). The contradiction check follows the edge deduplication prompt of [Graphiti](https://github.com/getzep/graphiti). The folder structure is Tiago Forte's PARA.

Built by [João Victor Beato](https://github.com/jvbeat), Delivery Lead at DDGroup, from a year of running Salesforce, Braze and Insider One delivery for several clients at the same time.

## License

MIT
