# Gözİhale deployment readiness

## Current state
- API and iOS prototype are in the repository.
- SQLite persistence, ingestion event log, source catalog, scan ledger, relevance scoring, deadline parsing and urgency labels exist.
- CI live-source smoke tests have fetched and screened official pages in isolated runs. The scheduled production collection workflow remains a framework: it needs a persistent HTTPS API URL and write token, and its remote sources must be explicitly configured and enabled.
- iOS is not yet built or tested in Xcode or on a physical device.

## Before public deployment
1. Configure verified official feeds/API endpoints, one source at a time.
2. Enable each source only after its access method and terms are reviewed.
3. Replace wildcard CORS with an explicit deployment origin policy (or remove CORS for a native-only API).
4. Set `GOZ_IHALE_API_WRITE_TOKEN` to a long random secret; POST write/collection endpoints require it in the `X-Goz-Ihale-Token` header. Without the environment token, those endpoints return 503. Add rate limiting as a separate deployment control.
5. Use HTTPS and a protected secret store for any feed configuration.
6. Persist the SQLite database on a durable volume and back it up.
7. Run CI tests and record results.
8. Configure an actual iOS API base URL and test on device.

## Deadline priority
The priority-notices endpoint adds `days_remaining` and `urgency` fields to each notice, where the urgency labels are Turkish-language triage labels. These are informational; always confirm deadlines against the original official notice and its addenda.


## Write endpoint protection (implemented)
- `POST /api/tenders`, `POST /api/collect/record`, `POST /api/scan-catalog`, and `POST /api/run-source/{source_key}` require `X-Goz-Ihale-Token` matching the `GOZ_IHALE_API_WRITE_TOKEN` environment variable.
- If the variable is absent, these endpoints fail closed with HTTP 503; incorrect or missing request token returns HTTP 401.
- Store the token only in the hosting provider's secret settings. Do not commit it to GitHub or the app source.
- This is a basic shared-secret gate, not a substitute for HTTPS, rate limiting, origin restrictions, or a stronger identity system.

## Health endpoint

- `GET /api/health` performs read-only SQLite checks across the API, ingestion, and scan-ledger stores and reports the latest recorded source outcomes.
- A healthy storage result is **not** proof that live collection is configured or currently running. The response separates storage checks from `live_collection_configured` and the last recorded scan.
- The notice count is capped at 500 for a lightweight diagnostic response.

## Live-source milestone — 28 November 2026

The official-source smoke workflow completed successfully on commit `2897376c3c153995d810f1c4b4a0cd23497812c4` (run [46109606139](https://github.com/sinancimen58-blip/goz-ihale-ios/actions/runs/46109606139)). The live probes reported:

| Source | Status | Fetched links/candidates | Relevant screened | New in isolated run |
|---|---|---:|---:|---:|
| KHGM central notices | success | 187 | 1 | 1 |
| DMO | success | 86 | 0 | 0 |
| Pamukkale University hospital purchase | success | 151 | 0 | 0 |
| KHGM supply page | adapter missing/invalid | 0 | 0 | 0 |
| Dokuz Eylül hospital purchase | error | 0 | 0 | 0 |
| EKAP | error | 0 | 0 | 0 |

The one KHGM candidate was persisted as a new notice in the run's temporary SQLite database. These numbers are CI smoke evidence only: the temporary databases are discarded after the run, and the production VPS/API/health and Telegram delivery are still unverified.
