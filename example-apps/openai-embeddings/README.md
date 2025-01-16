# OpenAI embeddings example application

This is a small example Node.js/Express application that demonstrates how to
integrate Elastic and OpenAI.

The application has two components:
* [generate](generate_embeddings.js)
  * Generates embeddings for [sample_data](sample_data/medicare.json) into
    Elasticsearch.
* [app](search_app.js)
  * Runs the web service which hosts the [web frontend](views) and the
    search API.
* Both scripts use the [Elasticsearch](https://github.com/elastic/elasticsearch-js) and [OpenAI](https://github.com/openai/openai-node) JavaScript clients.

![Screenshot of the sample app](./app-demo.png)

## Download the Project

Download the project from Github and extract the `openai-embeddings` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/openai-embeddings
```

## Make your .env file

Copy [env.example](env.example) to `.env` and fill in values noted inside.

## Installing and connecting to Elasticsearch

There are a number of ways to install Elasticsearch. Cloud is best for most
use-cases. Visit the [Install Elasticsearch](https://www.elastic.co/search-labs/tutorials/install-elasticsearch) for more information.

Once you decided your approach, edit your `.env` file accordingly.

### Running your own Elastic Stack with Docker

If you'd like to start Elastic locally, you can use the provided
[docker-compose-elastic.yml](docker-compose-elastic.yml) file. This starts
Elasticsearch, Kibana, and APM Server and only requires Docker installed.

Use docker compose to run Elastic stack in the background:

```bash
docker compose -f docker-compose-elastic.yml up --force-recreate -d
```

Then, you can view Kibana at http://localhost:5601/app/home#/

If asked for a username and password, use username: elastic and password: elastic.

Clean up when finished, like this:

```bash
docker compose -f docker-compose-elastic.yml down
```

## Running the App

There are two ways to run the app: via Docker or locally. Docker is advised for
ease while locally is advised if you are making changes to the application.

### Run with docker

Docker compose is the easiest way, as you get one-step to:
* generate embeddings and store them into Elasticsearch
* run the app, which listens on http://localhost:3000

**Double-check you have a `.env` file with all your variables set first!**

```bash
docker compose up --build --force-recreate
```

Clean up when finished, like this:

```bash
docker compose down
```

### Run locally

First, set up a Node.js environment for the example like this:

```bash
nvm use --lts  # or similar to setup Node.js v20 or later
npm install
```

**Double-check you have a `.env` file with all your variables set first!**

#### Run the generate command

First, ingest the data into elasticsearch:
```bash
npm run generate
```

#### Run the app

Now, run the app, which listens on http://localhost:3000
```bash
npm run app
```

## Advanced

Here are some tips for modifying the code for your use case. For example, you
might want to use your own sample data.

### OpenTelemetry

If you set `OTEL_SDK_DISABLED=false` in your `.env` file, the app will send
logs, metrics and traces to an OpenTelemetry compatible endpoint.

[env.example](env.example) defaults to use Elastic APM server, started by
[docker-compose-elastic.yml](docker-compose-elastic.yml). If you start your
Elastic stack this way, you can access Kibana like this, authenticating with
the username "elastic" and password "elastic":

http://localhost:5601/app/apm/traces?rangeFrom=now-15m&rangeTo=now

Under the scenes, openai-embeddings is automatically instrumented by the Elastic
Distribution of OpenTelemetry (EDOT) Node.js. You can see more details about
EDOT Node.js [here](https://github.com/elastic/elastic-otel-node).

### Using a different source file or document mapping

- Ensure your file contains the documents in JSON format
- Modify the document mappings and fields in the `.js` files and in [views/search.hbs](views/search.hbs)
- Modify the initialization of `FILE` in [utils.js](utils.js)

### Using a different OpenAI model

- Modify `EMBEDDINGS_MODEL` in `.env`
- Ensure that `embedding.dims` in your index mapping is the same number as the dimensions of the model's output.

### Using a different Elastic index

- Modify the initialization of `INDEX` in [utils.js](utils.js)

### Using a different method to connect to Elastic

- Modify the initialization of `elasticsearchClient` in [utils.js](utils.js)
- Refer to [this document](https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/client-connecting.html)
