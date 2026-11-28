# Collector runner

The runner centralizes explicitly configured source execution:
1. Resolve a registered source and verify it is enabled.
2. Require a configured, validated adapter (missing/invalid configuration means no request).
3. Collect public candidates, screen/category/score them, and persist relevant notices in SQLite with deduplication and source observations.
4. Retry collection at most twice, with short bounded delays, for transient timeouts, connection errors, HTTP 408/429 and selected 5xx responses. Permanent errors are not retried.
5. Record source outcome and metrics in the scan ledger, then attempt delivery of pending Telegram outbox alerts.

Retries apply to the read-only fetch stage; ingestion begins after collection succeeds. Each source is activated separately via environment configuration and must be reviewed for terms, rate limits and data handling.

API: `POST /api/run-source/{source_key}` (requires the write token).

The live-source smoke CI probes public official pages with temporary databases. It is an isolated test, not a deployed production scan.
