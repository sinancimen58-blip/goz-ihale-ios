# Gözİhale

Ophthalmology procurement notice intelligence: source discovery, filtering, deduplication, persistence, API and iOS prototype.

## Current sprint
- 72-hour MVP execution target; milestones are verified, not assumed.
- First official source integration: KHGM Central Purchasing notice list (HTTPS HTML adapter).
- Source registry and collection API; SQLite ingestion and scan ledger.
- iOS prototype loads `/api/priority-notices` from a configurable API URL.
- Live collector is not yet deployed to a persistent public server.

## Live progress dashboard

- Intended URL: https://sinancimen58-blip.github.io/goz-ihale-ios/
- The dashboard reads repository commits and GitHub Actions evidence and refreshes every 30 seconds. It does not claim production collection or deployment from CI-only tests.
- Initial GitHub Pages site creation is blocked by the workflow token's integration permissions. One-time manual setup is required: **Settings → Pages → Build and deployment → Source: GitHub Actions**. Then rerun the `Publish live project dashboard` workflow.

## Start here
- [72-hour MVP runbook](docs/MVP_72H_RUNBOOK.md)
- [Collection setup](backend/COLLECTION_SETUP.md)
- [Docker setup](backend/DOCKER_SETUP.md)
- [Security checklist](backend/VPS_SECURITY_CHECKLIST.md)
- [iOS bootstrap](ios/BUILD_BOOTSTRAP.md)

## Local backend
See `backend/README.md` and `backend/DOCKER_SETUP.md`. Configure source keys and source adapters explicitly. Never commit tokens. The API write endpoints require a server-side token.

## Live source verification
The official KHGM listing has a live smoke test in GitHub Actions that fetches, screens, and persists source results in an ephemeral test database. The daily smoke test does not represent production deployment or continuous collection. See [workflow](.github/workflows/official-source-smoke.yml).

## Collection schedule
A HTTPS-gated weekday GitHub Actions workflow is prepared. It remains inactive for remote collection until `GOZ_IHALE_API_URL` and `GOZ_IHALE_API_TOKEN` repository secrets are configured and the server is deployed over HTTPS.

## Latest reliability improvement (2026-11-27)
- Source collection now retries transient DNS lookup failures in addition to transient HTTP/transport errors.
- Retry behavior is covered by automated tests; a retry succeeding is not itself proof that an official source has returned relevant notices.
- Deployment gate: configure HTTPS API URL/token secrets, deploy to a persistent VPS, then verify collection ledger, `/api/priority-notices`, and notification delivery on the deployed instance before enabling scheduled remote scans.
