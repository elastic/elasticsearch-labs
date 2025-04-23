import json
import os
from sys import stdout
import time
from halo import Halo
from warnings import warn

from elasticsearch import (
    ApiError,
    Elasticsearch,
    NotFoundError,
    BadRequestError,
)
from elastic_transport._exceptions import ConnectionTimeout

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_elasticsearch import ElasticsearchStore

# Global variables
# Modify these if you want to use a different file, index or model
INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
FILE = os.getenv("FILE", f"{os.path.dirname(__file__)}/data.json")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2")

if ELASTICSEARCH_USER:
    es = Elasticsearch(
        hosts=[ELASTICSEARCH_URL],
        basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    )
elif ELASTICSEARCH_API_KEY:
    es = Elasticsearch(hosts=[ELASTICSEARCH_URL], api_key=ELASTICSEARCH_API_KEY)
else:
    raise ValueError(
        "Please provide either ELASTICSEARCH_USER or ELASTICSEARCH_API_KEY"
    )


def install_elser():
    # This script is re-entered on ctrl-c or someone just running it twice.
    # Hence, both steps need to be careful about being potentially redundant.

    # Step 1: Ensure ELSER_MODEL is defined
    try:
        es.ml.get_trained_models(model_id=ELSER_MODEL)
    except NotFoundError:
        print(f'"{ELSER_MODEL}" model not available, downloading it now')
        es.ml.put_trained_model(
            model_id=ELSER_MODEL, input={"field_names": ["text_field"]}
        )

    while True:
        status = es.ml.get_trained_models(
            model_id=ELSER_MODEL, include="definition_status"
        )
        if status["trained_model_configs"][0]["fully_defined"]:
            break
        time.sleep(1)

    # Step 2: Ensure ELSER_MODEL is fully allocated
    if not is_elser_fully_allocated():
        try:
            es.ml.start_trained_model_deployment(
                model_id=ELSER_MODEL, wait_for="fully_allocated"
            )
            print(f'"{ELSER_MODEL}" model is deployed')
        except BadRequestError:
            # Already started, and likely fully allocated
            pass

    print(f'"{ELSER_MODEL}" model is ready')


def is_elser_fully_allocated():
    stats = es.ml.get_trained_models_stats(model_id=ELSER_MODEL)
    deployment_stats = stats["trained_model_stats"][0].get("deployment_stats", {})
    allocation_status = deployment_stats.get("allocation_status", {})
    return allocation_status.get("state") == "fully_allocated"


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

    print(f"Creating Elasticsearch sparse vector store for {ELASTICSEARCH_URL}")

    store = ElasticsearchStore(
        es_connection=es,
        index_name=INDEX,
        strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=ELSER_MODEL),
    )

    # The first call creates ML tasks to support the index, and typically fails
    # with the default 10-second timeout, at least when Elasticsearch is a
    # container running on Apple Silicon.
    #
    # Once elastic/elasticsearch#107077 is fixed, we can use bulk_kwargs to
    # adjust the timeout.

    print(f"Adding documents to index {INDEX}")

    if stdout.isatty():
        spinner = Halo(text="Processing bulk operation", spinner="dots")
        spinner.start()

    try:
        es.indices.delete(index=INDEX, ignore_unavailable=True)
        store.add_documents(list(docs))
    except BadRequestError:
        # This error means the index already exists
        pass
    except (ConnectionTimeout, ApiError) as e:
        if isinstance(e, ApiError) and e.status_code != 408:
            raise
        warn(f"Error occurred, will retry after ML jobs complete: {e}")
        await_ml_tasks()
        es.indices.delete(index=INDEX, ignore_unavailable=True)
        store.add_documents(list(docs))

    if stdout.isatty():
        spinner.stop()

    print(f"Documents added to index {INDEX}")


def await_ml_tasks(max_timeout=1200, interval=5):
    """
    Waits for all machine learning tasks to complete within a specified timeout period.

    Parameters:
        max_timeout (int): Maximum time to wait for tasks to complete, in seconds.
        interval (int): Time to wait between status checks, in seconds.

    Raises:
        TimeoutError: If the timeout is reached and machine learning tasks are still running.
    """
    start_time = time.time()
    ml_tasks = get_ml_tasks()
    if not ml_tasks:
        return  # likely a lost race on tasks

    print(f"Awaiting {len(ml_tasks)} ML tasks")

    while time.time() - start_time < max_timeout:
        ml_tasks = get_ml_tasks()
        if not ml_tasks:
            return
        time.sleep(interval)

    raise TimeoutError(
        f"Timeout reached. ML tasks are still running: {', '.join(ml_tasks)}"
    )


def get_ml_tasks():
    """Return a list of ML task actions from the ES tasks API."""
    tasks = []
    resp = es.tasks.list(detailed=True, actions=["cluster:monitor/xpack/ml/*"])
    for node_info in resp["nodes"].values():
        for task_info in node_info.get("tasks", {}).values():
            tasks.append(task_info["action"])
    return tasks


# Unless we run through flask, we can miss critical settings or telemetry signals.
if __name__ == "__main__":
    raise RuntimeError("Run via the parent directory: 'flask create-index'")
