# GozIhale live source configuration

Collection is opt-in: a source must be listed in `GOZ_IHALE_ENABLED_SOURCE_KEYS` and have an explicitly configured adapter. Do not enable an unreviewed source. The adapters reject non-HTTPS, credentials, fragments, non-public IP addresses and redirects, and cap downloaded content. These checks are defense-in-depth, not a substitute for server isolation and connection-time IP pinning.

## Fast-start: official KHGM and DMO HTML listings

The two reviewed public listing pages are:

- KHGM Central Purchasing: `https://khgm.saglik.gov.tr/TR-119527/ihale-duyurulari.html`
- DMO: `https://www.dmo.gov.tr/Ihale/Liste?type=1`

For a VPS, run from the backend folder:

```bash
bash scripts/enable_live_collection.sh
```

The helper writes the two source allowlist values and the exact listing URLs to `.env`, generates a write token if none exists, rebuilds the API, runs both scans, and reports the scan ledger. It preserves other .env entries. The API stays bound to loopback. When root and an active cron service are available, it installs a separate weekday 09:00/17:00 Europe/Istanbul schedule. It does not automatically skip Turkish public holidays.

## RSS/Atom sources

Configure the following only when the official portal offers a verified public feed:
- `GOZ_IHALE_ENABLED_SOURCE_KEYS`: comma-separated enabled keys
- `GOZ_IHALE_FEED_<SOURCE_KEY>`: verified public HTTPS feed URL

## API and security

- Set a strong server-side `GOZ_IHALE_API_WRITE_TOKEN`; never commit it.
- Configure HTTPS and restrict CORS to trusted clients.
- Persist the SQLite files via the Docker volume or equivalent.
- Keep the API private behind a TLS reverse proxy; do not expose the write API over plaintext HTTP.
- GitHub Actions scheduled collection uses `GOZ_IHALE_API_URL` and `GOZ_IHALE_API_TOKEN` secrets and sends the token only to HTTPS. If secrets are missing, the workflow skips.

## Run and verify

Inspect `/api/health`, `/api/sources`, `/api/scan-summary`, `/api/collected-notices`, and `/api/priority-notices`. Verify source links and deadlines; HTML list extraction does not replace manual review of official documents and attachments.

## Current probe status (28 Nov 2026)

The latest completed probe is [GitHub Actions run 46112337925](https://github.com/sinancimen58-blip/goz-ihale-ios/actions/runs/46112337925):

- KHGM central: 187 links fetched, 1 relevant, 1 new notice in an ephemeral CI database.
- Pamukkale University Hospital: 151 links fetched, 0 relevant in the current probe.
- DMO: 86 links fetched, 0 relevant in the current probe.
- EKAP: probe failed; keep disabled.
- Dokuz Eylül: network probe failed; keep disabled.
- KHGM Supply: adapter/configuration missing or invalid; keep disabled.

CI live-source probes use temporary databases; they do not prove production VPS collection is running.

## Optional Telegram alert delivery

Set `GOZ_IHALE_TELEGRAM_BOT_TOKEN` and `GOZ_IHALE_TELEGRAM_CHAT_ID` only in the server's secret environment. The collector stores new/important alert candidates in a deduplicated outbox and delivers them on collection runs when configured. Pending messages are retained without credentials. Status is available at `GET /api/notification-status`; authenticated retry is `POST /api/dispatch-alerts`. Failed deliveries stop after eight attempts.
