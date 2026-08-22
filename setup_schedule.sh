#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$PROJECT_DIR/daily_digest.sh"
LOG="$PROJECT_DIR/digest.log"
CRON_LINE="0 9 * * * $SCRIPT >> $LOG 2>&1"

# Install the job only if it is not already present.
if crontab -l 2>/dev/null | grep -Fq "$SCRIPT"; then
  echo "Cron job for daily_digest.sh already installed; skipping."
else
  { crontab -l 2>/dev/null | grep -Fv "$SCRIPT"; echo "$CRON_LINE"; } | crontab -
  echo "Installed cron job: daily_digest.sh every day at 09:00."
fi

echo
echo "Resulting crontab entry:"
crontab -l 2>/dev/null | grep -F "$SCRIPT" || echo "(no entry found)"
