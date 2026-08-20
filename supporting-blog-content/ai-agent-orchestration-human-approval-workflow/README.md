# Long-running AI agents with Elasticsearch Workflows

Code companion for the Elasticsearch Labs blog post: [Agentic workflows in Elasticsearch: pause an AI agent for human approval, resume 72 hours later](https://www.elastic.co/search-labs/blog/ai-agent-orchestration-human-approval-workflow).

## What this builds

A workflow that remediates failed documents in an Elasticsearch failure store using AI agents and human approval gates:

1. An alerting rule detects failures in the failure store and starts the workflow
2. The `failure-analyst` agent diagnoses the root cause and proposes a fix
3. The workflow pauses at Gate 1 for engineer approval (days if needed, zero compute cost)
4. If approved, the `remediation-executor` agent runs the fix automatically as a workflow step
5. Gate 2 shows the agent's report and asks the engineer to confirm the result as resolved or escalated
6. A rejected proposal gets one revision cycle through Gate 1b before the case closes

## Prerequisites

- An Elastic Cloud Serverless project (Elasticsearch/Search type)
- Agent Builder (GA, enabled by default on Search projects)
- Workflows (GA on Elastic Stack 9.4+; enable in Management → Feature Settings on Serverless)
- The following environment variables:

```bash
export ES_URL="https://your-project.es.region.gcp.elastic.cloud:443"
export ES_API_KEY="your-api-key"
export KIBANA_ENDPOINT="https://your-project.kb.region.gcp.elastic.cloud"
```

## Setup

### 1. Run the code locally

```bash
cd supporting-blog-content/ai-agent-orchestration-human-approval-workflow

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install requests python-dotenv
```

Set the connection details for your Elastic project in a `.env` file in this
folder, or export them in your shell. The `.env` file is loaded automatically
by `restore.py`; export the variables in your shell before running the shell
scripts:

```bash
ES_URL="https://your-project.es.region.gcp.elastic.cloud:443"
ES_API_KEY="your-api-key"
KIBANA_ENDPOINT="https://your-project.kb.region.gcp.elastic.cloud"
```

```bash
export ES_URL ES_API_KEY KIBANA_ENDPOINT
```

The scripts in this folder use these variables to connect to Elasticsearch and
Kibana. Continue with the restore step below to load the agents, skills, and
workflow.

### 2. Restore agents, skills, and workflow

```bash
python3 scripts/restore.py
```

This restores the two agents (`failure-analyst`, `remediation-executor`), the two skills (`failure-store-remediation-planner`, `execute-failure-store-fix`), and the workflow — no manual configuration needed.

Expected output:

```
Restoring skills
  created  failure-store-remediation-planner
  created  execute-failure-store-fix
  Skills: created=2, updated=0

Restoring agents
  created  failure-analyst
  created  remediation-executor
  Agents: created=2, updated=0

Restoring workflow
  imported failure_store_remediation

Restore completed successfully
```

Running the script a second time updates existing components without creating duplicates.

### 3. Create the data stream

```bash
./scripts/01-setup-failure-store.sh
```

Creates the `logs-demo-app` data stream with failure store enabled and ingests 3 valid documents.

### 4. Create the alerting rule

In Kibana, go to **Management → Rules → Create rule → Elasticsearch query**:

- Query type: ES|QL
- Query:
  ```sql
  FROM logs-demo-app::failures
  | WHERE @timestamp > NOW() - 5 minutes
  | STATS failure_count = COUNT(*)
  | WHERE failure_count > 0
  ```
- Check every: 1 minute
- Actions: Add action → Workflows → select `failure_store_remediation`
- Run workflow for: **New alerts**
- Action frequency: **Run per alert**
- Save and enable the rule

### 5. Test

Ingest invalid documents to trigger the alert:

```bash
./scripts/02-trigger-test.sh
```

Then watch **Workflows → Executions** for the workflow to start.

## How it works

1. Alert fires → workflow starts → `failure-analyst` reads the failure store and diagnoses the problem
2. **Gate 1**: engineer reviews the diagnosis and approves or rejects
3. If approved: `remediation-executor` runs the `execute-failure-store-fix` skill automatically — no manual steps needed
4. **Gate 2**: workflow shows the agent's full report inline; engineer clicks "Yes, mark as resolved" or "No, escalate"
5. If rejected at Gate 1: `failure-analyst` revises the diagnosis with engineer feedback → **Gate 1b** → same execution path
6. All outcomes are recorded in `remediation-runs` for auditing

### Gate timeouts

Each approval gate has a 72-hour timeout. If no response is submitted before the gate expires, the step fails — it is not treated as a rejection. Independently, the seven-day workflow timeout cancels an execution that has not reached a terminal state by then.

## Scripts

| Script | Purpose |
|--------|---------|
| `01-setup-failure-store.sh` | Creates the data stream and ingests 3 valid documents |
| `02-trigger-test.sh` | Ingests 5 invalid docs with current timestamp to trigger the alerting rule |
| `03-reset-full-test-environment.sh` | Deletes all test resources (preview mode by default; requires `--apply`) |
| `04-verify-happy-path.sh` | Validates the final state after a complete happy-path execution |
| `restore.py` | Restores agents, skills, and workflow from `backup/` |

### Reset and rebuild

```bash
# Preview what will be deleted
./scripts/03-reset-full-test-environment.sh

# Apply the reset
./scripts/03-reset-full-test-environment.sh --apply

# Rebuild
./scripts/01-setup-failure-store.sh
```

### Verify after a test run

```bash
./scripts/04-verify-happy-path.sh
```

Expected output ends with:

```
RESULT: PASSED
The happy path completed successfully.
```

## Files

```
├── README.md
├── workflow/
│   └── failure-store-remediation.yaml        # Complete workflow YAML (v2, automatic execution)
├── scripts/
│   ├── 01-setup-failure-store.sh             # Creates data stream + ingests 3 valid documents
│   ├── 02-trigger-test.sh                    # Ingests bad docs to trigger the alert
│   ├── 03-reset-full-test-environment.sh     # Deletes all test resources
│   ├── 04-verify-happy-path.sh              # Validates final state after happy path
│   └── restore.py                            # Restores agents, skills, and workflow
└── backup/
    ├── save_agents.json                      # Agent configs with tools and skills
    └── save_skills.json                      # Skill definitions including execute-failure-store-fix
```

## Related

- [Blog post: Agentic workflows in Elasticsearch: pause an AI agent for human approval, resume 72 hours later](https://www.elastic.co/search-labs/blog/ai-agent-orchestration-human-approval-workflow)
- [Elasticsearch Workflows documentation](https://www.elastic.co/docs/explore-analyze/workflows)
- [Agent Builder documentation](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder)
- [Failure store documentation](https://www.elastic.co/docs/manage-data/data-store/data-streams/failure-store)
