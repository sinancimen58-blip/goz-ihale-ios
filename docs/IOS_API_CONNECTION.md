# iOS API connection prototype

The SwiftUI home screen requests `GET /api/priority-notices` from the configured API base URL. Settings allow changing and saving that URL. The app validates that the configured base URL is HTTPS before fetching. The Settings connection-test button now calls `GET /api/health`, reports storage and live-source configuration status, and then loads the notice list on a healthy response. The list includes collected notices, relevance/deadline ordering, and urgency enrichment when available.

- Configure the base URL to the deployed API origin, for example `https://api.example.com` (replace with the real deployment URL).
- `GET /api/health` is a read-only deployment diagnostic and can be used to check API storage and the latest recorded source scan.
- Health checks do not prove live collection is configured; inspect the separate `live_collection_configured` and scan-status fields.
- No production URL is bundled into the app yet. Physical-device testing requires a reachable deployment.

Do not expose the write token in the iOS app. Write/collection endpoints require server-side authentication and should only be called from trusted services.
