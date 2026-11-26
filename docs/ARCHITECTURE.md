# Gözİhale Architecture

## Product
An iPhone-first Turkish ophthalmology procurement intelligence platform.

## Components
- iOS client: SwiftUI
- API: FastAPI
- Storage: PostgreSQL
- Collection: source-specific ingestion workers; comply with site terms, robots policies, access controls and rate limits.
- Notifications: Apple Push Notification Service (APNs)

## Data flow
1. Source adapters collect public listing metadata and source links.
2. Normalization maps listings into a shared tender model.
3. Deduplication identifies repeated notices and updates.
4. Category and relevance scoring prioritize ophthalmology opportunities.
5. API serves filters, saved listings and details to the iOS client.
6. Notifications deliver selected new or changed opportunities.

## Security
- Secrets stored outside source control.
- Authenticated API access.
- Logging, monitoring and backups.
- Respect privacy, site terms, access limits and data retention.
