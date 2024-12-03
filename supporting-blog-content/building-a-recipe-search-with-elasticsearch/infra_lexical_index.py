from elasticsearch_connection import ElasticsearchConnection

client = ElasticsearchConnection().get_client()


def create_index():
    response = client.indices.create(
        index="grocery-catalog",
        mappings={
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "text"},
                "description": {"type": "text", "copy_to": "description_embedding"},
                "category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "price": {"type": "float"},
                "unit": {"type": "keyword"},
            }
        },
    )
    print(response)


if __name__ == "__main__":
    create_index()
