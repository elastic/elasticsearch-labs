#!/bin/bash
set -e

CLEANUP=false
for arg in "$@"; do
  case $arg in
    --with-cleanup)
    CLEANUP=true
    shift
    ;;
  esac
done

NETWORK_NAME="shared-test-network"

ELASTIC_COMPOSE="../../../../docker/docker-compose-elastic.yml"
ELASTIC_STACK_OVERRIDES="elastic-stack.override.yml"

TRACETEST_COMPOSE="docker-compose.test.yml"
TRACETEST_COMPOSE_OVERRIDES="docker-compose.test.override.yml"

CHATBOT_RAG_COMPOSE="../../docker-compose.yml"
CHATBOT_RAG_COMPOSE_OVERRIDES="chatbot-rag.override.yml"

cleanup() {
    echo "Cleaning up resources..."
    docker compose -f $CHATBOT_RAG_COMPOSE -f $CHATBOT_RAG_COMPOSE_OVERRIDES down
    docker compose -f $ELASTIC_COMPOSE -f $ELASTIC_STACK_OVERRIDES down
    docker compose -f $TRACETEST_COMPOSE -f $TRACETEST_COMPOSE_OVERRIDES down
    docker network rm $NETWORK_NAME || true
}

# Set up cleanup trap if --with-cleanup was provided
if [ "$CLEANUP" = true ]; then
    trap cleanup EXIT
fi

# Create the shared network if it doesn't exist
echo "Creating shared Docker network: $NETWORK_NAME"
docker network create $NETWORK_NAME || echo "Shared network already exists"

echo "Setting up Tracetest tracetest server"
docker compose -f $TRACETEST_COMPOSE -f $TRACETEST_COMPOSE_OVERRIDES up --force-recreate -d --wait

echo "Setting up Elastic stack"
docker compose \
  -f $ELASTIC_COMPOSE \
  -f $ELASTIC_STACK_OVERRIDES \
  up -d --wait

echo "Building and starting test environment"
# Rebuilding the chatbot-rag app in order to test locally made changes
docker compose -f $CHATBOT_RAG_COMPOSE -f $CHATBOT_RAG_COMPOSE_OVERRIDES build api-frontend
docker compose -f $CHATBOT_RAG_COMPOSE -f $CHATBOT_RAG_COMPOSE_OVERRIDES up -d --wait

echo "Executing trace tests"

docker run --rm \
  -v $(pwd)/resources:/resources \
  --network=$NETWORK_NAME \
  --entrypoint tracetest \
  kubeshop/tracetest:v1.7.1 \
  -s http://tracetest:11633 \
  run test --file /resources/openai-chatbot-test.yaml
