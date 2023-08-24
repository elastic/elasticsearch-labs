# Elastic Workplace Sample App

This is a sample app that combines Elasticsearch and OpenAI to create a semantic search experience.

![Screenshot of the sample app](./app-demo.gif)

## 1. Download the Project

Download the project from Github and extract the `workplace-search` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/workplace-search
```

## 2. Index Data

You can index the data from the provided .json files by following the [README](./example-data/README.md) instructions in the `example-data` folder. At the moment indexing your own data should be possible. The UI will attempt to use the URL in the data file for the HTML link to the source.

### Loading your own data

See the [medicare](./example-data/README.md#loading-custom-data) example in the example-data folder for loding your own data.

## 3. Credentials

Requires the following environment variables to be set.

```sh
export ELASTIC_CLOUD_ID=...
export ELASTIC_USERNAME=...
export ELASTIC_PASSWORD=...
export OPENAI_API_KEY=...
```

Note: you can get your OpenAI key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

## Developing

With the environment variables set, you can run the following commands to start the server and frontend.

### Pre-requisites

- Python 3.8+
- Node 14+

### Install the dependencies

```sh
pip install -r requirements.txt
cd frontend && yarn
```

### Run API and frontend

```sh
python api/app.py

# in a separate terminal

cd frontend && yarn start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.

## Running the Docker container

```
docker build -f Dockerfile -t python-flask-example .
docker run -p 4000:4000 -d python-flask-example
```
