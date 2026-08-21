#!/usr/bin/env bash
# =============================================================================
# Script 04: Verify the completed happy path
#
# Validates the final state after:
#   1. scripts/01-setup-failure-store.sh
#   2. cleanup of the setup failure-store documents
#   3. scripts/02-trigger-test.sh
#   4. Gate 1 approved
#   5. Gate 2 approved (resolved)
#
# The script is read-only except for refresh operations.
# It validates:
#   - final document counts
#   - the five test documents in logs-demo-app
#   - preserved price_raw values and absence of pipeline errors
#   - original document IDs restored from the failure store
#   - a remediation pipeline using recover_failure_document
#   - remediation-runs containing awaiting_fix_approval and resolved
#   - a non-empty agent_report in the resolved audit record
#
# Required environment variables:
#   ES_URL
#   ES_API_KEY
#
# Optional overrides:
#   EXPECTED_MAIN_COUNT=8
#   EXPECTED_FAILURE_COUNT=5
#   EXPECTED_TEST_DOCS=5
#   EXPECTED_FINAL_STATUS=resolved
# =============================================================================

set -euo pipefail

ES_URL="${ES_URL:?Set ES_URL environment variable}"
ES_API_KEY="${ES_API_KEY:?Set ES_API_KEY environment variable}"

EXPECTED_MAIN_COUNT="${EXPECTED_MAIN_COUNT:-8}"
EXPECTED_FAILURE_COUNT="${EXPECTED_FAILURE_COUNT:-5}"
EXPECTED_TEST_DOCS="${EXPECTED_TEST_DOCS:-5}"
EXPECTED_FINAL_STATUS="${EXPECTED_FINAL_STATUS:-resolved}"

AUTH_HEADER="Authorization: ApiKey ${ES_API_KEY}"
CONTENT_TYPE="Content-Type: application/json"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

api_request() {
  local method="$1"
  local path="$2"
  local output_file="$3"
  local body="${4:-}"

  if [[ -n "${body}" ]]; then
    curl -sS -f -X "${method}" "${ES_URL}${path}" \
      -H "${AUTH_HEADER}" \
      -H "${CONTENT_TYPE}" \
      -d "${body}" \
      > "${output_file}"
  else
    curl -sS -f -X "${method}" "${ES_URL}${path}" \
      -H "${AUTH_HEADER}" \
      > "${output_file}"
  fi
}

print_header() {
  echo "============================================"
  echo "  Happy Path Final Verification"
  echo "============================================"
  echo "Elasticsearch: ${ES_URL}"
  echo "Expected main count: ${EXPECTED_MAIN_COUNT}"
  echo "Expected failure-store count: ${EXPECTED_FAILURE_COUNT}"
  echo "Expected test documents: ${EXPECTED_TEST_DOCS}"
  echo "Expected final status: ${EXPECTED_FINAL_STATUS}"
  echo ""
}

print_header

echo "[1/6] Refreshing indices..."
api_request POST "/logs-demo-app/_refresh" "${TMP_DIR}/refresh-main.json"
api_request POST "/logs-demo-app::failures/_refresh" "${TMP_DIR}/refresh-failures.json"
api_request POST "/remediation-runs/_refresh" "${TMP_DIR}/refresh-audit.json"
echo "  OK"
echo ""

echo "[2/6] Reading final counts..."
api_request GET "/logs-demo-app/_count" "${TMP_DIR}/main-count.json"
api_request GET "/logs-demo-app::failures/_count" "${TMP_DIR}/failure-count.json"
echo "  OK"
echo ""

echo "[3/6] Reading destination and failure-store documents..."
api_request POST "/logs-demo-app/_search" "${TMP_DIR}/main-search.json" '{
  "size": 100,
  "track_total_hits": true,
  "query": {"match_all": {}},
  "_source": [
    "@timestamp",
    "user_id",
    "message",
    "price",
    "price_raw",
    "status",
    "category",
    "pipeline_error"
  ]
}'

api_request POST "/logs-demo-app::failures/_search" "${TMP_DIR}/failure-search.json" '{
  "size": 100,
  "track_total_hits": true,
  "query": {"match_all": {}},
  "_source": [
    "document.id",
    "document.source.user_id",
    "document.source.price",
    "error.type",
    "error.message"
  ]
}'
echo "  OK"
echo ""

echo "[4/6] Reading remediation pipelines..."
api_request GET "/_ingest/pipeline" "${TMP_DIR}/pipelines.json"
echo "  OK"
echo ""

echo "[5/6] Reading remediation audit history..."
api_request POST "/remediation-runs/_search" "${TMP_DIR}/audit-search.json" '{
  "size": 100,
  "track_total_hits": true,
  "query": {"match_all": {}},
  "_source": [
    "data_stream",
    "triggered_by_rule",
    "failure_count",
    "status",
    "reviewer_feedback",
    "notes",
    "agent_report"
  ]
}'
echo "  OK"
echo ""

echo "[6/6] Validating results..."

EXPECTED_MAIN_COUNT="${EXPECTED_MAIN_COUNT}" \
EXPECTED_FAILURE_COUNT="${EXPECTED_FAILURE_COUNT}" \
EXPECTED_TEST_DOCS="${EXPECTED_TEST_DOCS}" \
EXPECTED_FINAL_STATUS="${EXPECTED_FINAL_STATUS}" \
VERIFY_TMP_DIR="${TMP_DIR}" \
python3 <<'PY'
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


tmp = Path(os.environ["VERIFY_TMP_DIR"])
expected_main_count = int(os.environ["EXPECTED_MAIN_COUNT"])
expected_failure_count = int(os.environ["EXPECTED_FAILURE_COUNT"])
expected_test_docs = int(os.environ["EXPECTED_TEST_DOCS"])
expected_final_status = os.environ["EXPECTED_FINAL_STATUS"]

expected_values = {
    "u-test-1": "INVALID",
    "u-test-2": "N/A",
    "u-test-3": "free",
    "u-test-4": "TBD",
    "u-test-5": "varies",
}

failures: list[str] = []
warnings: list[str] = []
passes: list[str] = []


def load(name: str) -> Any:
    with (tmp / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def pass_check(message: str) -> None:
    passes.append(message)
    print(f"  PASS - {message}")


def fail_check(message: str) -> None:
    failures.append(message)
    print(f"  FAIL - {message}")


def warn_check(message: str) -> None:
    warnings.append(message)
    print(f"  WARN - {message}")


def nested_contains_key(value: Any, target: str) -> bool:
    if isinstance(value, dict):
        if target in value:
            return True
        return any(nested_contains_key(child, target) for child in value.values())
    if isinstance(value, list):
        return any(nested_contains_key(child, target) for child in value)
    return False


main_count_data = load("main-count.json")
failure_count_data = load("failure-count.json")
main_search = load("main-search.json")
failure_search = load("failure-search.json")
pipelines = load("pipelines.json")
audit_search = load("audit-search.json")

main_count = int(main_count_data.get("count", -1))
failure_count = int(failure_count_data.get("count", -1))

print("")
print("  Final counts")
print(f"    logs-demo-app:           {main_count}")
print(f"    logs-demo-app::failures: {failure_count}")

if main_count == expected_main_count:
    pass_check(f"logs-demo-app count is {expected_main_count}")
else:
    fail_check(
        f"logs-demo-app count is {main_count}; expected {expected_main_count}"
    )

if failure_count == expected_failure_count:
    pass_check(f"failure-store count is {expected_failure_count}")
else:
    fail_check(
        f"failure-store count is {failure_count}; expected {expected_failure_count}"
    )

main_hits = main_search.get("hits", {}).get("hits", [])
main_test_hits: dict[str, list[dict[str, Any]]] = {
    user_id: [] for user_id in expected_values
}

for hit in main_hits:
    source = hit.get("_source", {})
    user_id = source.get("user_id")
    if user_id in main_test_hits:
        main_test_hits[user_id].append(hit)

print("")
print("  Remediated test documents")
found_destination_docs = sum(len(items) for items in main_test_hits.values())

if found_destination_docs == expected_test_docs:
    pass_check(f"found {expected_test_docs} remediated u-test-* documents")
else:
    fail_check(
        f"found {found_destination_docs} remediated u-test-* documents; "
        f"expected {expected_test_docs}"
    )

for user_id, expected_raw in expected_values.items():
    hits = main_test_hits[user_id]
    if len(hits) != 1:
        fail_check(f"{user_id} appears {len(hits)} times in logs-demo-app; expected 1")
        continue

    hit = hits[0]
    source = hit.get("_source", {})
    actual_raw = source.get("price_raw")
    price_value = source.get("price", "<absent>")
    pipeline_error = source.get("pipeline_error")

    if actual_raw == expected_raw:
        pass_check(f"{user_id} preserved price_raw={expected_raw!r}")
    else:
        fail_check(
            f"{user_id} has price_raw={actual_raw!r}; expected {expected_raw!r}"
        )

    if price_value is None or price_value == "<absent>":
        pass_check(f"{user_id} has no incompatible price value")
    else:
        fail_check(f"{user_id} still has price={price_value!r}")

    if pipeline_error in (None, ""):
        pass_check(f"{user_id} has no pipeline_error")
    else:
        fail_check(f"{user_id} has pipeline_error={pipeline_error!r}")

failure_hits = failure_search.get("hits", {}).get("hits", [])
failure_by_user: dict[str, list[dict[str, Any]]] = {
    user_id: [] for user_id in expected_values
}

for hit in failure_hits:
    source = hit.get("_source", {})
    document = source.get("document", {})
    original = document.get("source", {})
    user_id = original.get("user_id")
    if user_id in failure_by_user:
        failure_by_user[user_id].append(hit)

print("")
print("  Failure-store records and original IDs")
found_failure_docs = sum(len(items) for items in failure_by_user.values())

if found_failure_docs == expected_test_docs:
    pass_check(f"failure store still contains the {expected_test_docs} source records")
else:
    fail_check(
        f"failure store contains {found_failure_docs} matching source records; "
        f"expected {expected_test_docs}"
    )

for user_id, expected_raw in expected_values.items():
    failure_hits_for_user = failure_by_user[user_id]
    destination_hits_for_user = main_test_hits[user_id]

    if len(failure_hits_for_user) != 1:
        fail_check(
            f"{user_id} appears {len(failure_hits_for_user)} times in the failure store; "
            "expected 1"
        )
        continue

    failure_hit = failure_hits_for_user[0]
    failure_source = failure_hit.get("_source", {})
    failure_document = failure_source.get("document", {})
    original_source = failure_document.get("source", {})
    original_id = failure_document.get("id")
    original_price = original_source.get("price")

    if original_price == expected_raw:
        pass_check(f"{user_id} failure record preserves price={expected_raw!r}")
    else:
        fail_check(
            f"{user_id} failure record has price={original_price!r}; "
            f"expected {expected_raw!r}"
        )

    if len(destination_hits_for_user) == 1:
        destination_id = destination_hits_for_user[0].get("_id")
        if original_id and destination_id == original_id:
            pass_check(f"{user_id} restored original document ID {original_id}")
        else:
            fail_check(
                f"{user_id} destination _id={destination_id!r}, "
                f"failure-store document.id={original_id!r}"
            )

print("")
print("  Remediation pipeline")

if not isinstance(pipelines, dict) or not pipelines:
    fail_check("no ingest pipeline matching '*logs-demo-app*' was found")
else:
    selected_pipeline_id: str | None = None
    selected_pipeline: dict[str, Any] | None = None

    for pipeline_id, definition in pipelines.items():
        if not isinstance(definition, dict):
            continue
        has_recover = nested_contains_key(definition, "recover_failure_document")
        mentions_price_raw = "price_raw" in json.dumps(definition, sort_keys=True)
        if has_recover and mentions_price_raw:
            selected_pipeline_id = pipeline_id
            selected_pipeline = definition
            break

    print("    Matching pipeline IDs:")
    for pipeline_id in sorted(pipelines):
        print(f"      - {pipeline_id}")

    if selected_pipeline_id and selected_pipeline:
        pass_check(
            f"pipeline {selected_pipeline_id!r} uses recover_failure_document "
            "and preserves price_raw"
        )

        processors = selected_pipeline.get("processors", [])
        processor_types: list[str] = []
        if isinstance(processors, list):
            for processor in processors:
                if isinstance(processor, dict):
                    keys = [key for key in processor if not key.startswith("_")]
                    if keys:
                        processor_types.append(keys[0])
        if processor_types:
            print(f"    Processor sequence: {' -> '.join(processor_types)}")
    else:
        fail_check(
            "no matching pipeline contains both recover_failure_document "
            "and a price_raw transformation"
        )

print("")
print("  remediation-runs audit history")

audit_hits = audit_search.get("hits", {}).get("hits", [])
statuses: list[str] = []
resolved_reports: list[str] = []
awaiting_failure_counts: list[Any] = []

for hit in audit_hits:
    source = hit.get("_source", {})
    status = source.get("status")
    if isinstance(status, str):
        statuses.append(status)
    if status == "awaiting_fix_approval":
        awaiting_failure_counts.append(source.get("failure_count"))
    if status == expected_final_status:
        report = source.get("agent_report")
        if isinstance(report, str) and report.strip():
            resolved_reports.append(report.strip())

print(f"    Statuses found: {', '.join(statuses) if statuses else '<none>'}")

if "awaiting_fix_approval" in statuses:
    pass_check("audit history contains awaiting_fix_approval")
else:
    fail_check("audit history does not contain awaiting_fix_approval")

if expected_final_status in statuses:
    pass_check(f"audit history contains final status {expected_final_status}")
else:
    fail_check(f"audit history does not contain final status {expected_final_status}")

if any(str(value) == str(expected_test_docs) for value in awaiting_failure_counts):
    pass_check(
        f"awaiting_fix_approval records failure_count={expected_test_docs}"
    )
else:
    warn_check(
        "no awaiting_fix_approval record has the expected failure_count; "
        f"values found: {awaiting_failure_counts}"
    )

if resolved_reports:
    pass_check(f"{expected_final_status} record contains a non-empty agent_report")
    report_preview = resolved_reports[-1].replace("\n", " ")
    if len(report_preview) > 500:
        report_preview = report_preview[:500] + "..."
    print(f"    Agent report preview: {report_preview}")
else:
    fail_check(f"no {expected_final_status} record contains agent_report")

print("")
print("============================================")
print("  Verification Summary")
print("============================================")
print(f"PASS: {len(passes)}")
print(f"WARN: {len(warnings)}")
print(f"FAIL: {len(failures)}")

if warnings:
    print("")
    print("Warnings:")
    for warning in warnings:
        print(f"  - {warning}")

if failures:
    print("")
    print("Failures:")
    for failure in failures:
        print(f"  - {failure}")
    print("")
    print("RESULT: FAILED")
    sys.exit(1)

print("")
print("RESULT: PASSED")
print("The happy path completed successfully.")
PY
