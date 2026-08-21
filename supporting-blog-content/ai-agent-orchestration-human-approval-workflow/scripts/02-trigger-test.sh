#!/bin/bash
# =============================================================================
# Script 02: Trigger test — ingest bad documents to fire the alert
#
# Ingests documents with invalid price values (strings instead of floats)
# into the logs-demo-app data stream. These documents will be redirected
# to the failure store, triggering the alerting rule and starting the
# remediation workflow.
#
# Prerequisites:
#   - Script 01 already executed (data stream exists with failure store)
#   - Alerting rule created and connected to the workflow
#   - ES_URL and ES_API_KEY environment variables set
# =============================================================================

set -euo pipefail

ES_URL="${ES_URL:?Set ES_URL environment variable}"
ES_API_KEY="${ES_API_KEY:?Set ES_API_KEY environment variable}"

AUTH="Authorization: ApiKey ${ES_API_KEY}"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "============================================"
echo "  Trigger Test"
echo "  Timestamp: ${NOW}"
echo "============================================"
echo ""

echo "Ingesting 5 documents with invalid price values..."
echo ""

curl -sS -f -X POST "${ES_URL}/_bulk" \
  -H "${AUTH}" \
  -H "Content-Type: application/x-ndjson" \
  -d "{\"create\":{\"_index\":\"logs-demo-app\"}}
{\"@timestamp\":\"${NOW}\",\"message\":\"Test failure 1\",\"price\":\"INVALID\",\"status\":\"test\",\"user_id\":\"u-test-1\",\"category\":\"test\"}
{\"create\":{\"_index\":\"logs-demo-app\"}}
{\"@timestamp\":\"${NOW}\",\"message\":\"Test failure 2\",\"price\":\"N/A\",\"status\":\"test\",\"user_id\":\"u-test-2\",\"category\":\"test\"}
{\"create\":{\"_index\":\"logs-demo-app\"}}
{\"@timestamp\":\"${NOW}\",\"message\":\"Test failure 3\",\"price\":\"free\",\"status\":\"test\",\"user_id\":\"u-test-3\",\"category\":\"test\"}
{\"create\":{\"_index\":\"logs-demo-app\"}}
{\"@timestamp\":\"${NOW}\",\"message\":\"Test failure 4\",\"price\":\"TBD\",\"status\":\"test\",\"user_id\":\"u-test-4\",\"category\":\"test\"}
{\"create\":{\"_index\":\"logs-demo-app\"}}
{\"@timestamp\":\"${NOW}\",\"message\":\"Test failure 5\",\"price\":\"varies\",\"status\":\"test\",\"user_id\":\"u-test-5\",\"category\":\"test\"}
" | python3 -c "
import sys,json
data = json.load(sys.stdin)
fs = sum(1 for i in data['items'] if i['create'].get('failure_store','')=='used')
print(f'  {fs} documents sent to failure store')
print()
print('  The alerting rule checks every 1 minute.')
print('  Watch Workflows > Executions for the workflow to start.')
"

echo ""
echo "============================================"
