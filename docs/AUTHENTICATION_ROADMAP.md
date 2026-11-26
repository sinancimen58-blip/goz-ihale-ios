# GozIhale Authentication and Multi-user Architecture

## Target for the iPhone prototype
- Sign-in screen using email/username and password.
- Token-based session; HTTPS only outside local development.
- Sign out and session expiry handling.
- Per-user favorites and notification preferences.
- Admin user management, with roles enforced on the API.

## Backend design (implementation checklist)
1. Account table: UUID, normalized email, display name, password hash, role, enabled, created/updated timestamps.
2. Password storage: Argon2id (or a maintained password-hashing library with secure defaults); never store plaintext or reversible passwords.
3. Login endpoint: rate limited; generic error responses; issue short-lived access token and refresh-token rotation/revocation.
4. Authorization: validate tokens and role on every protected endpoint; admin operations are server-side checks.
5. Password reset: single-use, short-lived token delivered by verified email; avoid account enumeration.
6. Session/device management: revoke sessions, track last-used timestamps, do not store secrets in ordinary app preferences.
7. iOS: store refresh/session credentials in Keychain; clear them on sign out; handle expired sessions.
8. Deployment: HTTPS, secure secrets management, database backups, audit events, and rate limiting.

## Roles
- admin: user/source/configuration management.
- member: notices, search, analyses, own favorites and settings.
- restricted: limited read-only access as defined by server policy.

## Privacy and safety
Authentication must not be simulated as production security. Demo screens must be clearly labeled. Do not expose write tokens or secrets in the iOS app. All access control must be enforced by the server, not just by UI visibility.

## Implementation order
1. Prototype login UI and session states.
2. Backend registration/invite and login/logout/refresh endpoints.
3. Keychain integration and protected API requests.
4. Admin panel and user lifecycle.
5. TestFlight deployment after signing setup.
