# Database and alert policy foundation

This iteration adds a PostgreSQL schema draft (not yet applied to a live database), a persistence-neutral repository contract and alert policy helper.

## Notice entities
- sources: source metadata and enablement status
- notices: normalized opportunity records and raw payload
- notice_sources: source provenance and source URL variants
- notice_events: change history and alert-relevant events

## Alert policy
- New notices: alert by default, priority elevated for high scores.
- Updates: deadline, status and specification changes are high priority.
- Unchanged notices: suppress alert.

## Limitations
No PostgreSQL instance, push provider, email, SMS or source polling has been connected. This is code/schema groundwork only.
