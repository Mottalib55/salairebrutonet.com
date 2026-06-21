#!/bin/bash
# submit-indexnow.sh — Submit all sitemap URLs to IndexNow API
# Usage: ./scripts/submit-indexnow.sh

set -euo pipefail

DOMAIN="https://salairebrutonet.com"
HOST="salairebrutonet.com"
KEY="dc6156f9d98f4267ab490ed4b6606c7a"
API="https://www.bing.com/indexnow"

echo "Fetching sitemap..."
ALL_URLS=$(curl -s "$DOMAIN/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's/<loc>//g;s/<\/loc>//g')
TOTAL=$(echo "$ALL_URLS" | wc -l | tr -d ' ')
echo "Found $TOTAL URLs in sitemap."

# Build JSON payload
URL_LIST=$(echo "$ALL_URLS" | jq -R -s -c 'split("\n") | map(select(length > 0))')

JSON=$(jq -n \
  --arg host "$HOST" \
  --arg key "$KEY" \
  --argjson urlList "$URL_LIST" \
  '{host: $host, key: $key, keyLocation: ("https://" + $host + "/" + $key + ".txt"), urlList: $urlList}')

echo "Submitting $TOTAL URLs to IndexNow..."

RESPONSE=$(curl -s -X POST "$API" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$JSON" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

case "$HTTP_CODE" in
  200) echo "Success! $TOTAL URLs submitted and accepted." ;;
  202) echo "Success! $TOTAL URLs submitted and accepted for processing." ;;
  400) echo "Error 400 (Bad Request): $BODY" ;;
  403) echo "Error 403 (Forbidden): Key not valid. $BODY" ;;
  422) echo "Error 422 (Unprocessable): URLs don't belong to the host. $BODY" ;;
  429) echo "Error 429 (Too Many Requests): Try again later. $BODY" ;;
  *)   echo "Unexpected response (HTTP $HTTP_CODE): $BODY" ;;
esac
