import asyncio
import json

from elasticsearch import helpers

from elasticsearch_connection import ElasticsearchConnection

async_client = ElasticsearchConnection().get_async_client()


def partition_list(lst, chunk_size):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def index_data():
    global partitions
    with open("files/output.json", "r") as file:
        data_json = json.load(file)
    documents = []
    for doc in data_json:
        documents.append(
            {
                "_index": "grocery-catalog-elser",
                "_source": doc,
            }
        )

        partitions = partition_list(documents, 500)

    for i, partition in enumerate(partitions):
        print(f"partition {i + 1}")
        await async_bulk_indexing(async_client, partition)


async def async_bulk_indexing(client, documents):
    success, failed = await helpers.async_bulk(client, documents)
    print(
        f"Successfully indexed {success} documents. Failed to index {failed} documents."
    )


async def main():
    await index_data()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
