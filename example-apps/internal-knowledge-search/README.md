# Elastic Internal Knowledge Search App

This is a sample app that demonstrates how to build an internal knowledge search application with document-level security on top of Elasticsearch.

**Requires at least 8.11.0 of Elasticsearch.**


## Download the Project

Download the project from Github and extract the `internal-knowledge-search` folder.

```bash
curl https://codeload.github.com/elastic/elasticsearch-labs/tar.gz/main | \
tar -xz --strip=2 elasticsearch-labs-main/example-apps/internal-knowledge-search
```

## Installing and connecting to Elasticsearch

### Install Elasticsearch

There are a number of ways to install Elasticsearch. Cloud is best for most use-cases. Visit the [Install Elasticsearch](https://www.elastic.co/search-labs/tutorials/install-elasticsearch) for more information.

### Connect to Elasticsearch

This app requires the following environment variables to be set to connect to Elasticsearch:

```sh
export ELASTICSEARCH_URL=...
export ELASTIC_USERNAME=...
export ELASTIC_PASSWORD=...
```

You can add these to a `.env` file for convenience. See the `env.example` file for a .env file template.

You can also set the `ELASTIC_CLOUD_ID` instead of the `ELASTICSEARCH_URL` if you're connecting to a cloud instance and prefer to use the cloud ID.

# Workplace Search Reference App

This application shows you how to build an application using [Elastic Search Applications](https://www.elastic.co/guide/en/enterprise-search/current/search-applications.html) for a Workplace Search use case.
![img.png](img.png)

The application uses the [Search Application Client](https://github.com/elastic/search-application-client). Refer to this [guide](https://www.elastic.co/guide/en/enterprise-search/current/search-applications-search.html) for more information.

## Running the application

### Configuring mappings (subject to change in the near future)

The application uses two mapping files (will be replaced with a corresponding UI in the near future).
One specifies the mapping of the documents in your indices to the rendered search result.
The other one maps a source index to a corresponding logo.

#### Data mapping

The data mappings are located inside [config/documentsToSearchResultMappings.json](app-ui/src/config/documentsToSearchResultMappings.json).
Each entry maps the fields of the documents to the search result UI component for a specific index. The mapping expects `title`, `created`, `previewText`, `fullText`, and `link` as keys.
Specify a field name of the document you want to map for each key.

##### Example:

Content document:

````json
{
  "name": "Document name",
  "_timestamp": "2342345934",
  "summary": "Some summary",
  "fullText": "description",
  "link": "some listing url"
}
````

Mapping:
````json
{
  "search-mongo": {
    "title": "name",
    "created": "_timestamp",
    "previewText": "summary",
    "fullText": "description",
    "link": "listing_url"
  }
}
````

#### Logo mapping
You can specify a logo for each index behind the search application. Place your logo inside [data-source-logos](public/data-source-logos) and configure
your mapping as follows:

````json
{
  "search-index-1": "data-source-logos/some_logo.png",
  "search-index-2": "data-source-logos/some_other_logo.webp"
}
````

### Configuring the search application

To be able to use the index filtering and sorting in the UI you should update the search template of your search application:

`PUT _application/search_application/{YOUR_SEARCH_APPLICATION_NAME}`
````json
{
  "indices": [{YOUR_INDICES_USED_BY_THE_SEARCH_APPLICATION}],
  "template": {
    "script": {
      "lang": "mustache",
      "source": """
        {
          "query": {
            "bool": {
              "must": [
              {{#query}}
              {
                "query_string": {
                  "query": "{{query}}"
                }
              }
              {{/query}}
            ],
            "filter": {
              "terms": {
              "_index": {{#toJson}}indices{{/toJson}}
            }
            }
            }
          },
          "from": {{from}},
          "size": {{size}},
          "sort": {{#toJson}}sort{{/toJson}}
        }
      """,
      "params": {
        "query": "",
        "size": 10,
        "from": 0,
        "sort": [],
        "indices": []
      }
    }
  }
````

### Setting the search app variables

You need to set search application name and search application endpoints to the corresponding values in the UI. You'll get these values when [creating a search application](https://www.elastic.co/guide/en/enterprise-search/current/search-applications.html). Note that for the endpoint you should use just the hostname, so excluding the `/_application/search_application/{application_name}/_search`.

### Disable CORS

By default, Elasticsearch is configured to disallow cross-origin resource requests. To call Elasticsearch from the browser, you will need to [enable CORS on your Elasticsearch deployment](https://www.elastic.co/guide/en/elasticsearch/reference/current/behavioral-analytics-cors.html#behavioral-analytics-cors-enable-cors-elasticsearch).

If you don't feel comfortable enabling CORS on your Elasticsearch deployment, you can set the search endpoint in the UI to `http://localhost:3001/api/search_proxy`. Change the host if you're running the backend elsewhere. This will make the backend act as a proxy for the search calls, which is what you're most likely going to do in production.


### Set up DLS with SPO
1. create a connector in kibana named `search-sharepoint`
2. start connectors-python, if using connector clients
3. enable DLS
4. run an access control sync
5. run a full sync
6. define mappings, as above in this README
7. create search application
8. enable cors: https://www.elastic.co/guide/en/elasticsearch/reference/master/search-application-security.html#search-application-security-cors-elasticsearch

### Change your API host

By default, this app will run on `http://localhost:3000` and the backend on `http://localhost:3001`. If you are running the backend in a different location, set the environment variable `REACT_APP_API_HOST` to wherever you're hosting your backend, plus the `/api` path.


### Run API and frontend

```sh
# Launch API app
flask run

# In a separate terminal launch frontend app
cd app-ui && npm install && npm run start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.
