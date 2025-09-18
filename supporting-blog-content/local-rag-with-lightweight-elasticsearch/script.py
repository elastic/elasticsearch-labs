import os
import time

import requests
from elasticsearch import Elasticsearch

ES_URL = "http://localhost:9200"
ES_API_KEY = "your-api-key-here"
INDEX_NAME = "team-data"
OLLAMA_URL = "http://localhost:11434/api/generate"
DATASET_FOLDER = "./Dataset"


es_client = Elasticsearch(ES_URL, api_key=ES_API_KEY)


def index_documents():
    docs_count = 0
    for filename in os.listdir(DATASET_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATASET_FOLDER, filename)

            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            doc = {
                "file_title": filename,
                "file_content": content,
                "semantic_field": f"{filename} {content}",
            }

            start_time = time.time()
            es_client.index(index=INDEX_NAME, document=doc)
            index_latency = (time.time() - start_time) * 1000  # ms

            docs_count += 1
            print(f"✓ {filename} | Latency: {index_latency:.0f}ms")

    return docs_count


def semantic_search(query, size=3):
    start_time = time.time()
    search_body = {
        "query": {"semantic": {"field": "semantic_field", "query": query}},
        "size": size,
    }

    response = es_client.search(index=INDEX_NAME, body=search_body)

    search_latency = (time.time() - start_time) * 1000  # ms
    print(
        f"🔍 Search completed in {search_latency:.0f}ms"
    )  # Print for monitoring purposes

    return response["hits"]["hits"], search_latency


def query_ollama(prompt, model="qwen3:4b"):
    start_time = time.time()
    data = {"model": model, "prompt": prompt, "stream": False}

    response = requests.post(OLLAMA_URL, json=data)

    ollama_latency = (time.time() - start_time) * 1000  # ms

    if response.status_code == 200:
        print(
            f"🤖 Ollama answered in {ollama_latency:.0f}ms"
        )  # Print for monitoring purposes
        return response.json()["response"], ollama_latency
    else:
        return f"Error: {response.status_code}", ollama_latency


if __name__ == "__main__":
    print("📥 Indexing documents...")
    docs_count = index_documents()

    query = "performance issues in the API"

    print(f"\n🔍 Search: '{query}'")
    search_results, search_latency = semantic_search(query)

    context = "Information found:\n"
    for hit in search_results:
        source = hit["_source"]
        context += f"File: {source['file_title']}\n"
        context += f"Content: {source['file_content']}\n\n"

    prompt = f"{context}\nQuestion: {query}\nAnswer:"

    print("🤖 Asking to model...")
    response, ollama_latency = query_ollama(prompt)

    print(f"\n💡 Question: {query}\n📝 Answer: {response}")

    print(f"\n🔍 Search Latency: {search_latency:.0f}ms")
    print(f"🤖 Ollama Latency: {ollama_latency:.0f}ms")
    print(f"📄 Documents Indexed: {docs_count}")
