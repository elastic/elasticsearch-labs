## From five dashboards to one prompt: Elastic Agent Builder's Red/Yellow/Green APM verdict

Ask Elastic's APM Service Health Monitor whether your service is healthy. It fans out to five ES|QL queries over your existing `traces-*` data and answers **Red, Yellow, or Green** with the root cause attached — in one response, without switching dashboards or correlating anything by hand.

Runs on **Elastic Agent Builder**, tested on Elasticsearch and Kibana 9.3. One deployment covers every service in your fleet with no per-service setup.

---

## What it does

Five ES|QL tools score latency, errors, throughput, and dependencies against your 24-hour baseline. The agent compares the results and returns a single health verdict with the root cause identified — so you don't dashboard-hop during an APM incident.

| Signal | How it's scored |
|---|---|
| Latency (p95) | % drift from 24h baseline → < 10% Green · 10–30% Yellow · > 30% Red |
| Error rate | Fixed thresholds → < 1% Green · 1–5% Yellow · > 5% Red |
| Throughput | % drift from 24h baseline → < 10% Green · 10–30% Yellow · > 30% Red |
| Dependencies | Per-resource error rate → all ≤ 1% Green · any > 1% Yellow · any > 5% Red |

**Overall rule:** the worst individual signal wins.

---

## Requirements

- Elasticsearch 9.3 and Kibana 9.3
- Agent Builder enabled in Kibana
- APM data flowing into `traces-*` indices

---

## How to implement

See [`implementation-guide.md`](./implementation-guide.md) for the full step-by-step deployment — all five tool registrations and the agent payload, in execution order.

---

## Authors

- Naga Putta, Consulting Architect
- Stephen Brown, Distinguished Customer Engineering Specialist

**Tags:** Observability · APM · Agent Builder · Elasticsearch  

