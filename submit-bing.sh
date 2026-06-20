#!/usr/bin/env bash
# submit-bing.sh - Submit URLs to Bing via IndexNow API
# Usage: BING_API_KEY=15b1d26333aa4cd7a1cdba8e813bfc7f ./submit-bing.sh

set -euo pipefail

BING_API_KEY="${BING_API_KEY:-15b1d26333aa4cd7a1cdba8e813bfc7f}"
HOST="salairebrutonet.com"
KEY_LOCATION="https://${HOST}/a7ebea6dfbd14ad6a3efe3c5fab40e46.txt"
ENDPOINT="https://api.indexnow.org/indexnow"

# Collect all URLs from sitemap.xml
URLS=$(grep -oP '(?<=<loc>)[^<]+' sitemap.xml 2>/dev/null || true)

if [ -z "$URLS" ]; then
    echo "No URLs found in sitemap.xml"
    exit 1
fi

# Build JSON array of URLs
URL_JSON=$(echo "$URLS" | while read -r url; do echo "\"$url\""; done | paste -sd, -)

# Submit to IndexNow
echo "Submitting $(echo "$URLS" | wc -l | tr -d ' ') URLs to Bing IndexNow..."

curl -s -X POST "$ENDPOINT" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{
        \"host\": \"${HOST}\",
        \"key\": \"${BING_API_KEY}\",
        \"keyLocation\": \"${KEY_LOCATION}\",
        \"urlList\": [${URL_JSON}]
    }"

echo ""
echo "Done! URLs submitted to IndexNow."
