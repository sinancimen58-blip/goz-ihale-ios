# 72-Hour MVP Runbook

Goal: deliver a usable iPhone MVP backed by real, verified procurement notices. This is a sprint target, not a guarantee.

## Definition of done
- API deployed over HTTPS with persistent storage and write-token protected collection endpoints.
- At least 2-3 permitted, reachable official sources configured and live-tested; no source is marked live until the scan log confirms it.
- Relevant notices filtered, normalized, deduplicated, persisted, and ranked.
- iOS app loads /api/priority-notices from the deployed API and displays source links and deadline urgency.
- Scheduled collection is enabled only after HTTPS and server-side token configuration are verified.
- CI is green; deployment and source scan status are recorded.

## Sprint order
1. **Backend/deploy:** Docker, reverse proxy/HTTPS, persistent DB, health checks, token configuration.
2. **Source discovery:** reviewed official HTML/RSS adapters; start with KHGM and DMO, then add more only after a successful probe.
3. **Data quality:** screen ophthalmology terms, normalize fields, deduplicate, preserve provenance, record run failures.
4. **iOS:** use Settings to configure the HTTPS API; smoke-test list, refresh, favorite, search, and source link.
5. **Automation:** enable scheduled scans after API endpoint/token are safely configured in GitHub Actions secrets or server environment.
6. **Expansion:** add more institutions and sources after first live data is verified.

## First live-source activation

From the backend folder on the VPS, run `bash scripts/enable_live_collection.sh`. It configures only the two reviewed sources, preserves existing .env entries, creates a write token if needed, rebuilds Docker Compose and runs both scans. It installs weekday 09:00/17:00 Europe/Istanbul cron only when root and an active cron service are available. Turkish public holidays are not automatically skipped. Details: `backend/LIVE_COLLECTION_RUNBOOK.md`.

## Required server-side environment
- GOZ_IHALE_API_WRITE_TOKEN: strong random secret; never commit it.
- GOZ_IHALE_ENABLED_SOURCE_KEYS: comma-separated enabled source keys.
- GOZ_IHALE_FEED_<KEY>: public HTTPS feed URL for enabled RSS/Atom sources.
- GOZ_IHALE_HTML_SOURCE_KEYS and GOZ_IHALE_HTML_PAGE_<KEY>: optional reviewed HTML source settings.
- GOZ_IHALE_DB, GOZ_IHALE_INGEST_DB, GOZ_IHALE_SCAN_DB: persistent storage paths.
- GOZ_IHALE_CORS_ORIGINS: restrict to required clients.

## Explicit blockers needing operator access
- Public HTTPS domain/reverse-proxy configuration.
- GitHub Actions secrets for remote HTTPS collection, if that schedule is preferred.
- Apple developer signing/TestFlight credentials if distribution beyond local build is desired.
- Access restrictions or terms of service on source endpoints; do not bypass them.
