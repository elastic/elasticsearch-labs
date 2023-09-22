# Elastic Workplace Sample App

This is a sample app that combines Elasticsearch and OpenAI to create a semantic search experience.

![Screenshot of the sample app](./app-demo.gif)

## 1. Download the Project

Download the project from Github and extract the `workplace-search` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/workplace-search
```

## 2. Credentials

This app requires the following environment variables to be set:

```sh
export ELASTIC_CLOUD_ID=...
export ELASTIC_USERNAME=...
export ELASTIC_PASSWORD=...
```

Note:

- If you don't have an Elastic Cloud deployment, sign up [here](https://cloud.elastic.co/registration?utm_source=github&utm_content=elasticsearch-labs-samples) for a free trial.

  1. Go to the [Create deployment](https://cloud.elastic.co/deployments/create) page
  2. Select **Create deployment** and follow the instructions


To use llm other than openai you can set up the LLM_TYPE environment variable to one of the following values:
```sh
# azure|openai|vertex|bedrock
export LLM_TYPE=azure
```

### 2.1. OpenAI LLM

To use OpenAI LLM, you will need to set up only OPENAI_API_KEY environment variable:

```sh
export OPENAI_API_KEY=...
```
You can get your OpenAI key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).
### 2.2. Azure OPENAI LLM

If you are using Azure LLM, you will need to set the following environment variables:

```sh
export OPENAI_VERSION=... # e.g. 2023-05-15
export OPENAI_BASE_URL=...
export OPENAI_API_KEY=...
export OPENAI_ENGINE=... # deployment name in Azure
```

### 2.2. Google Vertex LLM

### 2.3. Bedrock LLM

To use Bedrock LLM first of all you need to install pre-release version of `boto3` and `botocore` packages:
Follow this guide to download and install https://d2eo22ngex1n9g.cloudfront.net/Documentation/BedrockUserGuide.pdf page 21

Then you need to set the following environment variables:
    
```sh
    export AWS_ACCESS_KEY=...
    export AWS_SECRET_KEY=...
    export AWS_REGION=... # e.g. us-east-1
```

## 3. Index Data

You can index the data from the provided .json files in the `data` folder:

```sh
python data/index-data.py
```

## Developing

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
