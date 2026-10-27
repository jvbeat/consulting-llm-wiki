---
canonical: integration-architecture
verified-on: 2026-07-15
---

# Integration architecture: Northwind Grocers

Point-of-sale transactions are published by the vendor's middleware as events. Salesforce consumes them into Loyalty Management as transaction journals, and Data Cloud receives the same events for segmentation.

The middleware is the system of record for transactions. Salesforce never writes back to it.
