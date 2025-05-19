# Trace-Based Testing for Chatbot RAG Application

*The instructions and tests below have been used with models hosted by OpenAI.
We plan to add tests for additional model configurations in the future.*

## Introduction to Trace Testing

Trace testing is a modern approach to testing distributed systems by leveraging the distributed traces that flow through your applications.

Tracetest is an open-source tool that enables you to create, run, and maintain tests using distributed traces with support for OpenTelemetry and observability backends such as Elastic APM. It allows you to:

- Validate the flow of requests through your entire system
- Assert on specific spans within a trace
- Test complex scenarios involving multiple services

For more information about Tracetest, visit the [official documentation](https://docs.tracetest.io/).

## Setup

Our setup uses Docker to create a testing environment that includes:

1. A Tracetest server for executing and managing tests
2. An OpenTelemetry collector for processing and routing telemetry data
3. Tracetest test running that uses Tracetest CLI to communicate with Tracetest server and execute tests based on the specified configuration.
4. Optionally, you can also setup the Elastic Stack and the chatbot-rag-app itself if you don't have them running in your environment.

## Environment Configuration

The test environment expects the Elastic Stack and chatbot-rag-app to run locally. If you already have these services running, you're ready to execute the tests and skip to the next section.

If you are starting without from scratch, you will need to set up the necessary environment variables for the chatbot-rag-app. For this you can follow setup the instructions in [the applications's directory](../../README.md#make-your-env-file) or copy our example to `.env` file in `example-apps/chatbot-rag-app`:

```bash
# Location of the application routes
FLASK_APP=api/app.py
# Ensure print statements appear as they happen
PYTHONUNBUFFERED=1

# How you connect to Elasticsearch: change details to your instance
ELASTICSEARCH_URL=http://localhost:9200
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
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
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

   If you already have Elastic stack and chatbot-rag-app running locally, you use the `--skip-stack-setup` and only spin up test resources.

   ```bash
    ./run-tests.sh --skip-stack-setup
   ```

   To automatically clean up resources after the tests complete (or if they fail), you can use the --with-cleanup flag:

   ```bash
    ./run-tests.sh --with-cleanup
   ```

The script performs the following operations:

- Sets up the Tracetest server
- If not using `--skip-stack-setup`:
  - Starts the Elastic stack (Elasticsearch and Kibana)
  - Builds and starts the chatbot-rag-app
- Configures the OpenTelemetry Collector to send data to Tracetest
- Executes the trace tests defined in `resources/openai-chatbot-test.yaml`
- If `--with-cleanup` is provided, automatically cleans up all resources when the script exits

The example test sends a question about working from home policy to the LLM via API and validates several aspects of the application:

- Successful interraction with the LLM (in the initial setup, a `gpt-4o-mini` via OpenAI API)
- Proper search operations in Elasticsearch for RAG functionality
- Correct updating of chat history
