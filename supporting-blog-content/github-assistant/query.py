import asyncio
from llama_index.core import VectorStoreIndex, QueryBundle, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from index import get_es_vector_store
import httpx

embed_model = OpenAIEmbedding(model="text-embedding-3-large")
Settings.embed_model = embed_model

def run_query_sync():
    query = input("Please enter your query: ")

    openai_llm = OpenAI(model="gpt-4o")

    es_vector_store = get_es_vector_store()
    index = VectorStoreIndex.from_vector_store(es_vector_store)

    try:
        query_engine = index.as_query_engine(
            llm=openai_llm,
            similarity_top_k=3,
            streaming=False,
            response_mode="tree_summarize",
        )

        bundle = QueryBundle(query, embedding=embed_model.get_query_embedding(query))

        result = query_engine.query(bundle)
        return result.response
    except Exception as e:
        print(f"An error occurred while running the query: {e}")
    finally:
        if hasattr(openai_llm, "client") and isinstance(
            openai_llm.client, httpx.Client
        ):
            openai_llm.client.close()
        if hasattr(embed_model, "client") and isinstance(
            embed_model.client, httpx.Client
        ):
            embed_model.client.close()
        if hasattr(es_vector_store, "close"):
            es_vector_store.close()
            print("Elasticsearch connection closed.")

if __name__ == "__main__":
    try:
        result = run_query_sync()
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
