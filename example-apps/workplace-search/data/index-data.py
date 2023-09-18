from elasticsearch import Elasticsearch
from langchain.vectorstores import ElasticsearchStore
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import os
load_dotenv()

# Global variables
# Modify these if you want to use a different file, index or model
FILE = f'{os.path.dirname(__file__)}/data.json'
INDEX = 'workplace-app-docs'
ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')

elasticsearch_client = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)

# Metadata extraction function
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["name"] = record.get("name")
    metadata["summary"] = record.get("summary")
    metadata["url"] = record.get("url")
    metadata["category"] = record.get("category")
    metadata["updated_at"] = record.get("updated_at")

    return metadata


if __name__ == "__main__":
    print(f'Loading data from ${FILE}')

    loader = JSONLoader(
        file_path=FILE,
        jq_schema='.[]',
        content_key='content',
        metadata_func=metadata_func
    )
    workplace_docs = loader.load()

    print(f'Loaded {len(workplace_docs)} documents')

    text_splitter = CharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=400
    )

    docs = text_splitter.transform_documents(workplace_docs)

    print(f'Split {len(workplace_docs)} documents into {len(docs)} chunks')

    print(f'Creating Elasticsearch sparse vector store in Elastic Cloud: {ELASTIC_CLOUD_ID}')

    ElasticsearchStore.from_documents(
        docs,
        es_connection=elasticsearch_client,
        index_name=INDEX,
        strategy=ElasticsearchStore.SparseVectorRetrievalStrategy()
    )
