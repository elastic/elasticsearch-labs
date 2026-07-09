# Implementation guide — APM Service Health Monitor

Full step-by-step deployment of the APM Service Health Monitor agent and its five ES|QL tools. Run tool registrations first, then register the agent.

> **Tested on:** Elasticsearch 9.3 · Kibana 9.3 · Agent Builder (GA)

---

## Prerequisites

- Elasticsearch 9.3 and Kibana 9.3
- Agent Builder enabled in Kibana
- APM data flowing into `traces-*` indices via any Elastic APM agent
- Elastic Enterprise license is required to utilize Agent Builder and ES|QL cross-cluster search

---

## Deployment order

Register tools first so the agent can reference them by ID.

```
Step 1 → apm_dependency_health_tool
Step 2 → apm_error_trend_tool
Step 3 → apm_latency_trend_tool
Step 4 → apm_metrics_overview_tool
Step 5 → apm_throughput_trend_tool
Step 6 → apm_service_health_agent   ← register last

```

---

## Step 1 — Register the dependency health tool

Evaluates the error rate of every external dependency (databases, APIs, caches) called by the service over the last 24 hours.

```http
POST kbn:/api/agent_builder/tools
{
  "id": "apm_dependency_health_tool",
  "type": "esql",
  "description": "Evaluates the health of external dependencies (DBs, APIs, caches) by computing error rates per dependency over the last 24 hours.",
  "tags": ["apm", "dependencies", "health", "external"],
  "configuration": {
    "query": "FROM traces-*\n| WHERE service.name == ?service\n| WHERE processor.event == \"span\" AND span.destination.service.resource IS NOT NULL\n| WHERE @timestamp >= NOW() - 24 hours\n| EVAL is_error = CASE(event.outcome == \"failure\", 1, 0)\n| STATS\n    total_calls  = COUNT(*),\n    failed_calls = SUM(is_error),\n    error_rate   = 100.0 * SUM(is_error)/COUNT(*)\n  BY dependency_name = span.destination.service.resource\n| SORT error_rate DESC\n| LIMIT 100",
    "params": {
      "service": {
        "type": "text",
        "description": "Service name",
        "optional": false
      }
    }
  },
  "readonly": false,
  "schema": {
    "type": "object",
    "properties": {
      "service": { "type": "string", "description": "Service name" }
    },
    "required": ["service"],
    "additionalProperties": false,
    "$schema": "http://json-schema.org/draft-07/schema#"
  }
}

```

**Scoring:** all dependencies ≤ 1% → 🟢 · any > 1% → 🟡 · any > 5% → 🔴

---

## Step 2 — Register the error trend tool

Buckets error rates into 5-minute intervals over 24 hours to expose failure shape — gradual rise vs. sudden spike.

```http
POST kbn:/api/agent_builder/tools
{
  "id": "apm_error_trend_tool",
  "type": "esql",
  "description": "Tracks 5-minute bucketed error rates for the service over 24 hours, showing failure trends and spikes in errors.",
  "tags": ["apm", "trend", "errors", "health"],
  "configuration": {
    "query": "FROM traces-*\n| WHERE service.name == ?service\n| WHERE transaction.type == \"request\"\n| WHERE @timestamp >= NOW() - 24 hours\n| EVAL is_error = CASE(event.outcome == \"failure\", 1, 0)\n| STATS\n    total_requests = COUNT(*),\n    error_count    = SUM(is_error),\n    error_rate     = 100.0 * SUM(is_error)/COUNT(*)\n  BY time_bucket = DATE_TRUNC(5 minutes, @timestamp)\n| SORT time_bucket ASC\n| LIMIT 1000",
    "params": {
      "service": {
        "type": "text",
        "description": "Service name",
        "optional": false
      }
    }
  },
  "readonly": false,
  "schema": {
    "type": "object",
    "properties": {
      "service": { "type": "string", "description": "Service name" }
    },
    "required": ["service"],
    "additionalProperties": false,
    "$schema": "http://json-schema.org/draft-07/schema#"
  }
}

```

**Scoring:** latest bucket error rate < 1% → 🟢 · 1–5% → 🟡 · > 5% → 🔴

---

## Step 3 — Register the latency trend tool

Buckets p95, p75, and average latency into 5-minute intervals over 24 hours. The agent compares the latest bucket against the 24h baseline from the metrics overview tool to detect drift.

```http
POST kbn:/api/agent_builder/tools
{
  "id": "apm_latency_trend_tool",
  "type": "esql",
  "description": "Provides 5-minute bucketed latency trends (avg, p95, p75) for the last 24 hours, enabling visualization of performance patterns over time.",
  "tags": ["apm", "trend", "latency", "performance"],
  "configuration": {
    "query": "FROM traces-*\n| WHERE service.name == ?service\n| WHERE transaction.type == \"request\"\n| WHERE @timestamp >= NOW() - 24 hours\n| STATS\n    avg_latency_ms = AVG(transaction.duration.us / 1000),\n    p95_latency_ms = PERCENTILE(transaction.duration.us / 1000, 95),\n    p75_latency_ms = PERCENTILE(transaction.duration.us / 1000, 75)\n  BY time_bucket = DATE_TRUNC(5 minutes, @timestamp)\n| SORT time_bucket ASC\n| LIMIT 1000",
    "params": {
      "service": {
        "type": "text",
        "description": "Service name",
        "optional": false
      }
    }
  },
  "readonly": false,
  "schema": {
    "type": "object",
    "properties": {
      "service": { "type": "string", "description": "Service name" }
    },
    "required": ["service"],
    "additionalProperties": false,
    "$schema": "http://json-schema.org/draft-07/schema#"
  }
}

```

**Scoring:** latest p95 vs 24h baseline — drift < 10% → 🟢 · 10–30% → 🟡 · > 30% → 🔴

---

## Step 4 — Register the metrics overview tool

Computes the 24-hour aggregate snapshot: avg latency, p95/p99, error rate, and throughput. This is the **baseline anchor** — every trend tool compares its latest reading back to these numbers.

```http
POST kbn:/api/agent_builder/tools
{
  "id": "apm_metrics_overview_tool",
  "type": "esql",
  "description": "Aggregates key service metrics over the last 24 hours, including avg latency, p95/p99 latency, error rate, and throughput. Provides a single snapshot for quick health evaluation.",
  "tags": ["apm", "overview", "metrics", "health"],
  "configuration": {
    "query": "FROM traces-*\n| WHERE service.name == ?service\n| WHERE transaction.type == \"request\"\n| WHERE @timestamp >= NOW() - 24 hours\n| EVAL is_error = CASE(event.outcome == \"failure\", 1, 0)\n| STATS\n    avg_latency_ms  = AVG(transaction.duration.us / 1000),\n    p95_latency_ms  = PERCENTILE(transaction.duration.us / 1000, 95),\n    p99_latency_ms  = PERCENTILE(transaction.duration.us / 1000, 99),\n    error_rate      = 100.0 * SUM(is_error) / COUNT(*),\n    throughput_rps  = COUNT(*) / (24*3600)",
    "params": {
      "service": {
        "type": "text",
        "description": "Service name",
        "optional": false
      }
    }
  },
  "readonly": false,
  "schema": {
    "type": "object",
    "properties": {
      "service": { "type": "string", "description": "Service name" }
    },
    "required": ["service"],
    "additionalProperties": false,
    "$schema": "http://json-schema.org/draft-07/schema#"
  }
}

```

---

## Step 5 — Register the throughput trend tool

Buckets request counts into 5-minute intervals. A significant drop in throughput (silent upstream failure, misconfigured load balancer) is flagged just as quickly as a spike.

```http
POST kbn:/api/agent_builder/tools
{
  "id": "apm_throughput_trend_tool",
  "type": "esql",
  "description": "Provides service throughput trends in 5-minute intervals over 24 hours, measuring request volume over time.",
  "tags": ["apm", "trend", "throughput", "performance"],
  "configuration": {
    "query": "FROM traces-*\n| WHERE service.name == ?service\n| WHERE transaction.type == \"request\"\n| WHERE @timestamp >= NOW() - 24 hours\n| STATS requests_count = COUNT(*)\n  BY time_bucket = DATE_TRUNC(5 minutes, @timestamp)\n| SORT time_bucket ASC\n| LIMIT 1000",
    "params": {
      "service": {
        "type": "text",
        "description": "Service name",
        "optional": false
      }
    }
  },
  "readonly": false,
  "schema": {
    "type": "object",
    "properties": {
      "service": { "type": "string", "description": "Service name" }
    },
    "required": ["service"],
    "additionalProperties": false,
    "$schema": "http://json-schema.org/draft-07/schema#"
  }
}

```

**Scoring:** latest throughput vs 24h baseline — drift < 10% → 🟢 · 10–30% → 🟡 · > 30% → 🔴

---

## Step 6 — Register the agent

Wire all five tool IDs into the agent. The health logic lives in the `instructions` field and can be adjusted from the Agent Builder UI in Kibana without any code changes.

```http
POST kbn:/api/agent_builder/agents
{
  "id": "apm_service_health_agent",
  "type": "chat",
  "name": "APM Service Health Monitor",
  "description": "Provides Red/Yellow/Green health status and trends for services over 24 hours using APM metrics.",
  "labels": ["apm", "health", "service", "monitoring"],
  "avatar_color": "#4CAF50",
  "avatar_symbol": "❤️",
  "configuration": {
    "instructions": "You are the Service Health Agent. Your job is to assess and report the health of a specified service over the last 24 hours.\n\n1. Collect metrics from assigned tools:\n   - apm_metrics_overview_tool → avg latency, p95/p99 latency, error rate, throughput\n   - apm_latency_trend_tool → 5-minute latency trends\n   - apm_error_trend_tool → 5-minute error trends\n   - apm_throughput_trend_tool → 5-minute throughput trends\n   - apm_dependency_health_tool → error rates of DBs, APIs, caches\n\n2. Compute metric states:\n   - Latency (p95): Green if latest p95 differs from 24h p95 by <10% · Yellow 10–30% · Red >30%\n   - Error rate: Green if <1% · Yellow 1–5% · Red >5%\n   - Throughput: Green if drift from 24h baseline <10% · Yellow 10–30% · Red >30%\n   - Dependency health: Green if all ≤1% · Yellow if any >1% · Red if any >5%\n\n3. Overall verdict: any Red → Red · any Yellow (no Red) → Yellow · all Green → Green\n\n4. Present results with a summary table per metric, trend highlights, and actionable recommendations for Yellow/Red metrics.\n\n5. Default time window: last 24 hours. Prompt user if service name is missing.",
    "tools": [
      {
        "tool_ids": [
          "platform.core.search",
          "platform.core.list_indices",
          "platform.core.get_index_mapping",
          "platform.core.get_document_by_id",
          "platform.core.execute_esql",
          "platform.core.generate_esql",
          "apm_dependency_health_tool",
          "apm_error_trend_tool",
          "apm_latency_trend_tool",
          "apm_metrics_overview_tool",
          "apm_throughput_trend_tool"
        ]
      }
    ]
  },
  "readonly": false
}

```

---

## Verify

```http
GET kbn:/api/agent_builder/agents/apm_service_health_agent

```

A `200` response confirms the agent is live. Open it in Kibana and ask:

> **"What is the health of my** `checkout-service` **in the last 24 hours?"**

The agent fans out to all five tools, computes metric states in a single reasoning step, and returns a structured Red/Yellow/Green verdict with root cause and recommendations.

---

## Health scoring reference


| Metric          | Tool                         | Compared against      | 🟢 Green    | 🟡 Yellow    | 🔴 Red      |
| --------------- | ---------------------------- | --------------------- | ----------- | ------------ | ----------- |
| Latency (p95)   | `apm_latency_trend_tool`     | 24h p95 from overview | < 10% drift | 10–30% drift | > 30% drift |
| Error rate      | `apm_error_trend_tool`       | Fixed thresholds      | < 1%        | 1–5%         | > 5%        |
| Throughput      | `apm_throughput_trend_tool`  | 24h RPS from overview | < 10% drift | 10–30% drift | > 30% drift |
| Each dependency | `apm_dependency_health_tool` | Fixed thresholds      | All ≤ 1%    | Any > 1%     | Any > 5%    |


**Overall verdict rule:** the worst individual signal wins.

---

## Notes

- Queries use `traces-*` with cross-cluster wildcard support — one deployment covers multi-cluster environments.
- The `service` parameter means the same agent serves every service in your fleet with no per-service configuration.
- Health thresholds are encoded in the agent's `instructions` field — update them from Kibana without redeploying.

