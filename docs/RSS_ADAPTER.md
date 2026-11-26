# Public RSS/Atom adapter

Gözİhale now has a generic RSS/Atom parser and a runner hook for explicitly configured feeds.

Configuration:
- Environment variable pattern: `GOZ_IHALE_FEED_<SOURCE_KEY>` (key uppercase; hyphens replaced by underscores).
- The source must also be marked enabled in registry.
- Feed URL must be HTTPS.
- Timeout is 10 seconds; response read is limited to 2 MB.
- No feed is configured by default. Feed endpoints must be confirmed to be public and permitted before enabling.
- Parser supports RSS item and Atom entry title, link and summary/description fields.

This is a reusable mechanism, not proof that any official procurement portal provides a feed.
