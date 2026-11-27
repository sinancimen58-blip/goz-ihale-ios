# Collector runner scaffold

The runner centralizes adapter execution and handling:
1. Verify the source exists in the registry and is enabled.
2. Require a registered adapter (missing adapter means no request).
3. Collect candidates, screen/category/score them, then persist relevant candidates.
4. Retry collection at most twice, with short bounded delays, for transient timeouts, connection errors, HTTP 408/429 and selected 5xx responses. Permanent HTTP errors, validation failures, parser errors and other non-transient failures are not retried.
5. Record success/error, collection metrics and retry count in the scan ledger.

Retries apply to the read-only fetch stage only; notice ingestion begins after collection succeeds.

API: POST /api/run-source/{source_key}

Currently live adapters are not broadly enabled. This implementation is safe scaffolding; before enabling any adapter, verify official access options, terms, rate limits and data handling.
