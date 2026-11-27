# VPS Deployment and Security Checklist

This checklist is for the GozIhale FastAPI prototype running on an Ubuntu VPS behind Nginx.

## Current status and limitations
- API is a development prototype; demo records may be returned.
- Live procurement collection is not yet validated or enabled.
- No production authentication has been audited.
- Do not use the API for sensitive or critical decisions until hardening and source validation are complete.

## Docker port binding
On a VPS behind Nginx, bind the API only to loopback:
`127.0.0.1:${GOZ_IHALE_PORT:-8000}:8000`.
Do not expose port 8000 to the public Internet.

## Host firewall
Allow only SSH (preferably restricted to your IP), HTTP, and HTTPS. Do not expose SQLite, Docker socket, or API port 8000 publicly. Verify firewall rules before enabling them; retain a working SSH session while changing rules.

## Nginx and TLS
- Proxy to `http://127.0.0.1:8000`.
- Preserve Host and forwarded headers.
- Configure TLS using a trusted certificate and automatic renewal.
- Disable or protect Swagger/OpenAPI endpoints in production, or restrict them to trusted users/IPs.
- Configure reasonable request size, timeout and rate limits.

## Secrets and authentication
- Keep tokens and credentials in a root-owned environment file, mode 600, not in Git.
- Use strong, unique secrets and rotate any exposed credentials.
- Implement authenticated access and authorization before real users or sensitive data.
- Never use a shared write token as the sole production authorization model.

## Database and backup
- Keep SQLite files on a persistent Docker volume.
- Back up the database daily, encrypt backups, store a copy off-server, and periodically test restores.
- Avoid copying SQLite files while writes are active unless using a safe backup method.

## Validation steps
1. `docker compose config`
2. `docker compose up -d --build`
3. `docker compose ps`
4. `curl -fsS http://127.0.0.1:8000/`
5. `nginx -t`
6. Test HTTPS from a separate device.
7. Confirm port 8000 is not publicly reachable.

## Data integrity
Mark records as unverified until their official source, publication date, deadline, and tender status are validated. Do not present demo records as real notices.
