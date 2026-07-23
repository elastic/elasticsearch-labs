import os
from elasticsearch import Elasticsearch
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

es = Elasticsearch(os.environ["ES_URL"], api_key=os.environ["ES_API_KEY"])

@tool
def esql_query(query: str) -> list[dict] | str:
    """Execute an ES|QL query against Elasticsearch and return the matching rows.

    Args:
        query: A complete ES|QL query string, e.g. 'FROM ai-index-idx-* | LIMIT 5'.
    """
    try:
        resp = es.esql.query(query=query, format="json")
        cols = [c["name"] for c in resp["columns"]]
        return [dict(zip(cols, row)) for row in resp["values"]]
    except Exception as e:
        return f"ES|QL error: {e}"

# FilesystemBackend loads skills from disk, relative to root_dir.
backend = FilesystemBackend(root_dir=".", virtual_mode=False)

agent = create_deep_agent(
    model=ChatOpenAI(  # any OpenAI-compatible endpoint; configure via LLM_* env vars
        base_url=os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        model=os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-4.5"),
        api_key=os.environ["LLM_API_KEY"],
    ),
    tools=[esql_query],
    skills=["skills"],
    backend=backend,
    system_prompt=(
        "You are a research assistant answering questions about a document corpus. "
        "You have NOT memorized the corpus. When a question depends on specific facts, "
        "names, dates, or events, use the query-ki skill to retrieve Knowledge "
        "Indicators before answering. Ground your answer strictly in what it returns, "
        "and cite the KI titles you used."
    ),
)

result = agent.invoke({
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
