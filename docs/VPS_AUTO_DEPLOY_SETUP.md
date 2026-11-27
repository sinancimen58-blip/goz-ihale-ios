# GitHub Actions VPS deployment

This repository can deploy the backend to the existing VPS over SSH after tests pass. Deployment is intentionally gated; it is not enabled until repository settings are configured.

## One-time GitHub settings

In **Settings → Secrets and variables → Actions**:

1. Add the repository variable `VPS_DEPLOY_ENABLED` with value `true`.
2. Add these repository secrets:
   - `VPS_HOST`: VPS DNS name or IP.
   - `VPS_USER`: SSH deployment account.
   - `VPS_SSH_KEY`: private SSH key for that account.
   - `VPS_KNOWN_HOSTS`: pinned SSH host-key line(s) for the VPS (do not use an unverified key).
3. Optional secret `VPS_PORT`: SSH port (defaults to 22).

The SSH account needs read access to the existing checkout at `/opt/goz-ihale-ios`, permission to fast-forward the `main` branch, and Docker Compose access. Keep the backend `.env` file on the VPS; it is not transferred by Actions.

## Deployment behavior

- Runs backend tests, script syntax checks, Compose validation, and image build first.
- Only deploys on `main` after those checks pass, and only when `VPS_DEPLOY_ENABLED=true`.
- SSH host verification is pinned using `VPS_KNOWN_HOSTS`; host-key checking is not disabled.
- Uses `git pull --ff-only`; it will fail rather than overwrite local divergence.
- Rebuilds and restarts Compose from `backend`, then checks `/api/health` over loopback.
- A missing deploy flag skips the deploy job. Tests still run.
- The workflow does not configure HTTPS, DNS, reverse-proxy access, iOS signing or push credentials.

Workflow file: `.github/workflows/deploy-vps.yml`.
