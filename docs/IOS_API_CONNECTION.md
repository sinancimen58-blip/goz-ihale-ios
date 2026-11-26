# iOS API connection prototype

The SwiftUI home screen now requests `GET /api/tenders` and decodes the API response. Settings allow changing and saving the API base URL. A refresh button retries loading; categories are derived from returned records. The interface shows connection failures and no-data state rather than presenting demo notices as live.

Default URL is localhost for development only. On an iPhone, use a reachable backend host/IP and ensure networking permissions/ATS configuration are appropriate for the deployment environment. Do not expose an unsecured API on the public internet.
