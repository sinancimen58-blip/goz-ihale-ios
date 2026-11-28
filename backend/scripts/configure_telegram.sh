#!/usr/bin/env bash
set -euo pipefail
umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${BACKEND_DIR}/.env"
cd "${BACKEND_DIR}"

if [[ "${EUID:-$(id -u)}" -ne 0 && ! -w "$ENV_FILE" && ! -w "$BACKEND_DIR" ]]; then
  echo "Run as the owner of backend/.env or with sudo." >&2
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required." >&2
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "backend/.env is missing. Deploy the backend first." >&2
  exit 1
fi

printf "Telegram bot token (input hidden): "
read -r -s BOT_TOKEN
printf "\nTelegram chat ID (numeric, input visible): "
read -r CHAT_ID
printf "\n"

if [[ ! "$BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]{20,}$ ]]; then
  echo "Bot token format is invalid." >&2
  exit 1
fi
if [[ ! "$CHAT_ID" =~ ^-?[0-9]+$ ]]; then
  echo "Chat ID must be a numeric Telegram chat ID." >&2
  exit 1
fi

TMP_FILE="$(mktemp "${BACKEND_DIR}/.env.telegram.XXXXXX")"
trap 'rm -f "$TMP_FILE"' EXIT
awk '!/^[[:space:]]*GOZ_IHALE_TELEGRAM_BOT_TOKEN=/ && !/^[[:space:]]*GOZ_IHALE_TELEGRAM_CHAT_ID=/' "$ENV_FILE" > "$TMP_FILE"
printf "\nGOZ_IHALE_TELEGRAM_BOT_TOKEN=%s\nGOZ_IHALE_TELEGRAM_CHAT_ID=%s\n" "$BOT_TOKEN" "$CHAT_ID" >> "$TMP_FILE"
chmod 600 "$TMP_FILE"
mv "$TMP_FILE" "$ENV_FILE"
trap - EXIT

unset BOT_TOKEN CHAT_ID
docker compose up -d

STATUS="$(curl -fsS "http://127.0.0.1:${GOZ_IHALE_PORT:-8000}/api/notification-status")"
CONFIGURED="$(printf '%s' "$STATUS" | python3 -c 'import json,sys; print(str(json.load(sys.stdin).get("telegram_configured",False)).lower())')"
if [[ "$CONFIGURED" != "true" ]]; then
  echo "Telegram configuration was not confirmed by API." >&2
  exit 2
fi
printf "Telegram credentials saved securely and API configuration confirmed.\n"
printf "Pending alerts are retained; the next scheduled scan will attempt delivery.\n"
