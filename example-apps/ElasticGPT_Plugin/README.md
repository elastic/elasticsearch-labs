# ElasticGPT plugin

ℹ️ This approach enables use the ChatGPT UI with your own data.
If you want to use your own UI, andor you'd prefer to use the API, see the [ElasticDocs GPT](../ElasticDocs_GPT/README.md) application.

Implement a ChatGPT plugin and extend ChatGPT usage to any content indexed into Elasticsearch:

- Implement a ChatGPT plugin that allows access to Elasticsearch data for context-relevant responses.
- ChatGPT plugins are extensions developed to assist the model in completing its knowledge or executing actions.
- The plugin architecture involves making a call to the `/search` endpoint of the plugin, which sends a search request to Elasticsearch.
- The plugin then returns the document body and URL to ChatGPT, which uses this information to craft its response.
- Deployment of the plugin on Google Cloud Platform (GCP) is demonstrated using Cloud Run.
- Users can install the plugin in ChatGPT and query Elasticsearch data to enhance ChatGPT's knowledge and functionality.

For full details refer to the original Elastic Blog Post:

- [ChatGPT and Elasticsearch: A plugin to use ChatGPT with your Elastic data](https://www.elastic.co/blog/chatgpt-elasticsearch-plugin-elastic-data)
