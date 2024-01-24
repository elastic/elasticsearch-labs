import re
from flask import Flask, render_template, request
from search import Search

app = Flask(__name__)
es = Search()


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)

    if parsed_query:
        search_query = {
            'sub_searches': [
                {
                    'query': {
                        'bool': {
                            'must': {
                                'multi_match': {
                                    'query': parsed_query,
                                    'fields': ['name', 'summary', 'content'],
                                }
                            },
                            **filters
                        }
                    }
                },
                {
                    'query': {
                        'bool': {
                            'must': [
                                {
                                    'text_expansion': {
                                        'elser_embedding': {
                                            'model_id': '.elser_model_2',
                                            'model_text': parsed_query,
                                        }
                                    },
                                }
                            ],
                            **filters,
                        }
                    },
                },
            ],
            'rank': {
                'rrf': {}
            },
        }
    else:
        search_query = {
            'query': {
                'bool': {
                    'must': {
                        'match_all': {}
                    },
                    **filters
                }
            }
        }

    results = es.search(
        **search_query,
        aggs={
            'category-agg': {
                'terms': {
                    'field': 'category.keyword',
                }
            },
            'year-agg': {
                'date_histogram': {
                    'field': 'updated_at',
                    'calendar_interval': 'year',
                    'format': 'yyyy',
                },
            },
        },
        size=5,
        from_=from_,
    )
    aggs = {
        'Category': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['category-agg']['buckets']
        },
        'Year': {
            bucket['key_as_string']: bucket['doc_count']
            for bucket in results['aggregations']['year-agg']['buckets']
            if bucket['doc_count'] > 0
        },
    }
    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], aggs=aggs)


@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['name']
    paragraphs = document['_source']['content'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)


@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')


@app.cli.command()
def deploy_elser():
    """Deploy the ELSER v2 model to Elasticsearch."""
    try:
        es.deploy_elser()
    except Exception as exc:
        print(f'Error: {exc}')
    else:
        print(f'ELSER model deployed.')


def extract_filters(query):
    filter_regex = r'category:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m is None:
        return {}, query  # no filters
    filters = {
        'filter': [{
            'term': {
                'category.keyword': {
                    'value': m.group(1)
                }
            }
        }]
    }
    query = re.sub(filter_regex, '', query).strip()
    return filters, query

