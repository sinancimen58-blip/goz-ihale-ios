# GitHub Actions VPS deployment

The repository has a test-first, SSH deployment workflow for the existing VPS. Deployment is skipped unless the required secrets are configured; backend tests still run.

## One-time GitHub settings

In **Settings → Secrets and variables → Actions** (and the **production** environment if its secrets are environment-scoped), add:

- `DEPLOY_HOST`: VPS DNS name or IP.
- `DEPLOY_USER`: SSH deployment account.
- `DEPLOY_PATH`: existing checkout path, currently expected to be `/opt/goz-ihale-ios`.
- `DEPLOY_SSH_KEY`: private SSH key for that account.
- `DEPLOY_KNOWN_HOSTS`: pinned SSH host-key line(s) for the VPS. Do not disable host verification or use an unverified key.
- Optional `DEPLOY_PORT`: SSH port (defaults to 22).

The account needs permission to fast-forward the `main` checkout and run Docker Compose. Keep backend `.env` on the VPS; Actions does not transfer or overwrite it. Prefer a dedicated deploy account with narrowly scoped permissions.

## Deployment behavior

- Backend tests, Python/shell validation, Docker Compose configuration validation and image build run first.
- Deploy runs only on the `main` branch after the test job passes.
- Missing or malformed deployment settings cause the deploy steps to skip.
- SSH host verification uses the pinned `DEPLOY_KNOWN_HOSTS`.
- The remote update uses `git pull --ff-only`; it will fail instead of resetting or overwriting local changes if the checkout diverges.
- Docker Compose is rebuilt/restarted from `backend`, then the loopback health endpoint is checked with retries.
- The workflow does not configure HTTPS, DNS, reverse-proxy access, iOS signing or push credentials.

Workflow file: `.github/workflows/deploy-vps.yml`.
