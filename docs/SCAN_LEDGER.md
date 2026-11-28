# Source catalog and scan ledger

## API endpoints
- `GET /api/sources` — registry and safe readiness metadata.
- `POST /api/scan-catalog` — audit registry entries without contacting websites.
- `POST /api/run-source/{source_key}` — execute one explicitly enabled adapter.
- `POST /api/run-enabled-sources` — execute enabled sources (write-token protected).
- `GET /api/scan-runs` — recent source-run records.
- `GET /api/scan-summary` — latest run outcome per source.

Each real source run records fetched, relevant, new, updated, unchanged, alert-candidate, duration and retry metrics in the scan ledger. Configured endpoint query credentials are redacted before run-level provenance is stored. The ingestion database keeps consolidated notice records, source observations and change events; the scan ledger database is separate.

Live-source smoke tests use isolated temporary SQLite databases. Their successful result validates a live fetch-and-ingest pipeline for that CI run, but does not prove persistent production collection is deployed. Production collection requires reviewed source access, explicit configuration, durable storage, HTTPS and health validation.
