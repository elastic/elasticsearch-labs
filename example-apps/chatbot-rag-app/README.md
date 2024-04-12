# Elastic Chatbot RAG App

This is a sample app that combines Elasticsearch, Langchain and a number of different LLMs to create a chatbot experience with ELSER with your own private data.

**Requires at least 8.11.0 of Elasticsearch.**

![Screenshot of the sample app](./app-demo.gif)

## Download the Project

Download the project from Github and extract the `chatbot-rag-app` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/chatbot-rag-app
```

## Installing and connecting to Elasticsearch

### Install Elasticsearch

There are a number of ways to install Elasticsearch. Cloud is best for most use-cases. Visit the [Install Elasticsearch](https://www.elastic.co/search-labs/tutorials/install-elasticsearch) for more information.

### Connect to Elasticsearch

This app requires the following environment variables to be set to connect to Elasticsearch hosted on Elastic Cloud:

```sh
export ELASTIC_CLOUD_ID=...
export ELASTIC_API_KEY=...
```

You can add these to a `.env` file for convenience. See the `env.example` file for a .env file template.

#### Self-Hosted Elasticsearch

You can also connect to a self-hosted Elasticsearch instance. To do so, you will need to set the following environment variables:

```sh
export ELASTICSEARCH_URL=...
```

### Change the Elasticsearch index and chat_history index

By default, the app will use the `workplace-app-docs` index and the chat history index will be `workplace-app-docs-chat-history`. If you want to change these, you can set the following environment variables:

```sh
ES_INDEX=workplace-app-docs
ES_INDEX_CHAT_HISTORY=workplace-app-docs-chat-history
```

## Connecting to LLM

We support several LLM providers. To use one of them, you need to set the `LLM_TYPE` environment variable. For example:

```sh
export LLM_TYPE=azure
```

The following sub-sections define the configuration requirements of each supported LLM.

### OpenAI

To use OpenAI LLM, you will need to provide the OpenAI key via `OPENAI_API_KEY` environment variable:

```sh
export LLM_TYPE=openai
export OPENAI_API_KEY=...
```

You can get your OpenAI key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

### Azure OpenAI

If you want to use Azure LLM, you will need to set the following environment variables:

```sh
export LLM_TYPE=azure
export OPENAI_VERSION=... # e.g. 2023-05-15
export OPENAI_BASE_URL=...
export OPENAI_API_KEY=...
export OPENAI_ENGINE=... # deployment name in Azure
```

### Bedrock LLM

To use Bedrock LLM you need to set the following environment variables in order to authenticate to AWS.

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

To use Vertex AI you need to set the following environment variables. More information [here](https://python.langchain.com/docs/integrations/llms/google_vertex_ai_palm).

```sh
export LLM_TYPE=vertex
export VERTEX_PROJECT_ID=<gcp-project-id>
export VERTEX_REGION=<gcp-region> # Default is us-central1
export GOOGLE_APPLICATION_CREDENTIALS=<path-json-service-account>
```

### Mistral AI

To use Mistral AI you need to set the following environment variables. The app has been tested with Mistral Large Model deployed through Microsoft Azure. More information [here](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models-mistral).

```
export LLM_TYPE=mistral
export MISTRAL_API_KEY=...
export MISTRAL_API_ENDPOINT=...  # should be of the form https://<endpoint>.<region>.inference.ai.azure.com
export MISTRAL_MODEL=...  # optional
```

### Cohere

To use Cohere you need to set the following environment variables:

```
export LLM_TYPE=cohere
export COHERE_API_KEY=...
export COHERE_MODEL=...  # optional
```

## Running the App

Once you have indexed data into the Elasticsearch index, there are two ways to run the app: via Docker or locally. Docker is advised for testing & production use. Locally is advised for development.

### Through Docker

Build the Docker image and run it with the following environment variables.

```sh
docker build -f Dockerfile -t chatbot-rag-app .
```

#### Ingest data

Make sure you have a `.env` file with all your variables, then run:

```sh
docker run --rm --env-file .env chatbot-rag-app flask create-index
```

See "Ingest data" section under Running Locally for more details about the `flask create-index` command.

#### Run API and frontend

You will need to set the appropriate environment variables in your `.env` file. See the `env.example` file for instructions.

```sh
docker run --rm -p 4000:4000 --env-file .env -d chatbot-rag-app
```

Note that if you are using an LLM that requires an external credentials file (such as Vertex AI), you will need to make this file accessible to the container in the `run` command above. For this you can use a bind mount, or you can also edit the Dockerfile to copy the credentials file to the container image at build time.

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

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd frontend && yarn && cd ..
```

#### Ingest data

You can index the sample data from the provided .json files in the `data` folder:

```sh
flask create-index
```

By default, this will index the data into the `workplace-app-docs` index. You can change this by setting the `ES_INDEX` environment variable.

##### Indexing your own data

The ingesting logic is stored in `data/index-data.py`. This is a simple script that uses Langchain to index data into Elasticsearch, using the `JSONLoader` and `CharacterTextSplitter` to split the large documents into passages. Modify this script to index your own data.

Langchain offers many different ways to index data, if you cant just load it via JSONLoader. See the [Langchain documentation](https://python.langchain.com/docs/modules/data_connection/document_loaders)

Remember to keep the `ES_INDEX` environment variable set to the index you want to index into and to query from.

#### Run API and frontend

```sh
# Launch API app
flask run

# In a separate terminal launch frontend app
cd frontend && yarn start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.
