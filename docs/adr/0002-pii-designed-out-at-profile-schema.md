---
status: accepted
---

# PII is designed out of the Profile schema, not redacted at runtime

The brief requires that no personal data (institute names, employer names, etc.) ever reaches an LLM. We decided to enforce this at the data layer: the Profile's JSON schema simply has no fields for employer or institute names, and Experience Entry descriptions are manually genericized by the user (stripped of any incidental employer/product names) before the Profile is authored. The app never accepts or processes a raw, un-scrubbed CV in v1 — the Profile is always already clean by the time it reaches the app.

## Considered Options

- **Runtime redaction/scanning** of freeform profile text for PII before each LLM call — rejected: detection is probabilistic (named-entity recognition can miss names, especially non-Western ones like the user's own), so it can't give the same guarantee as a schema with no PII fields to begin with, and it re-introduces the raw CV as an artifact the app has to handle safely.

## Consequences

This pushes the freeform-CV-to-Profile conversion (mentioned in the brief as a future capability) out of v1 entirely — it becomes a distinct future ingestion module, and *that* module, not this one, will be responsible for solving PII-safe extraction from raw CV text. Until then, Profile authoring is a manual, human-owned step outside the app.
