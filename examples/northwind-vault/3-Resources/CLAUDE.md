# CLAUDE.md: resources schema

Knowledge that applies to more than one client: platform pitfalls, patterns, playbooks, your own standards. It loads when any file under `3-Resources/` is read.

## Atomic notes

One idea per note, at most one screen. The title carries the conclusion ("Deploying a permission set does not assign it"), the body opens with the context and closes with what changes next time. Frontmatter:

```yaml
type: pattern | pitfall | concept | playbook | reference
origin: <project or incident it came from>
source: <official documentation, measurement or incident, with date>
date: YYYY-MM-DD
```

A note without a source is not cited in a deliverable. This layer is quoted in every client's work, so an unsourced claim here costs the most.

## Promotion

A pattern that shows up in three or more projects becomes a standard in this layer, with a line saying where it came from. A lesson from one project stays in that project until it repeats.

## Supersession

A dead claim inside a living note carries `> [!superseded] DATE · replaced by [[successor]]`. A whole note that stopped being true moves to `_superseded/`.
