from elasticsearch import Elasticsearch, NotFoundError
from langchain_elasticsearch import ElasticsearchStore
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import json
import os
import time

load_dotenv()

# Global variables
# Modify these if you want to use a different file, index or model
INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
FILE = os.getenv("FILE", f"{os.path.dirname(__file__)}/data.json")
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2")

if ELASTICSEARCH_URL:
    elasticsearch_client = Elasticsearch(
        hosts=[ELASTICSEARCH_URL],
    )
elif ELASTIC_CLOUD_ID:
    elasticsearch_client = Elasticsearch(
        cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY
    )
else:
    raise ValueError(
        "Please provide either ELASTICSEARCH_URL or ELASTIC_CLOUD_ID and ELASTIC_API_KEY"
    )


def install_elser():
    try:
        elasticsearch_client.ml.get_trained_models(model_id=ELSER_MODEL)
        print(f'"{ELSER_MODEL}" model is available')
    except NotFoundError:
        print(f'"{ELSER_MODEL}" model not available, downloading it now')
        elasticsearch_client.ml.put_trained_model(
            model_id=ELSER_MODEL, input={"field_names": ["text_field"]}
        )
        while True:
            status = elasticsearch_client.ml.get_trained_models(
                model_id=ELSER_MODEL, include="definition_status"
            )
            if status["trained_model_configs"][0]["fully_defined"]:
                # model is ready
                break
            time.sleep(1)

        print("Model downloaded, starting deployment")
        elasticsearch_client.ml.start_trained_model_deployment(
            model_id=ELSER_MODEL, wait_for="fully_allocated"
        )


def main():
    install_elser()

    print(f"Loading data from ${FILE}")

    metadata_keys = ["name", "summary", "url", "category", "updated_at"]
    workplace_docs = []
    with open(FILE, "rt") as f:
        for doc in json.loads(f.read()):
            workplace_docs.append(
                Document(
                    page_content=doc["content"],
                    metadata={k: doc.get(k) for k in metadata_keys},
                )
            )

    print(f"Loaded {len(workplace_docs)} documents")

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512, chunk_overlap=256
    )

    docs = text_splitter.transform_documents(workplace_docs)

    print(f"Split {len(workplace_docs)} documents into {len(docs)} chunks")

    print(
        f"Creating Elasticsearch sparse vector store in Elastic Cloud: {ELASTIC_CLOUD_ID}"
    )

    elasticsearch_client.indices.delete(index=INDEX, ignore_unavailable=True)

    ElasticsearchStore.from_documents(
        docs,
        es_connection=elasticsearch_client,
        index_name=INDEX,
        strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=ELSER_MODEL),
        bulk_kwargs={
            "request_timeout": 60,
        },
    )


if __name__ == "__main__":
    main()
