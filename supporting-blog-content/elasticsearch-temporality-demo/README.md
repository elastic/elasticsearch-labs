# Elasticsearch OTLP JVM Metrics Demo

This demo showcases both delta and cumulative metric temporality support in Elasticsearch.

It runs two instances of the [Renaissance benchmark suite](https://renaissance.dev/) inside
constrained Docker containers to stress the JVM and exports metrics with the vanilla
[OpenTelemetry Java agent](https://opentelemetry.io/docs/zero-code/java/agent/).
One instance is configured to use delta temporality, the other one uses cumulative.
Those metrics are sent directly to the Elasticsearch OTLP endpoint.

## Prerequisites

- Docker and Docker Compose
- An Elasticsearch deployment that accepts OTLP ingest
- An Elasticsearch API key with permissions to ingest data

Helpful docs:

- Elastic OTLP/HTTP ingest endpoint:  
  [https://www.elastic.co/docs/manage-data/data-store/data-streams/tsds-ingest-otlp](https://www.elastic.co/docs/manage-data/data-store/data-streams/tsds-ingest-otlp)
- Elastic API keys:  
  [https://www.elastic.co/docs/deploy-manage/api-keys/elasticsearch-api-keys](https://www.elastic.co/docs/deploy-manage/api-keys/elasticsearch-api-keys)
- OpenTelemetry environment variables:  
  [https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)
- OpenTelemetry Java agent:  
  [https://opentelemetry.io/docs/zero-code/java/agent/](https://opentelemetry.io/docs/zero-code/java/agent/)

## Configuration

The key runtime settings are in `docker-compose.yml` under the `renaissance`
service.

At minimum, set:

- `OTEL_EXPORTER_OTLP_ENDPOINT` to your Elasticsearch OTLP endpoint
  (for example `https://<cluster>/_otlp`)
- `OTEL_EXPORTER_OTLP_HEADERS` with your API key in the format:
  `Authorization=ApiKey <base64-key>`

## Run the demo

From the repository root:

```bash
docker compose up --build
```

The benchmarks will run for an hour or can be manually stopped with `Ctrl+C`, then optionally clean up:

```bash
docker compose down
```