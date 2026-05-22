#!/bin/bash
set -u

GAME_DIR="${1:-}"
SLUG="${2:-game-$(date +%s)}"
DOMAIN="${SLUG}.surge.sh"
DESKTOP_FALLBACK="/mnt/c/Users/kiril/Desktop/games/${SLUG}"
SURGE_TIMEOUT_SECONDS="${SURGE_TIMEOUT_SECONDS:-45}"

if [ -z "$GAME_DIR" ] || [ ! -d "$GAME_DIR" ]; then
    echo "ERROR: game directory not found: $GAME_DIR" >&2
    exit 1
fi

if ! command -v surge >/dev/null 2>&1; then
    npm install -g surge --quiet
fi

if timeout "${SURGE_TIMEOUT_SECONDS}s" surge "$GAME_DIR" "$DOMAIN"; then
    echo "GAME_URL:https://$DOMAIN"
    exit 0
fi

mkdir -p "$DESKTOP_FALLBACK"
cp -R "$GAME_DIR"/. "$DESKTOP_FALLBACK"/
echo "SURGE_FAILED" >&2
echo "FALLBACK_PATH:$DESKTOP_FALLBACK"
exit 1
