import os
from elasticsearch import Elasticsearch
from langchain_core.tools import tool
from deepagents import create_deep_agent

es = Elasticsearch(os.environ["ES_URL"], api_key=os.environ["ES_API_KEY"])

@tool
def esql_query(query: str) -> list[dict] | str:
    """Execute an ES|QL query against Elasticsearch and return the matching rows.

    Args:
        query: A complete ES|QL query string, e.g. 'FROM beir-fiqa | LIMIT 5'.
               Full-text search syntax: WHERE MATCH(field, "value") — not field MATCH "value".
    """
    try:
        resp = es.esql.query(query=query, format="json")
        cols = [c["name"] for c in resp["columns"]]
        return [dict(zip(cols, row)) for row in resp["values"]]
    except Exception as e:
        return f"ES|QL error: {e}"

@tool
def get_mapping(index: str) -> dict:
    """Return the field mapping for an Elasticsearch index or pattern."""
    return es.indices.get_mapping(index=index).body

baseline_agent = create_deep_agent(
    model="openrouter:anthropic/claude-sonnet-4.5",
    tools=[esql_query, get_mapping],
    system_prompt=(
        "You are a research assistant with access to three Elasticsearch indices: "
        "beir-fiqa, beir-nfcorpus, and beir-scifact. "
        "You do NOT know which index is relevant for a given question. "
        "Use get_mapping to inspect an index's description and fields, "
        "then query the most relevant one with esql_query. "
        "Full-text search syntax: WHERE MATCH(field, \"value\") — never use field MATCH \"value\". "
        "Ground your answer strictly in what the queries return."
    ),
)

result = baseline_agent.invoke({
    "messages": [
        {"role": "user",
         "content": "Is there scientific evidence that vitamin D supplementation prevents cancer?"}
    ]
})

from langchain_core.messages import AIMessage
print("\n--- Tool calls ---")
for m in result["messages"]:
    if isinstance(m, AIMessage) and m.tool_calls:
        for tc in m.tool_calls:
            print(f"  [{tc['name']}] {str(tc['args'])[:120]}")
total = sum(len(m.tool_calls) for m in result["messages"] if isinstance(m, AIMessage) and m.tool_calls)
print(f"Total: {total}\n")

print("--- Answer ---")
print(result["messages"][-1].content)
