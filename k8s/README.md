# Running your own Elastic Stack with Kubernetes

If you would like to start a local Elastic Stack with Kubernetes, use
[manifest-elastic.yml](manifest-elastic.yml).

This starts Elasticsearch, Kibana and Elastic Distribution of OpenTelemetry
(EDOT) Collector.

Note: If you haven't checked out this repository, all you need is one file:
```bash
wget https://raw.githubusercontent.com/elastic/elasticsearch-labs/refs/heads/main/k8s/k8s-manifest-elastic.yml
```

Before you begin, ensure you have free CPU and memory in your cluster. If you
plan to use ELSER, assume a minimum of 8 cpus and 6GB memory for the containers
in this manifest.

First, start this Elastic Stack in the background:
```bash
kubectl apply -f k8s-manifest-elastic.yml
```

**Note**: For simplicity, this adds an Elastic Stack to the default namespace.
Commands after here are simpler due to this. If you want to choose a different
one, use `kubectl`'s `--namespace` flag!

Next, block until the whole stack is available. First install or changing the
Elastic Stack version can take a long time due to image pulling.
```bash
kubectl wait --for=condition=available --timeout=10m \
  deployment/elasticsearch \
  deployment/kibana \
  deployment/otel-collector
```

Next, forward the kibana port:
```bash
kubectl port-forward service/kibana 5601:5601 &
```

Finally, you can view Kibana at http://localhost:5601/app/home#/

If asked for a username and password, use username: elastic and password: elastic.

Clean up when finished, like this:

```bash
kubectl delete -f k8s-manifest-elastic.yml
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
