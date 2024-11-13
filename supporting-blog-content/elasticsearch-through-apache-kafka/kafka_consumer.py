from kafka import KafkaConsumer
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import json

es = Elasticsearch(["http://localhost:9200"])

consumer = KafkaConsumer(
    "logs",  # Topic name
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="latest",  # Ensures reading from the latest offset if the group has no offset stored
    enable_auto_commit=True,  # Automatically commits the offset after processing
    group_id="log_consumer_group",  # Specifies the consumer group to manage offset tracking
    max_poll_records=10,  # Maximum number of messages per batch
    fetch_max_wait_ms=2000,  # Maximum wait time to form a batch (in ms)
)


def create_bulk_actions(logs):
    for log in logs:
        yield {
            "_index": "logs",
            "_source": {
                "level": log["level"],
                "message": log["message"],
                "timestamp": log["timestamp"],
            },
        }


if __name__ == "__main__":
    try:
        print("Starting message consumption...")
        while True:

            messages = consumer.poll(timeout_ms=1000)

            # process each batch messages
            for _, records in messages.items():
                logs = [json.loads(record.value) for record in records]
                # print(logs)
                bulk_actions = create_bulk_actions(logs)
                response = helpers.bulk(es, bulk_actions)
                print(f"Indexed {response[0]} logs.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        consumer.close()
        print(f"Finish")
