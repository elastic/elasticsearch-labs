import os
from elasticsearch import Elasticsearch
from langchain_core.tools import tool
from deepagents import create_deep_agent

es = Elasticsearch(os.environ["ES_URL"], api_key=os.environ["ES_API_KEY"])

@tool
def esql_query(query: str) -> list[dict] | str:
    """Execute an ES|QL query against Elasticsearch and return the matching rows.

    Args:
        query: A complete ES|QL query string, e.g. 'FROM browsecomp-plus | LIMIT 5'.
               Full-text search syntax: MATCH(field, "value") — not field MATCH "value".
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
    model="openrouter:anthropic/claude-sonnet-4.5",   # same model as the KI agent
    tools=[esql_query, get_mapping],                  # no query-ki skill
    system_prompt=(
        "You are a research assistant answering questions about a document corpus "
        "stored in the Elasticsearch index `browsecomp-plus` (fields: docid, url, "
        "title, text). You have NOT memorized the corpus. Answer by querying the raw "
        "index directly with ES|QL via the esql_query tool. "
        "Full-text search syntax: WHERE MATCH(field, \"value\") — never use field MATCH \"value\". "
        "Use get_mapping if you are unsure of field names. Ground your answer strictly "
        "in the rows returned, and cite the docid or url you used."
    ),
)

result = baseline_agent.invoke({
    "messages": [
        {"role": "user",
         "content": "What was the actress who played Torvi from Vikings also known for?"}
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
