# Live-source activation on the VPS

The collector is opt-in. This helper configures three reviewed official HTML sources: KHGM central notices, DMO, and Pamukkale University Hospital procurement listings. It preserves unrelated .env entries, generates a write token if none exists, rebuilds Docker Compose and runs all three scans.

From the repository backend folder on the VPS:

```bash
bash scripts/enable_live_collection.sh
```

The script keeps the API bound to loopback by Docker Compose. It does not expose port 8000 or configure a reverse proxy. If cron is already active and the script is run as root, it installs an isolated `/etc/cron.d/gozihale-collection` schedule for weekdays at 09:00 and 17:00 Europe/Istanbul. It does not automatically skip Turkish public holidays. If cron is inactive, the initial scan still runs and no schedule is installed.

After the run, inspect:

- `/api/health`
- `/api/sources`
- `/api/scan-summary`
- `/api/collected-notices`
- `/api/priority-notices`

The script does not configure a public HTTPS domain, iOS signing, push-notification credentials or GitHub Actions secrets. Those remain separate deployment tasks. Do not expose the write token or the plain HTTP API to the internet.


Each scheduled live scan also checks the Telegram outbox. If server-side Telegram credentials are configured, it calls the protected `/api/dispatch-alerts` endpoint to attempt delivery of retained alerts and prints delivery counts. If credentials are absent, it skips dispatch and reports the retained pending count; no alert is discarded. The scheduled runner never prints token or chat-ID values.
