# Running your own Elastic Stack with Docker

If you would like to start a local Elastic Stack with Docker, use
[docker-compose-elastic.yml](docker-compose-elastic.yml).

This starts Elasticsearch, Kibana and Elastic Distribution of OpenTelemetry
(EDOT) Collector.

Note: If you haven't checked out this repository, all you need is one file:
```bash
wget https://raw.githubusercontent.com/elastic/elasticsearch-labs/refs/heads/main/docker/docker-compose-elastic.yml
```

Before you begin, ensure you have free CPU and memory on your Docker host. If
you plan to use ELSER, assume a minimum of 8 cpus and 6GB memory for the
containers in this compose file.

First, start this Elastic Stack in the background:
```bash
docker compose -f docker-compose-elastic.yml up --force-recreate --wait -d
```

Then, you can view Kibana at http://localhost:5601/app/home#/

If asked for a username and password, use username: elastic and password: elastic.

Clean up when finished, like this:
```bash
docker compose -f docker-compose-elastic.yml down
```

## OpenTelemetry

### Metrics

If your application only sends logs or traces, you can skip this section.

EDOT Collector supports delta, not cumulative metrics. Applications that send
OpenTelemetry metrics using the official OTEL SDK need to export this variable:
```bash
OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta
```

Alternatively, you can use [EDOT language SDKs][edot-sdks] which set this by
default.

---
[edot-sdks]: https://github.com/elastic/opentelemetry?tab=readme-ov-file#edot-sdks--agents
