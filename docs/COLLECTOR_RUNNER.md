# Collector runner scaffold

The runner centralizes adapter execution and handling:
1. Verify the source exists in the registry and is enabled.
2. Require a registered adapter (missing adapter means no request).
3. Collect candidates, screen/category/score them, then persist relevant candidates.
4. Record success/error and count in the scan ledger.

API: POST /api/run-source/{source_key}

Currently all source entries are disabled and ADAPTERS is empty. This implementation is safe scaffolding; it does not make live web requests. Before enabling any adapter, verify official access options, terms, rate limits and data handling.
