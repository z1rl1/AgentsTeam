#!/bin/bash
GAME_DIR="$1"
SLUG="${2:-game-$(date +%s)}"
DOMAIN="${SLUG}.surge.sh"
if ! command -v surge &> /dev/null; then
    npm install -g surge --quiet
fi
surge "$GAME_DIR" "$DOMAIN" 2>/dev/null || echo "SURGE_FAILED"
echo "GAME_URL:https://$DOMAIN"
