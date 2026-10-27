# Example: Northwind Grocers

`northwind-vault/` is a vault created from the template, with one fictional client: a regional grocery chain replacing two legacy loyalty systems with one program. Everything in it is invented.

The client project breaks the source locks on purpose, so you can see the lint catch them:

```
python3 scripts/lint.py examples/northwind-vault
```

- `workbook.md` has a superseded callout with no date and no successor.
- Decision D5 says it supersedes D2, and D2 carries no mark. D4 replacing D3 shows the correct form.
- `current-state.md` was verified before the latest ingest, and it still says points never expire.
- `integration-architecture.md` is canonical and was last verified more than 45 days ago.

The meeting note `2026-10-01-loyalty-workshop.md` shows authority weighting: the returns rule said by the Head of CRM is decided, and the welcome bonus suggested by an analyst who is still learning the loyalty model stays proposed.
