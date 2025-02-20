from datetime import datetime

from kafka import KafkaProducer
import json
import time
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log_producer")

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],  # Specifies the Kafka server to connect
    value_serializer=lambda x: json.dumps(x).encode(
        "utf-8"
    ),  # Serializes data as JSON and encodes it to UTF-8 before sending
    batch_size=16384,  # Sets the maximum batch size in bytes (here, 16 KB) for buffered messages before sending
    linger_ms=10,  # Sets the maximum delay (in milliseconds) before sending the batch
    acks="all",  # Specifies acknowledgment level; 'all' ensures message durability by waiting for all replicas to acknowledge
)


def generate_log_message():

    diff_seconds = random.uniform(300, 600)
    timestamp = time.time() - diff_seconds

    log_messages = {
        "INFO": [
            "User login successful",
            "Database connection established",
            "Service started",
            "Payment processed",
        ],
        "WARNING": ["Service stopped", "Payment may not have been processed"],
        "ERROR": ["User login failed", "Database connection failed", "Payment failed"],
        "DEBUG": ["Debugging user login flow", "Debugging database connection"],
    }

    level = random.choice(list(log_messages.keys()))

    message = random.choice(log_messages[level])

    log_entry = {"level": level, "message": message, "timestamp": timestamp}

    return log_entry


def send_log_batches(topic, num_batches=5, batch_size=10):
    for i in range(num_batches):
        logger.info(f"Sending batch {i + 1}/{num_batches}")
        for _ in range(batch_size):
            log_message = generate_log_message()
            producer.send(topic, value=log_message)
        producer.flush()
        time.sleep(1)


if __name__ == "__main__":
    topic = "logs"
    send_log_batches(topic)
    producer.close()
