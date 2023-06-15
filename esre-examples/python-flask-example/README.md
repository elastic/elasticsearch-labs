## Download the Project

Download the project from Github and extract the python-flask-example folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/esre-examples/python-flask-example
```

## Environment Variables

Requires the following environment variables to be set. This can be done by creating a `.env` file in the `/api` directory of the project.

```
openai_api_key=<your openai api key>
openai_api_type=azure
openai_api_base=<your openai api base url>
openai_api_version=2023-03-15-preview
openai_api_engine=<your openai api engine>
cloud_id=<elasticsearch-cloud-id>
cloud_pass=<elasticsearch-password>
cloud_user=<elasticsearch-user>
```

### Obtaining an Azure OpenAI Key

OpenAI keys are rate limited, so ideally, we aren't using the same OpenAI key as a growing SA team long term. The sa-dev Azure account isn't allowing new keys to be made. So for the short term we are going to use the one here. Please do not EDIT the key.

[Key and endpoint page for SA OpenAI resource](https://portal.azure.com/#@elastic365.onmicrosoft.com/resource/subscriptions/75e1bf24-e436-4b18-a571-2de0b09756a9/resourceGroups/vestal-sa/providers/Microsoft.CognitiveServices/accounts/sa-openai/cskeys)

You'll need the deployment endpoint as well. The SA-openai key looks like this.

```
openai_api_key=XXXXX_THE_KEY_XXXXX
openai_api_base=https://sa-openai.openai.azure.com/
openai_api_type=azure
openai_api_version=2023-03-15-preview
openai_api_engine=gpt-4
```

### Indexing your own data

You can index the data from the provided .json files by following the [README](./example-data/README.md) instructions in the `example-data` folder. At the moment indexing your own data should be possible. The UI will attempt to use the URL in the data file for the HTML link to the source.

## Developing

With the environment variables set, you can run the following commands to start the server and frontend.

### Pre-requisites

- Python 3.8+
- Node 14+

### Install the dependencies

```
cd api && pip3 install -r requirements.txt
cd frontend && yarn
```

### Run API and frontend

```
cd api && python3 app.py

# in a separate terminal

cd frontend && yarn start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.

## Running the Docker container

```
docker build -f Dockerfile -t python-flask-example .
docker run -p 4000:4000 -d python-flask-example
```

## Loading your own data

See the [medicare](./example-data/README.md#loading-custom-data) example in the example-data folder for loding your own data.
