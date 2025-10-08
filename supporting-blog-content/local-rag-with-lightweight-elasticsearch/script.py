import os
import time

import requests
from elasticsearch import Elasticsearch, helpers

ES_URL = "http://localhost:9200"
ES_API_KEY = "your-api-key-here"
INDEX_NAME = "team-data"
OLLAMA_URL = "http://localhost:11434/api/generate"
DATASET_FOLDER = "./Dataset"


es_client = Elasticsearch(ES_URL, api_key=ES_API_KEY)


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


def semantic_search(query, size=3):
    start_time = time.time()
    search_body = {
        "query": {"semantic": {"field": "semantic_field", "query": query}},
        "size": size,
    }

    response = es_client.search(index=INDEX_NAME, body=search_body)
    search_latency = (time.time() - start_time) * 1000  # ms

    return response["hits"]["hits"], search_latency


def query_ollama(prompt, model):
    start_time = time.time()
    data = {"model": model, "prompt": prompt, "stream": False, "think": False}

    response = requests.post(OLLAMA_URL, json=data)

    ollama_latency = (time.time() - start_time) * 1000  # ms

    if response.status_code == 200:
        response_data = response.json()

        eval_count = response_data.get("eval_count", 0)
        eval_duration = response_data.get("eval_duration", 0)
        tokens_per_second = 0

        if eval_count > 0 and eval_duration > 0:
            tokens_per_second = (
                eval_count / eval_duration * 1_000_000_000
            )  # nanoseconds to seconds (eval_count / eval_duration * 10^9)

        return response_data["response"], ollama_latency, tokens_per_second
    else:
        return f"Error: {response.status_code}", ollama_latency, 0


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

    ollama_model = "llama3.2"
    print(f"🤖 Asking to model: {ollama_model}")
    response, ollama_latency, tokens_per_second = query_ollama(prompt, ollama_model)

    print(f"\n💡 Question: {query}\n📝 Answer: {response}")

    print(f"✅ Indexed {success} documents in {bulk_latency:.0f}ms")
    print(f"🔍 Search Latency: {search_latency:.0f}ms")
    print(
        f"🤖 Ollama Latency: {ollama_latency:.0f}ms | {tokens_per_second:.1f} tokens/s"
    )
