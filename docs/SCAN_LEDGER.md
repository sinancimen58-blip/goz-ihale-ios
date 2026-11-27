# Source catalog and scan ledger

Endpoints:
- GET /api/sources — registry metadata, not proof of active access.
- POST /api/scan-catalog — writes a scan audit entry for every registry source. It deliberately does not contact websites.
- GET /api/scan-runs — recent audit records.

Scan runs include bounded retry counts alongside collection and ingestion metrics. The schema migration adds the field to existing SQLite databases without dropping records.

Statuses currently indicate disabled/not implemented adapter readiness only. Live crawling remains off until adapters are verified against source terms, APIs, rate limits and robots/permissions. This is a scaffold for observability, not live tender results.
