# Elastic Langchain Sample App

This is a sample app that combines Elasticsearch, Langchain and a number of different LLMs to create a semantic search experience with ELSER.

![Screenshot of the sample app](./app-demo.gif)

## 1. Download the Project

Download the project from Github and extract the `workplace-search` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/workplace-search
```

## 2. Connecting to Elasticsearch

This app requires the following environment variables to be set to connect to Elasticsearch

```sh
export ELASTIC_CLOUD_ID=...
export ELASTIC_USERNAME=...
export ELASTIC_PASSWORD=...
```

Note:

- If you don't have an Elastic Cloud deployment, sign up [here](https://cloud.elastic.co/registration?utm_source=github&utm_content=elasticsearch-labs-samples) for a free trial.

  1. Go to the [Create deployment](https://cloud.elastic.co/deployments/create) page
  2. Select **Create deployment** and follow the instructions

## 3. Connecting to LLM

We support three LLM providers: Azure, OpenAI and Bedrock.

To use one of them, you need to set the `LLM_TYPE` environment variable:

```sh
export LLM_TYPE=azure
# export LLM_TYPE=bedrock
# export LLM_TYPE=openai
```

### OpenAI

`LLM_TYPE=openai`

To use OpenAI LLM, you will need to provide the OpenAI key via `OPENAI_API_KEY` environment variable:

```sh
export OPENAI_API_KEY=...
```

You can get your OpenAI key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

### Azure OpenAI

`LLM_TYPE=azure`

If you are using Azure LLM, you will need to set the following environment variables:

```sh
export OPENAI_VERSION=... # e.g. 2023-05-15
export OPENAI_BASE_URL=...
export OPENAI_API_KEY=...
export OPENAI_ENGINE=... # deployment name in Azure
```

### Bedrock LLM

`LLM_TYPE=bedrock`

To use Bedrock LLM you need to set the following environment variables in order to AWS.

```sh
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

## 3. Ingest Data

You can index the sample data from the provided .json files in the `data` folder:

```sh
python data/index-data.py
```

### Indexing your own data

`index-data.py` is a simple script that uses Langchain to index data into Elasticsearch, using the `JSONLoader` and `CharacterTextSplitter` to split the large documents into passages. Modify this script to index your own data.

Langchain offers many different ways to index data, if you cant just load it via JSONLoader. See the [Langchain documentation](https://python.langchain.com/docs/modules/data_connection/document_loaders)

## Running the app

With the environment variables set, you can run the following commands to start the server and frontend.

### Pre-requisites

- Python 3.8+
- Node 14+

### Install the dependencies

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

### Run API and frontend

```sh
# Launch API app
python api/app.py

# In a separate terminal launch frontend app
cd frontend && yarn start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.

## Running the Docker container

```
docker build -f Dockerfile -t python-flask-example .
docker run -p 4000:4000 -d python-flask-example
```
