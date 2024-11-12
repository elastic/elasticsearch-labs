import yaml
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

promote_products_free_gluten = ["1043", "1042", "1039"]


def get_client_es():
    with open('../config.yml', 'r') as file:
        config = yaml.safe_load(file)
    return Elasticsearch(
        cloud_id=config['cloud_id'],
        api_key=config['api_key']
    )


def get_text_vector(sentences):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    return embeddings


def build_query(term=None, categories=None, product_types=None, brands=None):
    must_query = [{"match_all": {}}] if not term else [{
        "multi_match": {
            "query": term,
            "fields": ["name", "category", "description"]
        }
    }]

    filters = []
    if categories:
        filters.append({"terms": {"category": categories}})
    if product_types:
        filters.append({"terms": {"product_type": product_types}})
    if brands:
        filters.append({"terms": {"brand.keyword": brands}})

    return {
        "_source": ["id", "brand", "name", "price", "currency", "image_link", "category", "tag_list"],
        "query": {
            "bool": {
                "must": must_query,
                "filter": filters
            }
        }
    }


def build_hybrid_query(term=None, categories=None, product_types=None, brands=None, hybrid=False):
    # Standard query
    organic_query = build_query(term, categories, product_types, brands)

    if hybrid is True and term:

        vector = get_text_vector([term])[0]

        # Hybrid query with RRF (Reciprocal Rank Fusion)
        query = {
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {
                            "standard": {
                                "query": organic_query['query']
                            }
                        },
                        {
                            "knn": {
                                "field": "description_embeddings",
                                "query_vector": vector,
                                "k": 5,
                                "num_candidates": 20,
                                "filter": {
                                    "bool": {
                                        "filter": []
                                    }
                                }
                            }
                        }
                    ],
                    "rank_window_size": 20,
                    "rank_constant": 5
                }
            },
            "_source": organic_query['_source']
        }

        if categories:
            query['retriever']['rrf']['retrievers'][1]['knn']['filter']['bool']['filter'].append({
                "terms": {"category": categories}
            })
        if product_types:
            query['retriever']['rrf']['retrievers'][1]['knn']['filter']['bool']['filter'].append({
                "terms": {"product_type": product_types}
            })
        if brands:
            query['retriever']['rrf']['retrievers'][1]['knn']['filter']['bool']['filter'].append({
                "terms": {"brand.keyword": brands}
            })
    else:
        query = organic_query

    return query


def search_products(term, categories=None, product_types=None, brands=None, promote_products=[], hybrid=False):
    query = build_hybrid_query(term, categories, product_types, brands, hybrid)

    if promote_products and not hybrid:
        query = {
            "query": {
                "pinned": {
                    "ids": promote_products,
                    "organic": query['query']
                }
            },
            "_source": query['_source']
        }

    print(query)
    response = get_client_es().search(index="products-catalog", body=query, size=20)

    results = []
    for hit in response['hits']['hits']:
        print(f"Product Name: {hit['_source']['name']}, Score: {hit['_score']}")

        results.append({
            "id": hit['_source']['id'],
            "brand": hit['_source']['brand'],
            "name": hit['_source']['name'],
            "price": hit['_source']['price'],
            "currency": hit['_source']['currency'] if hit['_source']['currency'] else "USD",
            "image_link": hit['_source']['image_link'],
            "category": hit['_source']['category'],
            "tags": hit['_source'].get('tag_list', [])
        })

    return results


def get_facets_data(term, categories=None, product_types=None, brands=None):
    query = build_query(term, categories, product_types, brands)
    query["aggs"] = {
        "product_types": {"terms": {"field": "product_type"}},
        "categories": {"terms": {"field": "category"}},
        "brands": {"terms": {"field": "brand.keyword"}}
    }
    response = get_client_es().search(index="products-catalog", body=query, size=0)

    return {
        "product_types": [
            {"product_type": bucket['key'], "count": bucket['doc_count']}
            for bucket in response['aggregations']['product_types']['buckets']
        ],
        "categories": [
            {"category": bucket['key'], "count": bucket['doc_count']}
            for bucket in response['aggregations']['categories']['buckets']
        ],
        "brands": [
            {"brand": bucket['key'], "count": bucket['doc_count']}
            for bucket in response['aggregations']['brands']['buckets']
        ]
    }


@app.route('/api/products/search', methods=['GET'])
def search():
    query = request.args.get('query')
    categories = request.args.getlist('selectedCategories[]')
    product_types = request.args.getlist('selectedProductTypes[]')
    brands = request.args.getlist('selectedBrands[]')
    hybrid = request.args.get('hybrid', 'False').lower() == 'true'
    results = search_products(query, categories=categories, product_types=product_types,
                              brands=brands,
                              promote_products=promote_products_free_gluten,
                              hybrid=hybrid)
    return jsonify(results)


@app.route('/api/products/facets', methods=['GET'])
def facets():
    query = request.args.get('query')
    categories = request.args.getlist('selectedCategories[]')
    product_types = request.args.getlist('selectedProductTypes[]')
    brands = request.args.getlist('selectedBrands[]')
    results = get_facets_data(query, categories=categories,
                              product_types=product_types,
                              brands=brands)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
