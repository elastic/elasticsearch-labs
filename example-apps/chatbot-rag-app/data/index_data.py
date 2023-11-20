from elasticsearch import Elasticsearch, NotFoundError
from langchain.vectorstores import ElasticsearchStore
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Global variables
# Modify these if you want to use a different file, index or model
FILE = f"{os.path.dirname(__file__)}/data.json"
INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2")

elasticsearch_client = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)


def install_elser():
    try:
        elasticsearch_client.ml.get_trained_models(model_id=ELSER_MODEL)
        print(f"\"{ELSER_MODEL}\" model is available")
    except NotFoundError:
        print(f"\"{ELSER_MODEL}\" model not available, downloading it now")
        elasticsearch_client.ml.put_trained_model(model_id=ELSER_MODEL,
                                                  input={"field_names": ["text_field"]})
        while True:
            status = elasticsearch_client.ml.get_trained_models(model_id=ELSER_MODEL,
                                                                include="definition_status")
            if status["trained_model_configs"][0]["fully_defined"]:
                # model is ready
                break
            time.sleep(1)

        print("Model downloaded, starting deployment")
        elasticsearch_client.ml.start_trained_model_deployment(model_id=ELSER_MODEL,
                                                               wait_for="fully_allocated")


# Metadata extraction function
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["name"] = record.get("name")
    metadata["summary"] = record.get("summary")
    metadata["url"] = record.get("url")
    metadata["category"] = record.get("category")
    metadata["updated_at"] = record.get("updated_at")

    return metadata


def main():
    install_elser()

    print(f"Loading data from ${FILE}")

    loader = JSONLoader(
        file_path=FILE,
        jq_schema=".[]",
        content_key="content",
        metadata_func=metadata_func,
    )
    workplace_docs = loader.load()

    print(f"Loaded {len(workplace_docs)} documents")

    text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=400)

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
    )


if __name__ == "__main__":
    main()
