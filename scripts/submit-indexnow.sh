#!/usr/bin/env bash
# submit-indexnow.sh - Submit all sitemap URLs to IndexNow API
# Usage: ./scripts/submit-indexnow.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load API key from .env
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

API_KEY="${BING_API_KEY:-a7ebea6dfbd14ad6a3efe3c5fab40e46}"
HOST="salairebrutonet.com"
KEY_LOCATION="https://${HOST}/a7ebea6dfbd14ad6a3efe3c5fab40e46.txt"
ENDPOINT="https://api.indexnow.org/indexnow"
SITEMAP_URL="https://${HOST}/sitemap.xml"

# Fetch sitemap and extract URLs
echo "Fetching sitemap from ${SITEMAP_URL}..."
SITEMAP_CONTENT=$(curl -s "$SITEMAP_URL")

if [ -z "$SITEMAP_CONTENT" ]; then
    echo "Error: Could not fetch sitemap from ${SITEMAP_URL}"
    echo "Falling back to local sitemap.xml..."
    SITEMAP_CONTENT=$(cat "$PROJECT_ROOT/sitemap.xml" 2>/dev/null || true)
fi

if [ -z "$SITEMAP_CONTENT" ]; then
    echo "Error: No sitemap content available."
    exit 1
fi

# Extract URLs from sitemap (compatible with both Linux and macOS)
URLS=$(echo "$SITEMAP_CONTENT" | grep -o '<loc>[^<]*</loc>' | sed 's/<loc>//g;s/<\/loc>//g')

if [ -z "$URLS" ]; then
    echo "No URLs found in sitemap."
    exit 1
fi

URL_COUNT=$(echo "$URLS" | wc -l | tr -d ' ')
echo "Found ${URL_COUNT} URLs to submit."

# Build JSON array of URLs
URL_JSON=$(echo "$URLS" | while IFS= read -r url; do echo "\"$url\""; done | paste -sd, -)

# Submit to IndexNow
echo "Submitting ${URL_COUNT} URLs to IndexNow..."

HTTP_CODE=$(curl -s -o /dev/stderr -w "%{http_code}" -X POST "$ENDPOINT" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{
        \"host\": \"${HOST}\",
        \"key\": \"${API_KEY}\",
        \"keyLocation\": \"${KEY_LOCATION}\",
        \"urlList\": [${URL_JSON}]
    }" 2>&1)

echo ""
echo "IndexNow API response code: ${HTTP_CODE}"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "202" ]; then
    echo "Success! ${URL_COUNT} URLs submitted to IndexNow."
else
    echo "Warning: Unexpected response code ${HTTP_CODE}."
fi
