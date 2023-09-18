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
export OPENAI_API_KEY=...
```

Note:

- If you don't have an Elastic Cloud deployment, sign up [here](https://cloud.elastic.co/registration?utm_source=github&utm_content=elasticsearch-labs-samples) for a free trial.

  1. Go to the [Create deployment](https://cloud.elastic.co/deployments/create) page
  2. Select **Create deployment** and follow the instructions

- you can get your OpenAI key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

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
