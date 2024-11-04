from elasticsearch_connection import ElasticsearchConnection

client = ElasticsearchConnection().get_client()


def create_index_embedding():
    response = client.indices.create(
        index="grocery-catalog-elser",
        mappings={
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "text"},
                "description": {"type": "text", "copy_to": "description_embedding"},
                "category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "price": {"type": "float"},
                "unit": {"type": "keyword"},
                "description_embedding": {
                    "type": "semantic_text",
                    "inference_id": "elser_embeddings",
                },
            }
        },
    )
    print(response)


def create_inference():
    response = client.inference.put(
        inference_id="elser_embeddings",
        task_type="sparse_embedding",
        body={
            "service": "elser",
            "service_settings": {"num_allocations": 1, "num_threads": 1},
        },
    )
    print(response)


if __name__ == "__main__":

    create_inference()

    create_index_embedding()
