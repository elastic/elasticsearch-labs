# ElasticDocs GPT

Combine the search power of Elasticsearch with the Question Answering power of GPT.

This application supports the popular Elastic blog [ChatGPT and Elasticsearch: OpenAI meets private data](https://www.elastic.co/blog/chatgpt-elasticsearch-openai-meets-private-data).

ℹ️ This application uses the ChatGPT API with your own UI. If you want to use the ChatGPT UI, see the [ElasticGPT plugin](../ElasticGPT_Plugin/README.md).

## Overview

The following diagram shows the high level architecture of the application:

![diagram](https://raw.githubusercontent.com/jeffvestal/ElasticDocs_GPT/main/images/ElasticChat%20GPT%20Diagram%20-%20No%20line%20text.jpeg)

1. A **Python interface** accepts user questions
   - Generates a hybrid search request for Elasticsearch
   - BM25 match on the `title` field
   - kNN searches on the `title-vector` field
   - Boost `kNN` search results to align scores
   - Set `size=1` to return only the top scored document
2. **Search request** is sent to Elasticsearch
3. **Documentation body and original url** are returned to Python
4. **API call** is made to OpenAI ChatCompletion with the prompt:
   - _"answer this question <question> using only this document <body_content from top search result>"_
5. **Generated response** is returned to Python
6. Python adds **original documentation source url** to generated response and **prints it to the screen** for the user

# Examples
  ![autoscale](https://raw.githubusercontent.com/jeffvestal/ElasticDocs_GPT/main/images/elasticDocs%20GPT%20-%20elastic%20cloud%20autoscaling.png)

  ![apm](https://raw.githubusercontent.com/jeffvestal/ElasticDocs_GPT/main/images/elasticDocs%20GPT%20-%20elastic%20jvm%20apm.png)

  ![inference](https://github.com/jeffvestal/ElasticDocs_GPT/blob/main/images/elasticDocs%20GPT%20-%20inference%20processor.png)

  ![pii](https://raw.githubusercontent.com/jeffvestal/ElasticDocs_GPT/main/images/elasticDocs%20GPT%20-%20redact%20pii.png)