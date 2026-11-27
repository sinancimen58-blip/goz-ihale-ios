# 72-Hour MVP Runbook

Goal: deliver a usable iPhone MVP backed by real, verified procurement notices. This is a sprint target, not a guarantee.

## Definition of done
- API deployed over HTTPS with persistent storage and write-token protected collection endpoints.
- At least 2-3 permitted, reachable official sources configured and live-tested; no source is marked live until the scan log confirms it.
- Relevant notices filtered, normalized, deduplicated, persisted, and ranked.
- iOS app loads /api/priority-notices from the deployed API and displays source links and deadline urgency.
- Scheduled collection is enabled only after HTTPS and server-side token configuration are verified.
- CI is green; deployment and source scan status are recorded.

## Sprint order (work streams can overlap)
1. **Backend/deploy:** Docker, reverse proxy/HTTPS, persistent DB, health checks, token configuration.
2. **Source discovery:** start with official RSS/feed endpoints where available; otherwise a small reviewed official HTML listing adapter. Confirm source terms, final URL, host, and successful scan before enabling.
3. **Data quality:** screen ophthalmology terms, normalize fields, dedupe, preserve provenance, record run failures.
4. **iOS:** use Settings to configure the HTTPS API; smoke-test list, refresh, favorite, search, and source link.
5. **Automation:** enable scheduled scans after API endpoint/token are safely configured in GitHub Actions secrets or server environment.
6. **Expansion:** add more institutions and sources after first live data is verified.

## Required server-side environment
- GOZ_IHALE_API_WRITE_TOKEN: strong random secret; never commit it.
- GOZ_IHALE_ENABLED_SOURCE_KEYS: comma-separated reviewed source keys.
- GOZ_IHALE_FEED_<KEY>: public HTTPS feed URL for enabled RSS/Atom sources.
- GOZ_IHALE_HTML_SOURCE_KEYS and GOZ_IHALE_HTML_PAGE_<KEY>: optional, reviewed HTML source settings.
- GOZ_IHALE_DB, GOZ_IHALE_INGEST_DB, GOZ_IHALE_SCAN_DB: persistent storage paths.
- GOZ_IHALE_CORS_ORIGINS: restrict to required clients.

## First smoke-test sequence
1. GET / and /api/sources; verify status and adapter readiness.
2. Configure and enable only a reviewed source with a feed URL.
3. POST /api/run-source/<key> with X-Goz-Ihale-Token; verify successful run in /api/scan-runs and /api/scan-summary.
4. GET /api/collected-notices and /api/priority-notices; verify provenance and relevance.
5. Configure the iOS app with the HTTPS base URL and refresh.
6. Enable schedule only after secrets and HTTPS are verified.

## Explicit blockers needing operator access
- VPS/hosting account and DNS/domain for deployment.
- Secret token configuration in server environment and/or GitHub Actions.
- Apple developer signing/TestFlight credentials if distribution beyond local build is desired.
- Access restrictions or terms of service on source endpoints; do not bypass them.
