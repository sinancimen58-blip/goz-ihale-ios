# Collection engine

The collector supports explicitly enabled RSS/Atom and conservative official-HTML listing adapters. Candidate notices are screened with ophthalmology procurement keywords and relevance scoring, then normalized, deduplicated and stored in SQLite with source observations and event history. Each source run is recorded in a separate SQLite scan ledger.

The `official-source-smoke` CI workflow performs live probes against selected official pages and uses isolated temporary SQLite databases. It verifies the collection and screening pipeline; it is **not** evidence that production VPS collection or durable production storage is active.

Adapters must prefer documented APIs or permitted public access, respect source terms and rate limits, and never bypass authentication or anti-bot controls. Validate every candidate against its original notice.
