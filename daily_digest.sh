#!/usr/bin/env bash
set -euo pipefail

# Where this script lives; the whole loop runs relative to the project.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRESS_FILE="$PROJECT_DIR/progress.md"
TODAY="$(date +%Y-%m-%d)"

# The spine and the project's own docs/scripts are not code, so the scan
# skips them (and .git) so the system never digests itself.
SCAN_EXCLUDES=(
  --exclude=progress.md
  --exclude=README.md
  --exclude=digest.log
  --exclude=daily_digest.sh
  --exclude=setup_schedule.sh
  --exclude-dir=.git
)

cd "$PROJECT_DIR"

# Step 1 - make sure the spine exists; create it fresh instead of crashing.
if [ ! -f "$PROGRESS_FILE" ]; then
  printf '# Progress Log\n' > "$PROGRESS_FILE"
fi

# Step 2 - collect every TODO that past runs already reported.
# Bullet lines look like "- path:line | text"; rebuild "path:line|text" signatures.
KNOWN="$(sed -n 's/^- \([^|]*\) | \(.*\)$/\1|\2/p' "$PROGRESS_FILE")"

# Step 3 - scan the repo for the TODO comments that exist right now.
SCAN="$(grep -rna "TODO" "${SCAN_EXCLUDES[@]}" . || true)"

# Normalize grep output ("./path:line:content") into the same signature format.
CURRENT="$(printf '%s\n' "$SCAN" \
  | sed -n 's#^\./\([^:]*\):\([0-9][0-9]*\):\(.*\)$#\1:\2|\3#p' \
  | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

# Step 4 - diff: only signatures not previously reported count as new.
NEW="$(printf '%s\n' "$CURRENT" | while IFS= read -r sig; do
  if ! printf '%s\n' "$KNOWN" | grep -Fqx "$sig"; then
    printf '%s\n' "$sig"
  fi
done)"

COUNT="$(printf '%s\n' "$NEW" | sed '/^[[:space:]]*$/d' | wc -l | tr -d ' ')"
PLURAL=""
if [ "$COUNT" -ne 1 ]; then
  PLURAL="s"
fi

# Step 5 - build this run's entry and append (never overwrite) to progress.md.
if [ "$COUNT" -eq 0 ]; then
  if [ -z "$CURRENT" ]; then
    SUMMARY="No new TODOs since last run (the repo currently has no TODO comments at all)."
  else
    SUMMARY="No new TODOs since last run."
  fi
  ENTRY="## $TODAY

$SUMMARY
"
else
  ENTRY="## $TODAY

**$COUNT new TODO${PLURAL} since last run:**

"
  while IFS= read -r sig; do
    ENTRY="${ENTRY}- ${sig%%|*} | ${sig#*|}
"
  done <<< "$NEW"
fi

printf '\n%s' "$ENTRY" >> "$PROGRESS_FILE"

# Step 6 - print the same summary to the terminal.
printf '%s' "$ENTRY"

exit 0
