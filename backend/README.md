# Gözİhale Backend

FastAPI backend prototype with SQLite persistence, a controlled source registry, opt-in HTML/RSS collectors, scan ledger, relevance filtering and notice APIs.

## Run locally

1. Python 3.10+
2. From the backend folder: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload`
4. Open `http://127.0.0.1:8000/docs` for interactive API documentation.

SQLite files are created automatically or configured via environment variables. Demo records are explicitly labeled.

## Live-source validation status

- **KHGM central notice listing:** validated in GitHub Actions using the official public listing; the latest successful test fetched 185 links, screened 1 relevant notice and persisted 1 new notice in a temporary test database. This is CI validation, not a deployed continuous service.
- **Pamukkale University Hospital procurement listing:** public HTML collection succeeded in an optional-source probe (151 links); the current page produced no ophthalmology-relevant candidates at that test.
- **KHGM Supply portal / DEU Hospital purchase:** probes currently report configuration/network failures in the test runner and are not marked live.
- Source collection remains opt-in. Configure and verify sources on a server before enabling scheduled production collection.

## Configuration

See `COLLECTION_SETUP.md` for source keys, HTTPS API write-token, persistent storage, scheduled workflow secrets and smoke-test instructions. See `DOCKER_SETUP.md` and `VPS_SECURITY_CHECKLIST.md` before deployment.
