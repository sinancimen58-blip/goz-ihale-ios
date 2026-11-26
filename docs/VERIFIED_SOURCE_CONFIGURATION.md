# Stage 5 — connecting verified official procurement sources

The collector now supports a source-by-source explicit environment allowlist. No source is enabled by default.

## Configuration

Set:
- `GOZ_IHALE_ENABLED_SOURCE_KEYS`: comma-separated source keys, e.g. `ekap`
- `GOZ_IHALE_FEED_EKAP`: the exact, verified public HTTPS RSS/Atom feed URL for EKAP

For each key, the feed variable is `GOZ_IHALE_FEED_<KEY>`, uppercased and with hyphens replaced by underscores.

Example (placeholder feed URL; do not use until verified):
```env
GOZ_IHALE_ENABLED_SOURCE_KEYS=ekap
GOZ_IHALE_FEED_EKAP=https://example.gov.tr/verified-feed.xml
```

## Safety / status
- Only keys in the allowlist can run.
- The URL must be HTTPS and resolve to public IP addresses.
- RSS adapter rejects redirects and caps its read to 2 MB.
- No feed URL is included in the repository and no source is activated by this commit.
- Feed URLs must be verified against the source's official documentation or public feed page before activation.
- This adapter is for RSS/Atom XML feeds, not HTML scraping.
- A source missing a feed URL or invalid URL is logged as not ready and is not contacted.

## API
`GET /api/sources` now reflects the environment allowlist.
`POST /api/run-source/ekap` executes only when the source is explicitly allowlisted and configured.
`POST /api/scan-catalog` remains a metadata/readiness audit, not a network scan.
