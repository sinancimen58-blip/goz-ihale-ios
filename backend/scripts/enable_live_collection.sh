#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${BACKEND_DIR}"

python3 -m app.collector.live_config
docker compose up -d --build

# Install the schedule before the first scan so a transient source outage does
# not prevent future scheduled collection from being configured.
if [[ "${EUID:-$(id -u)}" -eq 0 && -d /etc/cron.d ]]; then
  CRON_ACTIVE=0
  if command -v systemctl >/dev/null 2>&1; then
    systemctl is-active --quiet cron || systemctl is-active --quiet crond || true
    if systemctl is-active --quiet cron || systemctl is-active --quiet crond; then CRON_ACTIVE=1; fi
  fi
  if command -v pgrep >/dev/null 2>&1 && (pgrep -x cron >/dev/null 2>&1 || pgrep -x crond >/dev/null 2>&1); then CRON_ACTIVE=1; fi
  if [[ "$CRON_ACTIVE" -eq 1 ]]; then
    PYTHON="$(command -v python3)"
    cat > /etc/cron.d/gozihale-collection <<EOF
# GozIhale official-source collection (weekdays, Turkey time)
CRON_TZ=Europe/Istanbul
0 9,17 * * 1-5 root $PYTHON $BACKEND_DIR/scripts/run_live_scan.py >> $BACKEND_DIR/scan-cron.log 2>&1
EOF
    chmod 644 /etc/cron.d/gozihale-collection
    echo "Installed weekday 09:00 and 17:00 Europe/Istanbul source scans."
  else
    echo "Cron is not active; scan ran once. Scheduled scan was not installed."
  fi
else
  echo "Not running as root or /etc/cron.d unavailable; scan ran once only."
fi

python3 scripts/run_live_scan.py
