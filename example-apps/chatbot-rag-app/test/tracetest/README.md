# Trace-Based Testing for Chatbot RAG Application

*The instructions and tests below have been used with models hosted by OpenAI.
We plan to add tests for additional model configurations in the future.*

## Introduction to Trace Testing

Trace testing is a modern approach to testing distributed systems by leveraging the distributed traces that flow through your applications. In a complex system like the Chatbot RAG application, traditional testing approaches may fall short because they can't effectively monitor the interactions between microservices, databases, and external APIs.

Tracetest is an open-source tool that enables you to create, run, and maintain integration tests using distributed traces with support for OpenTelemetry and observability backends such as Elastic APM. It allows you to:

- Validate the flow of requests through your entire system
- Assert on specific spans within a trace
- Test complex scenarios involving multiple services

For more information about Tracetest, visit the [official documentation](https://docs.tracetest.io/).

## Setup

Chatbot RAG application setup uses Docker to create a testing environment that includes:

1. A Tracetest server for executing and managing tests
2. An Elasticsearch cluster for storing traces, logs, and application data
3. An OpenTelemetry collector for processing and routing telemetry data
4. The chatbot RAG application itself

The setup leverages several Docker Compose files to combine the test environment with the local Elastic Stack (from [docker/docker-compose-elastic.yml](../../../../docker/docker-compose-elastic.yml)) and Chatbot RAG application (from [example-apps/chatbot-rag-app/docker-compose.yml](../../docker-compose.yml)). In order to spin up the up-to-date versions of all moving parts, we leverage overrides maintained within this directory. We use:

- `docker-compose.test.yml` - for Tracetest configuration
- `docker-compose.test.override.yml` - Test-specific Tracetest configuration
- `elastic-stack.override.yml` - for test-specific configuration for Elasticsearch and OpenTelemetry Collector
- `chatbot-rag.override.yml` - for configuration of the chatbot application in test mode.

All services are connected through a shared Docker network to enable communication between components.

## Environment Configuration

Before running tests, you need to prepare a `.env.test` file with the necessary environment variables. This file configures the behavior of the chatbot application during testing (same configuration as described in [the applications's directory](../../README.md)).

Create a `.env.test` file in the `test/tracetest` directory with the following content to reproduce the environment we're testing with:

```bash
# Location of the application routes
FLASK_APP=api/app.py
# Ensure print statements appear as they happen
PYTHONUNBUFFERED=1

# How you connect to Elasticsearch: change details to your instance
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=elastic

# The name of the Elasticsearch indexes
ES_INDEX=workplace-app-docs
ES_INDEX_CHAT_HISTORY=workplace-app-docs-chat-history

# OpenAI Configuration
LLM_TYPE=openai
OPENAI_API_KEY=
CHAT_MODEL=gpt-4o-mini

# Set to false to record logs, traces and metrics
OTEL_SDK_DISABLED=false

# Assign the service name that shows up in Kibana
OTEL_SERVICE_NAME=chatbot-rag-app

# OpenTelemetry configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true

# Performance tuning
OTEL_METRIC_EXPORT_INTERVAL=3000
OTEL_BSP_SCHEDULE_DELAY=3000
OTEL_EXPERIMENTAL_RESOURCE_DETECTORS=process_runtime,os,otel,telemetry_distro
```

> Note: Make sure to add your actual OpenAI API key.

## Running the Tests

To run the trace-based tests for the chatbot RAG application, follow these steps:

1. Navigate to the test directory:

   ```bash
   cd example-apps/chatbot-rag-app/test/tracetest
   ```

2. Execute the test script:

   ```bash
    ./run-tests.sh
   ```

   To automatically clean up resources after the tests complete (or if they fail), you can use the --with-cleanup flag:

   ```bash
    ./run-tests.sh --with-cleanup
   ```

The script performs the following operations:

- Creates a shared Docker network for all services
- Sets up the Tracetest server
- Starts the Elastic stack (Elasticsearch and OpenTelemetry Collector)
- Builds and starts the chatbot RAG application
- Executes the trace tests defined in `resources/openai-chatbot-test.yaml`
- If `--with-cleanup` is provided, automatically cleans up all resources when the script exits (normally or due to an error)

The example test sends a question about working from home policy to the LLM via API and validates several aspects of the application:

- Successful interraction with the LLM (in the initial setup, a `gpt-4o-mini` via OpenAI API)
- Proper search operations in Elasticsearch for RAG functionality
- Correct updating of chat history
