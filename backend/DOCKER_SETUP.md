# Docker backend setup (development/self-hosting)

Requirements: Docker and Docker Compose.

1. Copy `.env.example` to `.env`, set a strong write token and reviewed source configuration, then restrict the file to the server owner (`chmod 600 .env`). The Compose service passes this file into the container.
2. From this folder, run `docker compose up --build -d`.
3. Open `http://localhost:8000/` for the API status or `http://localhost:8000/docs` for Swagger.
4. The primary tender database, ingestion database, and scan ledger are explicitly stored under `/data` and persisted in the Docker named volume `gozihale_data`.

This is a setup guide only; the API has not been deployed to a public host by this commit. The prototype currently contains sample data and no live procurement feed configuration. Before exposing publicly, configure authentication/access control, HTTPS, backups, and restrictive CORS/network rules.
