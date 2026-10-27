# Project: Northwind Grocers

Fictional client used to demonstrate the method. A regional grocery chain with three banners is replacing two legacy loyalty systems with one program on Salesforce.

## Canonical sources

| Question | Source of truth |
|---|---|
| What holds today | [[current-state]] |
| What was decided and why | [[decisions]] |
| Integration architecture | [[integration-architecture]] |
| Discovery status by capability | [[workbook]] |

## Project memory

- The point-of-sale vendor owns the middleware; we consume its events and never write back to it.
- Marketing decides channel and cadence; IT decides data contracts.
