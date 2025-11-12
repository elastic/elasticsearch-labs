import os
import time

from elasticsearch import Elasticsearch, helpers
from openai import OpenAI

ES_URL = "http://localhost:9200"
ES_API_KEY = "your-api-key-here"
INDEX_NAME = "team-data"
LOCAL_AI_URL = "http://localhost:8080/v1"  # Local AI server URL
DATASET_FOLDER = "./Dataset"


es_client = Elasticsearch(ES_URL, api_key=ES_API_KEY)
ai_client = OpenAI(base_url=LOCAL_AI_URL, api_key="sk-x")


def build_documents(dataset_folder, index_name):
    for filename in os.listdir(dataset_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(dataset_folder, filename)

            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            yield {
                "_index": index_name,
                "_source": {"file_title": filename, "file_content": content},
            }


def index_documents():
    try:
        start_time = time.time()

        success, _ = helpers.bulk(
            es_client, build_documents(DATASET_FOLDER, INDEX_NAME)
        )

        end_time = time.time()
        bulk_latency = (end_time - start_time) * 1000  # ms

        return success, bulk_latency
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 0, 0


def semantic_search(query, size=3):
    start_time = time.time()
    search_body = {
        "query": {"semantic": {"field": "semantic_field", "query": query}},
        "size": size,
    }

    response = es_client.search(index=INDEX_NAME, body=search_body)
    search_latency = (time.time() - start_time) * 1000  # ms

    return response["hits"]["hits"], search_latency


def query_local_ai(prompt, model):
    start_time = time.time()

    try:
        response = ai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        ai_latency = (time.time() - start_time) * 1000  # ms

        # Extract response text
        response_text = response.choices[0].message.content

        # Calculate tokens per second if usage info is available
        tokens_per_second = 0
        if hasattr(response, "usage") and response.usage:
            total_tokens = response.usage.completion_tokens
            if ai_latency > 0:
                tokens_per_second = (total_tokens / ai_latency) * 1000  # tokens/second

        return response_text, ai_latency, tokens_per_second
    except Exception as e:
        ai_latency = (time.time() - start_time) * 1000

        return f"Error: {str(e)}", ai_latency, 0


if __name__ == "__main__":
    print("📥 Indexing documents...")
    success, bulk_latency = index_documents()

    time.sleep(2)  # Wait for indexing to complete

    query = "Can you summarize the performance issues in the API?"

    print(f"🔍 Search: '{query}'")
    search_results, search_latency = semantic_search(query)

    context = "Information found:\n"
    for hit in search_results:
        source = hit["_source"]
        context += f"File: {source['file_title']}\n"
        context += f"Content: {source['file_content']}\n\n"

    prompt = f"{context}\nQuestion: {query}\nAnswer:"

    ai_model = "dolphin3.0-qwen2.5-0.5b"

    print(f"🤖 Asking to model: {ai_model}")
    response, ai_latency, tokens_per_second = query_local_ai(prompt, ai_model)

    print(f"\n💡 Question: {query}\n📝 Answer: {response}")

    print(f"✅ Indexed {success} documents in {bulk_latency:.0f}ms")
    print(f"🔍 Search Latency: {search_latency:.0f}ms")
    print(f"🤖 AI Latency: {ai_latency:.0f}ms | {tokens_per_second:.1f} tokens/s")
