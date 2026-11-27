# GozIhale public-feed collection configuration

The RSS/Atom adapter is intentionally allowlisted, HTTPS-only, redirect-blocking and rejects non-public DNS addresses.

## Server configuration
Configure these environment variables on the VPS (never commit tokens or private feed URLs):
- `GOZ_IHALE_ENABLED_SOURCE_KEYS`: comma-separated keys, e.g. `ekap,dmo`
- `GOZ_IHALE_FEED_EKAP`: verified RSS/Atom feed URL (HTTPS)
- `GOZ_IHALE_FEED_DMO`: verified RSS/Atom feed URL (HTTPS)

Only verified public feeds should be configured. The registry URL is a discovery entry point, not proof of a working feed endpoint. Many procurement portals do not expose RSS; don't assume these URLs work.

## Running
After HTTPS and authentication are properly configured, run the collector from the server or use the authenticated API. GitHub scheduled triggers remain paused until the API is protected by TLS.

## Scheduled jobs
GitHub Actions schedules use UTC. 06:00 and 14:00 UTC map to 09:00 and 17:00 Turkey time (UTC+3), on weekdays. GitHub scheduling may delay execution. Use server-side scheduled jobs if strict timing is required.
