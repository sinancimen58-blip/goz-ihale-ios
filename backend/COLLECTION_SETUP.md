# GozIhale live source configuration

Collection is opt-in: a source must be listed in `GOZ_IHALE_ENABLED_SOURCE_KEYS` and have an explicitly configured adapter. Do not enable an unreviewed source. The adapters reject non-HTTPS, credentials, fragments, non-public IP addresses and redirects, and cap downloaded content. These checks are defense-in-depth, not a substitute for server isolation and connection-time IP pinning.

## Fast-start: official KHGM listing (HTML)

The KHGM Central Purchasing notice list is a public official listing page and is registered in the source catalog:

`https://khgm.saglik.gov.tr/TR-119527/ihale-duyurulari.html`

On the server, set:

- `GOZ_IHALE_ENABLED_SOURCE_KEYS=khgm_central_notices`
- `GOZ_IHALE_HTML_SOURCE_KEYS=khgm_central_notices`

The registered page URL is used by default. Optional override:

- `GOZ_IHALE_HTML_PAGE_KHGM_CENTRAL_NOTICES`

The adapter captures notice link titles and links from the official listing page; it does not extract the full document text or bid deadlines from attached PDFs. Review its collected output before relying on it operationally. A live collection is only confirmed when the scan ledger records a successful run.

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

1. GET `/api/sources`; confirm the source is enabled and `adapter_ready` is true.
2. POST `/api/run-source/khgm_central_notices` with `X-Goz-Ihale-Token` to run one source, or POST `/api/run-enabled-sources` for all enabled sources.
3. Inspect `/api/scan-runs`, `/api/scan-summary`, `/api/collected-notices`, and `/api/collection-events`.
4. Verify title relevance and original source URLs; review attachments manually for deadlines and technical details.
5. Test iOS using the HTTPS API base URL.
6. Expand to more sources after the first source's successful live run.

## Scheduled jobs

The workflow is scheduled for weekdays at 06:00 and 14:00 UTC (09:00 and 17:00 Turkey time, UTC+3), subject to GitHub scheduling delays. Add the two repository secrets to activate remote collection. Strict scheduling may be better handled on the server.

The source catalog and discovery plans are metadata, not evidence that live collection is working. Mark sources live only after successful scan-ledger verification.

## Additional hospital sources (probed)

- `pau_hospital_purchase`: official Pamukkale University Hospital purchasing listing, `https://www.pau.edu.tr/ihale/tr`. Optional-source CI probe fetched 151 links but yielded no currently relevant ophthalmology notices; it is not a production-live claim.
- `deu_hospital_purchase`: official Dokuz Eylül hospital purchasing page, `https://hastane2.deu.edu.tr/satin-alma/`. The latest optional-source probe failed; keep disabled until successful scan-ledger verification.
- `khgm_supply`: separate KHGM procurement portal. The latest probe could not resolve/validate its host; keep disabled until it is reachable and verified.

The live-source CI workflow probes these sources independently. Network/DNS failure on an optional source must not block the validated primary KHGM source.
