#!/bin/sh

set -e

TOKEN=$TRACETEST_TOKEN
ENVIRONMENT_ID=$TRACETEST_ENVIRONMENT_ID

run() {
  echo "Configuring Tracetest"
  tracetest configure --server-url http://tracetest:11633

  echo "Running Trace-Based Tests..."
  tracetest run test -f /resources/chatbot-test.yaml
}

run