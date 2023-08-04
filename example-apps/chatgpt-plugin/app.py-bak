"""
Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
or more contributor license agreements. See the NOTICE file distributed with
this work for additional information regarding copyright
ownership. Elasticsearch B.V. licenses this file to you under
the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""


import json
import requests
import urllib.parse

import quart
import quart_cors
from quart import request

import os
import openai
from elasticsearch import Elasticsearch

app = quart_cors.cors(quart.Quart(__name__), allow_origin="*")

openai.api_key = os.environ['openai_api']
model = "gpt-3.5-turbo-0301"

# Connect to Elastic Cloud cluster
def es_connect(cid, user, passwd):
  es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))
  return es

# Search ElasticSearch index and return body and URL of the result
def ESSearch(query_text):
  cid = os.environ['cloud_id']
  cp = os.environ['cloud_pass']
  cu = os.environ['cloud_user']
  es = es_connect(cid, cu, cp)

  # Elasticsearch query (BM25) and kNN configuration for hybrid search
  query = {
    "bool": {
      "must": [{
        "match": {
          "title": {
            "query": query_text,
            "boost": 1
          }
        }
      }],
      "filter": [{
        "exists": {
          "field": "title-vector"
        }
      }]
    }
  }

  knn = {
    "field": "title-vector",
    "k": 1,
    "num_candidates": 20,
    "query_vector_builder": {
      "text_embedding": {
        "model_id": "sentence-transformers__all-distilroberta-v1",
        "model_text": query_text
      }
    },
    "boost": 24
  }

  fields = ["title", "body_content", "url"]
  index = 'search-elastic-docs'
  resp = es.search(index=index,
                   query=query,
                   knn=knn,
                   fields=fields,
                   size=1,
                   source=False)

  body = resp['hits']['hits'][0]['fields']['body_content'][0]
  url = resp['hits']['hits'][0]['fields']['url'][0]

  return body, url


def truncate_text(text, max_tokens):
  tokens = text.split()
  if len(tokens) <= max_tokens:
    return text

  return ' '.join(tokens[:max_tokens])


# Generate a response from ChatGPT based on the given prompt
def chat_gpt(prompt,
             model="gpt-3.5-turbo",
             max_tokens=1024,
             max_context_tokens=4000,
             safety_margin=5):
  # Truncate the prompt content to fit within the model's context length
  truncated_prompt = truncate_text(
    prompt, max_context_tokens - max_tokens - safety_margin)

  response = openai.ChatCompletion.create(model=model,
                                          messages=[{
                                            "role":
                                            "system",
                                            "content":
                                            "You are a helpful assistant."
                                          }, {
                                            "role": "user",
                                            "content": truncated_prompt
                                          }])

  return response["choices"][0]["message"]["content"]


@app.get("/search")
async def search():
  query = request.args.get("query")
  resp, url = ESSearch(query)
  return quart.Response(response=resp + '\n\n' + resp)


@app.get("/logo.png")
async def plugin_logo():
  filename = 'logo.png'
  return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
  host = request.headers['Host']
  with open("./.well-known/ai-plugin.json") as f:
    text = f.read()
    text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
  host = request.headers['Host']
  with open("openapi.yaml") as f:
    text = f.read()
    text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return quart.Response(text, mimetype="text/yaml")


def main():
  port = int(os.environ.get("PORT", 5001))
  app.run(debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
  main()
