# Three explicit extension seams: input source, Profile ingestion, and interface

The brief requires the system stay modular enough to extend later without rework, but named three specific, already-anticipated extensions rather than "extensibility" in the abstract: (1) pasted JobPosting text today → a web-scraper input source later, (2) manually-authored Profile JSON today → automated freeform-CV-to-Profile extraction later, (3) single-user local Streamlit today → multi-user web app later. We decided to treat each as an explicit module boundary from the start — the scoring/aggregation core depends on a JobPosting and a Profile as data, never on how either was produced — rather than deferring the abstraction until the extension is actually built.

## Consequences

This is a deliberate exception to YAGNI: normally we wouldn't build a seam before it's needed. It's justified here because the brief names these three extensions specifically (not speculative future-proofing), so the cost of the seam is paid once, up front, while the core is still small.
