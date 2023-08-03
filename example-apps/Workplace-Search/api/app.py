from flask import Flask, request, jsonify, Response, render_template
import flask
import os

import openai
from elasticsearch import Elasticsearch, exceptions
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
import uuid
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


DATABASE = './mem.db'

load_dotenv()


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


# Required Environment Variables
# openai_api - OpenAI API Key
# cloud_id - Elastic Cloud Deployment ID
# cloud_user - Elasticsearch Cluster User
# cloud_pass - Elasticsearch User Password

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

app.secret_key = "CHANGE_ME!!"
CORS(app, support_credentials=True)


@app.route('/')
def index_redir():
    return app.send_static_file('index.html')


elser_index = "search-workplace"
elser_search_fields = ["ml.inference.content_expanded.predicted_value"]
elser_result_fields = ["name", "content", "url", "category", "summary"]
facets_fields = {"category": "category.enum"}

bm25_index = "search-workplace"
bm25_search_fields = ["name", "content"]
bm25_result_fields = ["name", "content", "url", "category", "summary"]

openai_type = os.environ['openai_type']
model = ""
engine = ""

if openai_type == "azure":
    openai.api_key = os.environ['openai_api_key']
    openai.api_type = os.environ['openai_api_type']
    openai.api_base = os.environ['openai_api_base']
    openai.api_version = os.environ['openai_api_version']
    engine = os.environ['openai_api_engine']
else:
    openai.api_key = os.environ['openai_api_key']
    model = os.environ['openai_api_model']

# Retrieve conversation context using conversation_id


def get_conversation(conversation_id):
    if not conversation_id:
        conversation_id = uuid.uuid4()
    es = es_connect()
    try:
        resp = es.get(index="flask_mem", id=conversation_id)
        conversation = resp['_source']
    except exceptions.NotFoundError as e:
        conversation = {"context": [], "queries": []}
        es.index(index="flask_mem", id=conversation_id, document=conversation)

    return conversation_id, conversation

# Save conversation context


def save_conversation(conversation_id, query):
    es = es_connect()
    conversation = es.get(index="flask_mem", id=conversation_id)["_source"]
    conversation["queries"].append(query)
    es.index(index="flask_mem", id=conversation_id, document=conversation)

# Search documents from Elasticsearch


def get_documents(query, filters, combine_queries, past_queries, user):
    if combine_queries is True:
        search_query = query + ','.join(past_queries)
    else:
        search_query = query
    hits, facets = search(search_query, filters, user)
    return hits[:3], facets


def get_filters_dsl(filters):
    response = []
    for f in filters:
        if len(filters[f]) > 0:
            filter = {"terms": {f: filters[f]}}
            response.append(filter)
    return response


def get_facets_dsl():
    response = {}
    for f in facets_fields:
        term = {"terms": {"field": facets_fields[f]}}
        response[f] = term
    return response


def get_text_search_request_body(query, filters, search_fields, result_fields, size=10):
    """
    Generates an ES full text search request.
    """
    filters_dsl = get_filters_dsl(filters)
    return {
        '_source': False,
        'fields': result_fields,
        'size': size,
        'query': {
            "bool": {
                "must": {
                    "multi_match": {
                        "query":  query,
                        "fields": search_fields
                    }
                },                # Add boost for recent contents
                "should": {
                    "distance_feature": {
                        "field": "created_on",
                        "pivot": "40d",
                        "origin": "now",
                        "boost": 5
                    }
                },
                "filter": filters_dsl
            }
        },
        "aggs": {}
    }


def get_text_expansion_request_body(query, filters, search_fields, result_fields, size=10):
    """
    Generates an ES text expansion search request.
    """
    filters_dsl = get_filters_dsl(filters)
    aggs_dsl = get_facets_dsl()
    text_expansions = []
    boost = 1

    for field in search_fields:

        split_field_descriptor = field.split("^")
        if len(split_field_descriptor) == 2:
            boost = split_field_descriptor[1]
            field = split_field_descriptor[0]
        te = {"text_expansion": {}}
        te['text_expansion'][field] = {
            "model_text": query,
            "model_id": ".elser_model_1",
            "boost": boost
        }
        text_expansions.append(te)
    # Add boost for recent contents
    text_expansions.append({
        "distance_feature": {
            "field": "created_on",
            "pivot": "40d",
            "origin": "now",
            "boost": 5
        }
    })
    return {
        '_source': False,
        'fields': result_fields,
        'size': size,
        'query': {
            "bool": {
                "should": text_expansions,
                "filter": filters_dsl
            }
        },
        "aggs": aggs_dsl
    }


def find_id_index(id: int, hits: list):
    """
    Finds the index of an object in `hits` which has _id == `id`.
    """

    for i, v in enumerate(hits):
        if v['_id'] == id:
            return i + 1
    return 0


def rerank_hits(hits: list, other_hits: list, k: int):
    """
    Reranks hits with RRF. `hits` must contain the main list of documents to rerank. Uses the `_id` attribute of the
    documents to find matching ones in `other_hits`, and `k` as the rank constant.
    """

    i = 0
    for hit in hits:
        i += 1
        # Find the matching ordinal of the doc with the same _id in other_hits
        other_hit_index = find_id_index(hit['_id'], other_hits)
        rrf_score = 1 / (k + i)
        if other_hit_index > 0:
            rrf_score += 1 / (k + other_hit_index)
        hit['_rrf_score'] = rrf_score
        hit['_score'] = f'{round(rrf_score, 5)} ({round(1 / (k + i), 5)} + {round(1 / (k + other_hit_index), 5) if other_hit_index > 0 else 0}), KNN #{i}, BM25: #{other_hit_index}'

    hits.sort(key=lambda hit: hit['_rrf_score'], reverse=True)

    return hits


def init_streaming(query, documents):
    es = es_connect()
    streaming_id = uuid.uuid4()
    content = ""
    for hit in documents:
        content += f"Content: {hit['fields']['content'][0]} \nSource: {hit['fields']['name'][0]}\n"
    max_tokens = 1024
    max_context_tokens = 4000
    safety_margin = 5
    prompt = f"{content}\nQuestion: {query}"
    truncated_prompt = truncate_text(
        prompt, max_context_tokens - max_tokens - safety_margin)
    messages = [{"role": "system", "content": "Given the following extracted parts of a long document and a question, create a final answer with references. If you don't know the answer, just say 'The provided documents do not provide enough information to answer the question.'. Don't try to make up an answer. Only when you find an answer, return a 'SOURCES' part at the end of your answer, each document comma seperated, in the following format \n ** SOURCES: <sources> **"}] + [
        {"role": "user", "content": prompt}]

    es.index(index="flask_streaming", id=streaming_id,
             document={"message": messages})
    return streaming_id


@app.route("/api/search", methods=['POST'])
def route_api_search():
    required_params = ['query']
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    for param in required_params:
        if param not in data:
            return jsonify({"msg": f"Missing parameter: {param}"}), 400
    # all required parameters are present, continue with the route logic
    query = data.get("query")
    conversation_id = data.get("conversation_id")
    filters = data.get("filters", {})
    user = data.get("user")
    combine_queries = data.get("combine_queries", True)
    try:
        conversation_id, conversation = get_conversation(conversation_id)
    except Exception as e:
        print(e)
        return "Conversation id not valid", 400
    past_queries = conversation["queries"]
    documents, facets = get_documents(
        query, filters, combine_queries, past_queries, user)
    streaming_id = init_streaming(query, documents)
    save_conversation(conversation_id, query)
    return jsonify(results=list(map(lambda x: x["fields"], documents)), facets=facets, conversation_id=conversation_id, streaming_id=streaming_id), 200


def get_messages(streaming_id):
    es = es_connect()
    resp = es.get(index="flask_streaming", id=streaming_id)
    return resp['_source']["message"]


@app.route('/api/completions', methods=['POST'])
def route_api_stream():
    data = request.get_json()
    streaming_id = data.get('streaming_id')

    def stream():
        messages = get_messages(streaming_id)
        if (openai_type == "azure"):
            completion = completion_with_backoff(
                engine=engine,
                temperature=0.2,
                messages=messages,
                stream=True)
        else:
            completion = completion_with_backoff(
                model=model,
                temperature=0.2,
                messages=messages,
                stream=True)
        for line in completion:
            chunk = line['choices'][0].get('delta', {}).get('content', '')
            if chunk:
                # yield chunk
                yield 'data: %s\n\n' % chunk
        yield 'data: [DONE]\n\n'
    return flask.Response(stream(), mimetype='text/event-stream')

# Connect to Elastic Cloud cluster


def es_connect(user=None):
    cid = os.environ['cloud_id']
    cp = os.environ['cloud_pass']
    cu = user if user is not None else os.environ['cloud_user']
    es = Elasticsearch(cloud_id=cid, basic_auth=(cu, cp))
    return es


def print_results(hits):
    for hit in hits:
        print(hit["fields"]["name"])


def extract_facets(results):
    response = []
    for r in results:
        term = {"name": r, "entries": list(map(
            lambda x: {"value": x["key"], "count": x["doc_count"]}, results[r]["buckets"]))}
        response.append(term)
    return response


def search(query, filters, user):
    filters["rolePermissions"] = [user]

    elser_body = get_text_expansion_request_body(
        query, filters, elser_search_fields, elser_result_fields)
    bm25_body = get_text_search_request_body(
        query, filters, bm25_search_fields, bm25_result_fields)

    elser_results = execute_search(elser_index, elser_body)
    bm25_results = execute_search(bm25_index, bm25_body)
    facets = extract_facets(elser_results["aggregations"])
    reranked_hits = rerank_hits(
        elser_results['hits']['hits'], bm25_results['hits']['hits'], 1)
    return reranked_hits[:10], facets


def execute_search(index, body):
    es = es_connect()
    resp = es.search(index=index, query=body["query"], aggregations=body["aggs"],
                     fields=body["fields"], size=body["size"], source=body["_source"])
    return resp


def truncate_text(text, max_tokens):
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    return ' '.join(tokens[:max_tokens])


if __name__ == "__main__":
    app.run(port=4000, debug=True)
