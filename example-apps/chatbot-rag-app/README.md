# Elastic Chatbot RAG App

This is a sample app that combines Elasticsearch, Langchain and a number of different LLMs to create a chatbot experience with ELSER with your own private data.

![Screenshot of the sample app](./app-demo.gif)

## 1. Download the Project

Download the project from Github and extract the `chatbot-rag-app` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/chatbot-rag-app
```

## 2. Installing and connecting to Elasticsearch

### Install Elasticsearch

There are a number of ways to install Elasticsearch. Cloud is best for most use-cases. Visit the [Install Elasticsearch](https://www.elastic.co/search-labs/tutorials/install-elasticsearch) for more information.

### Connect to Elasticsearch

This app requires the following environment variables to be set to connect to Elasticsearch

### Elastic Cloud

To connect to Elasticsearch on Elastic Cloud, you will need to set the following environment variables:

```sh
export ELASTIC_CLOUD_ID=...
export ELASTIC_API_KEY=...
```

You can read more on how to get the Cloud ID and API key [here](https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud).

### Local Elasticsearch

To connect to a local Elasticsearch instance, you will need to set the following environment variables:

```sh
export ELASTICSEARCH_URL=http://localhost:9200
```

You can read more on how to install Elasticsearch locally [here](https://www.elastic.co/search-labs/tutorials/install-elasticsearch/docker).

### Change the Elasticsearch index and chat_history index

By default, the app will use the `workplace-app-docs` index and the chat history index will be `workplace-app-docs-chat-history`. If you want to change these, you can set the following environment variables:

```sh
ES_INDEX=workplace-app-docs
ES_INDEX_CHAT_HISTORY=workplace-app-docs-chat-history
```

## 3. Connecting to LLM

We support three LLM providers: Azure, OpenAI and Bedrock.

To use one of them, you need to set the `LLM_TYPE` environment variable:

```sh
export LLM_TYPE=azure
```

### OpenAI

To use OpenAI LLM, you will need to provide the OpenAI key via `OPENAI_API_KEY` environment variable:

```sh
export LLM_TYPE=openai
export OPENAI_API_KEY=...
```

You can get your OpenAI key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

### Azure OpenAI

If you are using Azure LLM, you will need to set the following environment variables:

```sh
export LLM_TYPE=azure
export OPENAI_VERSION=... # e.g. 2023-05-15
export OPENAI_BASE_URL=...
export OPENAI_API_KEY=...
export OPENAI_ENGINE=... # deployment name in Azure
```

### Bedrock LLM

To use Bedrock LLM you need to set the following environment variables in order to AWS.

```sh
export LLM_TYPE=bedrock
export AWS_ACCESS_KEY=...
export AWS_SECRET_KEY=...
export AWS_REGION=... # e.g. us-east-1
export AWS_MODEL_ID=... # Default is anthropic.claude-v2
```

#### AWS Config

Optionally, you can connect to AWS via the config file in `~/.aws/config` described here:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials

```
[default]
aws_access_key_id=...
aws_secret_access_key=...
region=...
```

### Vertex AI

To use Vertex AI you need to set the following environment variables. More infos [here](https://python.langchain.com/docs/integrations/llms/google_vertex_ai_palm).

```sh
    export LLM_TYPE=vertex
    export VERTEX_PROJECT_ID=<gcp-project-id>
    export VERTEX_REGION=<gcp-region> # Default is us-central1
    export GOOGLE_APPLICATION_CREDENTIALS=<path-json-service-account>
```

## 3. Ingest Data

You can index the sample data from the provided .json files in the `data` folder:

```sh
python data/index-data.py
```

by default, this will index the data into the `workplace-app-docs` index. You can change this by setting the `ES_INDEX` environment variable.

### Indexing your own data

`index-data.py` is a simple script that uses Langchain to index data into Elasticsearch, using the `JSONLoader` and `RecursiveCharacterTextSplitter` to split the large documents into passages. Modify this script to index your own data.

Langchain offers many different ways to index data, if you cant just load it via JSONLoader. See the [Langchain documentation](https://python.langchain.com/docs/modules/data_connection/document_loaders)

Remember to keep the `ES_INDEX` environment variable set to the index you want to index into and to query from.

## Running the App

Once you have indexed data into the Elasticsearch index, there are two ways to run the app: via Docker or locally. Docker is advised for testing & production use. Locally is advised for development.

### Through Docker

Build the Docker image and run it with the following environment variables.

```sh
docker build -f Dockerfile -t chatbot-rag-app .
```

Then run it with the following environment variables. In the example below, we are using OpenAI LLM.

If you're using one of the other LLMs, you will need to set the appropriate environment variables via `-e` flag.

```sh
docker run -p 4000:4000 \
  -e "ELASTIC_CLOUD_ID=<cloud_id>" \
  -e "ELASTIC_USERNAME=elastic" \
  -e "ELASTIC_PASSWORD=<password>" \
  -e "LLM_TYPE=openai" \
  -e "OPENAI_API_KEY=<openai_key>" \
  -d chatbot-rag-app
```

### Locally (for development)

With the environment variables set, you can run the following commands to start the server and frontend.

#### Pre-requisites

- Python 3.8+
- Node 14+

#### Install the dependencies

For Python we recommend using a virtual environment.

_ℹ️ Here's a good [primer](https://realpython.com/python-virtual-environments-a-primer) on virtual environments from Real Python._

```sh
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

```sh
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd frontend && yarn
```

#### Run API and frontend

```sh
# Launch API app
python api/app.py

# In a separate terminal launch frontend app
cd frontend && yarn start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.
