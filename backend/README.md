# Gözİhale Backend

FastAPI backend prototype with SQLite persistence, a controlled source registry, opt-in HTML/RSS collectors, scan ledger, relevance filtering and notice APIs.

## Run locally

1. Python 3.10+
2. From the backend folder: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload`
4. Open `http://127.0.0.1:8000/docs` for interactive API documentation.

SQLite files are created automatically or configured via environment variables. Demo records are explicitly labeled.

## Live-source validation status

- **KHGM central notice listing:** live GitHub Actions probe on 27 Nov 2026 fetched 187 links, screened 1 ophthalmology-relevant notice and persisted 1 new notice in an ephemeral test database. This is CI validation, not a deployed continuous service.
- **Pamukkale University Hospital procurement listing:** public HTML probe fetched 151 links; no ophthalmology-relevant candidate was found in the current sample.
- **DMO published tender listing:** public HTML probe fetched 92 links; no ophthalmology-relevant candidate was found in the current sample.
- **EKAP bulletin listing:** current adapter probe failed; keep disabled until a successful scan.
- **Dokuz Eylül hospital purchase:** current network probe failed; keep disabled until successful verification.
- **KHGM Supply portal:** current probe reports adapter missing/invalid; keep disabled until endpoint and configuration are reviewed.

## VPS live-source activation

`scripts/enable_live_collection.sh` configures KHGM and DMO, preserves the existing token if present (otherwise creates one), rebuilds Docker Compose and runs both source scans. It installs weekday 09:00/17:00 Europe/Istanbul cron only when run as root and cron is active. See `LIVE_COLLECTION_RUNBOOK.md`.

## Configuration

See `COLLECTION_SETUP.md` for source keys, HTTPS API write-token, persistent storage and scheduled workflow requirements. See `DOCKER_SETUP.md` and `VPS_SECURITY_CHECKLIST.md` before deployment.

## Telegram alert delivery (optional)

The collector writes notification candidates to a durable, deduplicated SQLite outbox. Telegram delivery is optional and requires server-side environment variables:

- `GOZ_IHALE_TELEGRAM_BOT_TOKEN`
- `GOZ_IHALE_TELEGRAM_CHAT_ID`

Never commit these values. If either is missing, alerts remain queued and are not discarded. After configuration, each collection run attempts delivery; `GET /api/notification-status` reports only whether configuration is present and the outbox counts, and authenticated `POST /api/dispatch-alerts` retries queued messages. Failed delivery is retried on subsequent runs up to eight attempts. Verify tender deadlines and source documents independently.

## Priority-notices API filtering

`GET /api/priority-notices` returns a relevance/deadline-sorted shortlist and stable IDs for the iOS client. Optional case-insensitive substring filters: `q` (title, institution, category, summary, specification, source, status and notice ID), `category`, `city`, `status`, and `source_name`. The `limit` parameter is capped at 200; the endpoint screens at most 500 persisted notices per request.
