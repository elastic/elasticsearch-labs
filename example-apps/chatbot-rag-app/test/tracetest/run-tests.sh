#!/bin/bash
set -e

CLEANUP=false
SKIP_STACK_SETUP=false

show_help() {
    cat << EOF
Usage: ./run-tests.sh [OPTIONS]

Run trace tests for the chatbot RAG application using Tracetest.

Options:
  --skip-stack-setup   Assume Elastic stack and chatbot RAG are already running
  --with-cleanup       Clean up resources after test execution
  --help               Display this help message and exit

Examples:
  # Set up complete environment and run tests
  ./run-tests.sh

  # Run tests with existing, local Elastic stack and chatbot RAG
  ./run-tests.sh --skip-stack-setup

  # Set up everything, run tests, and clean up afterward
  ./run-tests.sh --with-cleanup

  # Run tests with existing services and clean up test components afterward
  ./run-tests.sh --skip-stack-setup --with-cleanup
EOF
}

for arg in "$@"; do
  case $arg in
    --with-cleanup)
    CLEANUP=true
    shift
    ;;
    --skip-stack-setup)
    SKIP_STACK_SETUP=true
    shift
    ;;
    --help)
    show_help
    exit 0
    ;;
  esac
done


ELASTIC_STACK_COMPOSE="../../../../docker/docker-compose-elastic.yml"
# Docker compose override that configures the otel-collector to send traces to Tracetest
OTEL_COLLECTOR_OVERRIDE="otel-collector.override.yml"
TRACETEST_COMPOSE="docker-compose.test.yml"
CHATBOT_RAG_COMPOSE="../../docker-compose.yml"

cleanup() {
    echo "Cleaning up resources..."
    
    if [ "$SKIP_STACK_SETUP" = false ]; then
        # Clean up everything if not running in local mode
        echo "Cleaning up chatbot-rag-app..."
        docker compose -f $CHATBOT_RAG_COMPOSE down
        echo "Cleaning up Elastic stack..."
        docker compose -f $ELASTIC_STACK_COMPOSE down
    else
        # If running locally restore otel-collector to pre-test state
        echo "Stopping and removing otel-collector..."
        docker compose \
          -f $ELASTIC_STACK_COMPOSE \
          -f $OTEL_COLLECTOR_OVERRIDE \
          stop otel-collector
        docker compose \
          -f $ELASTIC_STACK_COMPOSE \
          -f $OTEL_COLLECTOR_OVERRIDE \
          rm -f otel-collector
        echo "Restarting otel-collector with original configuration..."
        docker compose \
          -f $ELASTIC_STACK_COMPOSE \
          up -d --wait otel-collector
    fi
    
    # Always clean up Tracetest
    echo "Cleaning up Tracetest..."
    docker compose -f $TRACETEST_COMPOSE down

    echo "Cleanup complete."
}

# Set up cleanup trap if --with-cleanup was provided
if [ "$CLEANUP" = true ]; then
    trap cleanup EXIT
fi

if [ "$SKIP_STACK_SETUP" = false ]; then
    echo "Setting up Elastic stack"
    docker compose \
      -f $ELASTIC_STACK_COMPOSE \
      up -d --wait elasticsearch kibana elasticsearch_settings
fi

echo "Setting up Tracetest server"
docker compose -f $TRACETEST_COMPOSE up --force-recreate -d --wait


echo "Adding Tracetest exporter to otel-collector"
docker compose \
  -f $ELASTIC_STACK_COMPOSE \
  -f $OTEL_COLLECTOR_OVERRIDE \
  up -d --wait --force-recreate otel-collector

if [ "$SKIP_STACK_SETUP" = false ]; then
    echo "Building and starting chatbot-rag-app"
    docker compose -f $CHATBOT_RAG_COMPOSE up --build -d --wait
fi

echo "Executing trace tests"

docker run --rm \
  -v $(pwd)/resources:/resources \
  --add-host=localhost:host-gateway \
  --entrypoint tracetest \
  kubeshop/tracetest:v1.7.1 \
  -s http://localhost:11633 \
  run test --file /resources/openai-chatbot-test.yaml
