---
name: new-vault
description: Create a consulting LLM wiki in a folder, or add a new client project to an existing one. Use when the user says "create my vault", "set up the wiki", "start a vault here", "new client", "add a project for <client>".
---

# New vault or new client

## A new vault

1. Ask for the folder if the user did not name one. An empty folder is expected.
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/new_vault.py" <folder>`. It copies the template, writes the `.llm-wiki` marker that turns the hooks on for that folder, and initializes git.
3. Open the new `CLAUDE.md` with the user and replace the first paragraph with who they are, what they deliver and for whom.
4. Ask which writing packs apply (`en`, `pt-BR`, or both) and set `writing_packs` in `_meta/llm-wiki.json`.
5. Suggest adding a private git remote, so the session hooks can sync and warn about unpushed work. Client material must stay in a private repository.

## A new client

1. Copy `1-Projects/_template/` to `1-Projects/<Client>/`.
2. Fill `README.md` with the sponsor and the stakeholders, including what each one decides, and add the decision owners to `_meta/authority-map.md`.
3. Replace `<Client>` in every file of the new folder.
4. Add the first line to the project's `log.md`.
