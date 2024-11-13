# Data Ingestion  with Apache Kafka and Elasticsearch

This project demonstrates a data ingestion pipeline using **Apache Kafka** and **Elasticsearch** with **Python**. Messages are produced and consumed through Kafka, indexed in Elasticsearch, and visualized in Kibana.

## Project Structure

The infrastructure is managed with **Docker Compose**, which starts the following services:

- **Zookeeper**: Manages and coordinates the Kafka brokers.
- **Kafka**: Responsible for distributing and storing messages.
- **Elasticsearch**: Stores and indexes the messages for analysis.
- **Kibana**: Visualization interface for data stored in Elasticsearch.

The **Producer** code sends messages to Kafka, while the **Consumer** reads and indexes these messages in Elasticsearch.

---

## Prerequisites

- **Docker and Docker Compose**: Ensure you have Docker and Docker Compose installed on your machine.
- **Python 3.x**: To run the Producer and Consumer scripts.

---

## Configure the Producer and Consumer

### Producer
The producer.py sends messages to the logs topic in Kafka in batches.
It uses the batch_size and linger_ms settings to optimize message sending.
````
python producer.py
````

### Consumer
The consumer.py reads messages from the logs topic and indexes them in Elasticsearch. It consumes messages in batches and automatically commits the processing of messages.

````
python consumer.py
````

## Data Verification in Kibana
After running the producer.py and consumer.py scripts, access Kibana at http://localhost:5601 to visualize the indexed data. Messages sent by the producer and processed by the consumer will be in the Elasticsearch index.

