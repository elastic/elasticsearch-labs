import yaml
from elasticsearch import Elasticsearch, AsyncElasticsearch


class ElasticsearchConnection:

    def __init__(self, config_file="config.yml"):
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            self.client = Elasticsearch(
                cloud_id=config["cloud_id"], api_key=config["api_key"]
            )

    def get_client(self):
        return self.client

    def get_async_client(self):
        with open("config.yml", "r") as f:
            config = yaml.safe_load(f)
            self.client = AsyncElasticsearch(
                cloud_id=config["cloud_id"],
                api_key=config["api_key"],
                request_timeout=240,
            )
        return self.client
