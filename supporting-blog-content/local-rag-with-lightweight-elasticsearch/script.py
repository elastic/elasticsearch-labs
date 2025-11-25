import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from openai import OpenAI

load_dotenv()

ES_URL = os.getenv("ES_URL", "http://localhost:9200")
ES_API_KEY = os.getenv("ES_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "team-data")
LOCAL_AI_URL = os.getenv("LOCAL_AI_URL", "http://localhost:8080/v1")
DATASET_FOLDER = os.getenv("DATASET_FOLDER", "./Dataset")


es_client = Elasticsearch(ES_URL, api_key=ES_API_KEY)
ai_client = OpenAI(base_url=LOCAL_AI_URL, api_key="sk-x")


def setup_inference_endpoint():
    inference_id = "e5-small-model"
    try:
        es_client.inference.put(
            inference_id=inference_id,
            task_type="text_embedding",
            body={
                "service": "elasticsearch",
                "service_settings": {
                    "num_allocations": 1,
                    "num_threads": 1,
                    "model_id": ".multilingual-e5-small",
                },
            },
        )
        print(f"✅ Inference endpoint '{inference_id}' created successfully")
    except Exception as e:
        print(f"❌ Error creating inference endpoint: {str(e)}")


def setup_inference_endpoint():
    inference_id = "e5-small-model"

    try:
        es_client.inference.get(inference_id=inference_id)
        print(f"✅ Inference endpoint '{inference_id}' already exists")
    except Exception:
        print(f"📦 Creating inference endpoint '{inference_id}'...")

        try:
            es_client.inference.put(
                inference_id=inference_id,
                task_type="text_embedding",
                body={
                    "service": "elasticsearch",
                    "service_settings": {
                        "num_allocations": 1,
                        "num_threads": 1,
                        "model_id": ".multilingual-e5-small",
                    },
                },
            )
            print(f"✅ Inference endpoint '{inference_id}' created successfully")
        except Exception as e:
            print(f"❌ Error creating inference endpoint: {str(e)}")


def setup_index():
    try:
        if es_client.indices.exists(index=INDEX_NAME):
            print(f"✅ Index '{INDEX_NAME}' already exists")

        print(f"📦 Creating index '{INDEX_NAME}'...")
        es_client.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "file_title": {"type": "text", "copy_to": "semantic_field"},
                        "file_content": {"type": "text", "copy_to": "semantic_field"},
                        "semantic_field": {
                            "type": "semantic_text",
                            "inference_id": "e5-small-model",
                        },
                    }
                }
            },
        )
        print(f"✅ Index '{INDEX_NAME}' created successfully")
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")


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
    print("🚀 Setting up infrastructure...")

    # Setup inference endpoint and index
    setup_inference_endpoint()
    setup_index()

    print("\n📥 Indexing documents...")
    success, bulk_latency = index_documents()

    time.sleep(2)  # Wait for indexing to complete

    query = "Can you summarize the performance issues in the API?"

    print(f"🔍 Search: '{query}'")
    search_results, search_latency = semantic_search(query)

    context = ""
    citations = []
    for idx, hit in enumerate(search_results, 1):
        source = hit["_source"]
        context += f"[{idx}] File: {source['file_title']}\n"
        context += f"Content: {source['file_content']}\n\n"
        citations.append(f"[{idx}] {source['file_title']}")

    prompt = f"""Based on the following documents, answer the user's question. 
        You MUST cite your sources using the format [1], [2], etc. when referencing information from the documents.

        Documents:
        {context}

        User Question: {query}

        Answer (remember to include citations [1], [2], etc. when referencing specific information)
    """

    ai_model = "smollm2-1.7b-instruct"

    print(f"🤖 Asking to model: {ai_model}")
    response, ai_latency, tokens_per_second = query_local_ai(prompt, ai_model)

    print(f"\n💡 Question: {query}\n📝 Answer: {response}")
    print("\n📚 Citations:")
    for citation in citations:
        print(f"  {citation}")

    print(f"✅ Indexed {success} documents in {bulk_latency:.0f}ms")
    print(f"🔍 Search Latency: {search_latency:.0f}ms")
    print(f"🤖 AI Latency: {ai_latency:.0f}ms | {tokens_per_second:.1f} tokens/s")
