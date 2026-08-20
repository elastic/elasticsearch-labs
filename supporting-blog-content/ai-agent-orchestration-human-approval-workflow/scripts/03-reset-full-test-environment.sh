#!/usr/bin/env bash
# Full reset for the failure-store remediation tutorial.
#
# Removes:
#   - remediation-runs index
#   - logs-demo-app data stream (backing indices + failure store)
#   - ingest pipelines whose IDs contain "logs-demo-app"
#   - logs-demo-app-template index template
#
# Usage:
#   export ES_URL="https://your-project.es.region.gcp.elastic.cloud:443"
#   export ES_API_KEY="your-api-key"
#
#   ./scripts/03-reset-full-test-environment.sh                # preview
#   ./scripts/03-reset-full-test-environment.sh --apply        # apply with confirmation
#   ./scripts/03-reset-full-test-environment.sh --apply --yes  # non-interactive
#   ./scripts/03-reset-full-test-environment.sh --apply --pipeline-id my-pipeline

set -euo pipefail

DATA_STREAM="${DATA_STREAM:-logs-demo-app}"
INDEX_TEMPLATE="${INDEX_TEMPLATE:-logs-demo-app-template}"
AUDIT_INDEX="${AUDIT_INDEX:-remediation-runs}"

APPLY=false
ASSUME_YES=false
EXTRA_PIPELINES=""

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --apply                 Perform deletions (default: preview only).
  --yes                   Skip confirmation prompt (requires --apply).
  --pipeline-id <id>      Also delete this exact pipeline ID (repeatable).
  -h, --help              Show this help.

Environment variables:
  ES_URL          Elasticsearch endpoint (required).
  ES_API_KEY      Elasticsearch API key (required).
  DATA_STREAM     Default: logs-demo-app
  INDEX_TEMPLATE  Default: logs-demo-app-template
  AUDIT_INDEX     Default: remediation-runs
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=true; shift ;;
    --yes) ASSUME_YES=true; shift ;;
    --pipeline-id)
      [[ $# -lt 2 || -z "${2:-}" ]] && { echo "Error: --pipeline-id requires a value." >&2; exit 2; }
      EXTRA_PIPELINES="$EXTRA_PIPELINES $2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if $ASSUME_YES && ! $APPLY; then
  echo "Error: --yes requires --apply." >&2; exit 2
fi

ES_URL="${ES_URL:-}"
ES_API_KEY="${ES_API_KEY:-}"

if [[ -z "$ES_URL" || -z "$ES_API_KEY" ]]; then
  echo "Error: ES_URL and ES_API_KEY must be set." >&2
  echo "  export ES_URL=https://your-project.es.region.gcp.elastic.cloud:443" >&2
  echo "  export ES_API_KEY=<your-api-key>" >&2
  exit 1
fi

for cmd in curl python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Error: $cmd not found." >&2; exit 1; }
done

ES_URL="${ES_URL%/}"
AUTH="Authorization: ApiKey ${ES_API_KEY}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

urlencode() {
  python3 -c "from urllib.parse import quote; import sys; print(quote(sys.argv[1], safe=''))" "$1"
}

http_status() {
  curl -sS -o "$TMP/response.json" -w "%{http_code}" -X "$1" "$ES_URL$2" -H "$AUTH"
}

http_delete() {
  local label="$1" path="$2" status
  status="$(curl -sS -o "$TMP/del.json" -w "%{http_code}" -X DELETE "$ES_URL$path" -H "$AUTH")"
  case "$status" in
    200) echo "   OK     $label deleted" ;;
    404) echo "   OK     $label did not exist" ;;
    *)   echo "   ERROR  $label (HTTP $status)" >&2
         [[ -s "$TMP/del.json" ]] && sed 's/^/     /' "$TMP/del.json" >&2
         return 1 ;;
  esac
}

# Discover pipelines whose IDs contain the data stream name
http_status GET "/_ingest/pipeline" > /dev/null
PIPELINE_IDS="$(python3 - "$TMP/response.json" "$DATA_STREAM" "$EXTRA_PIPELINES" <<'PY'
import json, sys

path = sys.argv[1]
needle = sys.argv[2].lower()
extras = sys.argv[3].split() if len(sys.argv) > 3 else []

with open(path) as f:
    data = json.load(f)

found = [pid for pid in sorted(data) if needle in pid.lower()]
all_ids = found + extras

# deduplicate preserving order
seen = set()
result = []
for pid in all_ids:
    if pid and pid not in seen:
        result.append(pid)
        seen.add(pid)

print("\n".join(result))
PY
)"

# Preview
echo ""
echo "Full reset preview"
echo "=================="
echo "Elasticsearch:   $ES_URL"
echo "Audit index:     $AUDIT_INDEX"
echo "Data stream:     $DATA_STREAM"
echo "Index template:  $INDEX_TEMPLATE"
echo ""

printf "  %-46s HTTP %s\n" "Audit index ($AUDIT_INDEX):" \
  "$(http_status GET "/$(urlencode "$AUDIT_INDEX")/_count")"
printf "  %-46s HTTP %s\n" "Data stream ($DATA_STREAM):" \
  "$(http_status GET "/_data_stream/$(urlencode "$DATA_STREAM")")"
printf "  %-46s HTTP %s\n" "Failure store:" \
  "$(http_status GET "/$(urlencode "${DATA_STREAM}::failures")/_count")"
printf "  %-46s HTTP %s\n" "Index template ($INDEX_TEMPLATE):" \
  "$(http_status GET "/_index_template/$(urlencode "$INDEX_TEMPLATE")")"

echo ""
if [[ -z "$PIPELINE_IDS" ]]; then
  echo "  Ingest pipelines: none found matching '$DATA_STREAM'"
else
  echo "  Ingest pipelines to delete:"
  echo "$PIPELINE_IDS" | while IFS= read -r pid; do
    [[ -n "$pid" ]] && echo "    - $pid"
  done
fi

echo ""
echo "Before applying: disable the alerting rule and confirm no workflow execution is active."
echo ""

if ! $APPLY; then
  echo "Preview only. Run with --apply to delete."
  exit 0
fi

if ! $ASSUME_YES; then
  read -r -p "Type RESET to confirm deletion: " confirm
  [[ "$confirm" == "RESET" ]] || { echo "Cancelled."; exit 1; }
fi

echo ""
echo "Applying reset..."
echo ""

echo "1. Deleting audit index..."
http_delete "$AUDIT_INDEX" "/$(urlencode "$AUDIT_INDEX")"

echo ""
echo "2. Deleting data stream (backing indices + failure store)..."
http_delete "$DATA_STREAM" "/_data_stream/$(urlencode "$DATA_STREAM")"

echo ""
echo "3. Deleting ingest pipelines..."
if [[ -z "$PIPELINE_IDS" ]]; then
  echo "   OK     no matching pipelines"
else
  echo "$PIPELINE_IDS" | while IFS= read -r pid; do
    [[ -n "$pid" ]] && http_delete "pipeline $pid" "/_ingest/pipeline/$(urlencode "$pid")"
  done
fi

echo ""
echo "4. Deleting index template..."
http_delete "$INDEX_TEMPLATE" "/_index_template/$(urlencode "$INDEX_TEMPLATE")"

echo ""
echo "Verifying..."
FAILED=false

verify_gone() {
  local label="$1" path="$2" status
  status="$(http_status GET "$path")"
  if [[ "$status" == "404" ]]; then
    echo "   OK     $label is absent"
  else
    echo "   ERROR  $label still responds HTTP $status" >&2
    FAILED=true
  fi
}

verify_gone "audit index"    "/$(urlencode "$AUDIT_INDEX")/_count"
verify_gone "data stream"    "/_data_stream/$(urlencode "$DATA_STREAM")"
verify_gone "failure store"  "/$(urlencode "${DATA_STREAM}::failures")/_count"
verify_gone "index template" "/_index_template/$(urlencode "$INDEX_TEMPLATE")"

if [[ -n "$PIPELINE_IDS" ]]; then
  while IFS= read -r pid; do
    [[ -n "$pid" ]] && verify_gone "pipeline $pid" "/_ingest/pipeline/$(urlencode "$pid")"
  done < <(printf '%s\n' "$PIPELINE_IDS")
fi

echo ""
if $FAILED; then
  echo "Reset finished with errors. Review messages above." >&2
  exit 1
fi

echo "Full reset completed."
echo "Next: run ./scripts/01-setup-failure-store.sh to rebuild the scenario."
