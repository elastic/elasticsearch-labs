# Building a Recipe Search with Elasticsearch

This project demonstrates how to implement a semantic search using Elastic's 
ELSER and compare its results with a traditional lexical search. The setup is made practical and efficient by using a cluster created in Elastic Cloud, simplifying the use of ELSER and accelerating development.

> **Tip:** To learn more about Elastic Cloud and how to use it, visit: [https://www.elastic.co/pt/cloud](https://www.elastic.co/pt/cloud)

## Project Objectives

1. **Configure Elasticsearch infrastructure** to support semantic and lexical search indexes.
2. **Data ingestion**: Use Python scripts to populate indexes with grocery product data.
3. **Compare search types**: Perform searches and display the results for comparison.

## Prerequisites

- **Elasticsearch v8.15** (recommended): To support ELSER.
- **Python 3.x**: Required to run the ingestion and search scripts.
- **Python Libraries**: Required libraries are listed in the `requirements.txt` file.

To install the dependencies, use the following command:

```bash
pip install -r requirements.txt
```

## Creating the Indexes
To create the semantic and lexical search indexes, run the following scripts:

### Semantic Index

```bash
python infra.py
```

### Lexical Index
```bash
python infra_lexical_index.py
```

These scripts will automatically configure the indexes in Elasticsearch.

## Data Ingestion
To ingest the recipe data into the indexes, use the commands below:

### Ingest Data into the Semantic Index

```bash
python ingestion.py
```

### Ingest Data into the Lexical Index
```bash
python ingestion_lexical_index.py
```

## Search
To perform searches and obtain results from both the semantic and lexical searches,
run the following command:

```bash
python search.py
```

This script performs searches in both indexes and displays the results in the console,
making it easy to compare the two approaches.

