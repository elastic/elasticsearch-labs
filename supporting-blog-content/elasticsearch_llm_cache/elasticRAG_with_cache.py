import os
import streamlit as st
import openai
from elasticsearch import Elasticsearch
from string import Template
import elasticapm
import time

from elasticsearch_llm_cache import (
    ElasticsearchLLMCache,  # Import the class from the file
)

## Configure OpenAI client
#openai.api_key = os.environ['OPENAI_API_KEY']
#openai.api_base = os.environ['OPENAI_API_BASE']
#openai.default_model = os.environ['OPENAI_API_ENGINE']
#openai.verify_ssl_certs = False

#Below is for Azure OpenAI
openai.api_type = os.environ['OPENAI_API_TYPE']
openai.api_base = os.environ['OPENAI_API_BASE']
openai.api_version = os.environ['OPENAI_API_VERSION']
openai.verify_ssl_certs = False
engine = os.environ['OPENAI_API_ENGINE']


# Configure APM and Elasticsearch clients
@st.cache_resource
def initElastic():
    #os.environ['ELASTIC_APM_SERVICE_NAME'] = "elasticsearch_llm_cache_demo"
    apmclient = elasticapm.Client()
    elasticapm.instrument()

    es = Elasticsearch(
        cloud_id=os.environ['ELASTIC_CLOUD_ID'].strip("="),
        basic_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASSWORD']),
        request_timeout=30
    )

    return apmclient, es

apmclient, es = initElastic()

# Set our data index
index = os.environ['ELASTIC_INDEX_DOCS']

# Run an Elasticsearch query using hybrid RRF scoring of KNN and BM25
@elasticapm.capture_span("knn_search")
def search_knn(query_text, es):
    query = {
        "bool": {
            "must": [{
                "match": {
                    "body_content": {
                        "query": query_text
                    }
                }
            }],
            "filter": [{
              "term": {
                "url_path_dir3": "elasticsearch"
              }
            }]
        }
    }

    knn = [
    {
      "field": "chunk-vector",
      "k": 10,
      "num_candidates": 10,
      "filter": {
        "bool": {
          "filter": [
            {
              "range": {
                "chunklength": {
                  "gte": 0
                }
              }
            },
            {
              "term": {
                "url_path_dir3": "elasticsearch"
              }
            }
          ]
        }
      },
      "query_vector_builder": {
        "text_embedding": {
          "model_id": "sentence-transformers__msmarco-minilm-l-12-v3",
          "model_text": query_text
        }
      }
    }]

    rank = {
       "rrf": {
       }
    }

    fields= [
        "title",
        "url",
        "position",
        "url_path_dir3",
        "body_content"
      ]

    resp = es.search(index=index,
                     query=query,
                     knn=knn,
                     rank=rank,
                     fields=fields,
                     size=10,
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
def genAI(prompt, 
             model="gpt-3.5-turbo", 
             max_tokens=1024, 
             max_context_tokens=4000, 
             safety_margin=5, 
             sys_content=None
            ):
    
    # Truncate the prompt content to fit within the model's context length
    truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)

    response = openai.ChatCompletion.create(engine=engine,
                                            temperature=0,
                                            messages=[{"role": "system", "content": sys_content}, 
                                                      {"role": "user", "content": truncated_prompt}]
                                           )


    # APM: add metadata labels of data we want to capture
    elasticapm.label(model = model)
    elasticapm.label(prompt = prompt)
    elasticapm.label(total_tokens = response["usage"]["total_tokens"])
    elasticapm.label(prompt_tokens = response["usage"]["prompt_tokens"])
    elasticapm.label(response_tokens = response["usage"]["completion_tokens"])
    if 'USER_HASH' in os.environ: elasticapm.label(user = os.environ['USER_HASH'])

    return response["choices"][0]["message"]["content"]

def toLLM(resp, url, usr_prompt, sys_prompt, neg_resp, show_prompt, engine):
    prompt_template = Template(usr_prompt)
    prompt_formatted = prompt_template.substitute(query=query, resp=resp, negResponse=negResponse)
    answer = genAI(prompt_formatted, engine, sys_content=sys_prompt)

    # Display response from LLM
    st.header('Response from LLM')
    st.markdown(answer.strip())

    # We don't need to return a reference URL if it wasn't useful
    if not negResponse in answer:
        st.write(url)

    # Display full prompt if checkbox was selected
    if show_prompt:
        st.divider()
        st.subheader('Full prompt sent to LLM')
        prompt_formatted

    return answer


@elasticapm.capture_span("cache_search")
def cache_query(cache, prompt_text):
    return cache.query(prompt_text=query)

@elasticapm.capture_span("add_to_cache")
def add_to_cache(cache, prompt, response):
    return cache.add(prompt=prompt, response=response)


#sidebar setup
st.sidebar.header("Elasticsearch LLM Cache Info")

### MAIN

# Init Elasticsearch Cache
cache = ElasticsearchLLMCache(es_client=es, 
                              index_name="llm_cache_test", 
                              create_index=False # setting only because of Streamlit behavor
                             )
st.sidebar.markdown(f'_creating Elasticsearch Cache_')

# Only want to attempt to create the index on first run
if "index_created" not in st.session_state:
    st.sidebar.markdown('_running create_index_')
    cache.create_index(768)
    # Set the flag so it doesn't run every time
    st.session_state.index_created = True
else:
    st.sidebar.markdown('_index already created, skipping_')


# Prompt Defaults
prompt_default = """Answer this question: $query
Using only the information from this Elastic Doc: $resp
Format the answer in complete markdown code format
If the answer is not contained in the supplied doc reply '$negResponse' and nothing else"""

system_default = 'You are a helpful assistant.'
neg_default = "I'm unable to answer the question based on the information I have from Elastic Docs."


st.title("Elasticsearch LLM Cache Demo")

with st.form("chat_form"):

    query = st.text_input("Ask the Elastic Documentation a question: ", placeholder='I want to secure my elastic cluster')

    with st.expander("Show Prompt Override Inputs"):
        # Inputs for system and User prompt override
        sys_prompt = st.text_area("create an alernative system prompt", placeholder=system_default, value=system_default)
        usr_prompt = st.text_area("create an alternative user prompt required -> \$query, \$resp, \$negResponse",
                                   placeholder=prompt_default, value=prompt_default )

        # Default Response when criteria are not met
        negResponse = st.text_area("Create an alternative negative response", placeholder = neg_default, value=neg_default)

    show_full_prompt = st.checkbox('Show Full Prompt Sent to LLM')


    col1, col2 = st.columns(2)
    with col1:
        query_button = st.form_submit_button("Run With Cache Check")
    with col2:
        refresh_button = st.form_submit_button("Refresh Cache with new call to LLM")
    
if query_button:
    apmclient.begin_transaction("query")
    elasticapm.label(search_method = "knn")
    elasticapm.label(query = query)

    # Start timing
    start_time = time.time()

    # check the llm cache first
    query_check = cache_query(cache, prompt_text=query)
    
    if query_check:
        st.sidebar.markdown('_cache match, using cached results_')
        st.subheader('Response from Cache')
        st.markdown(query_check['response'][0])
#        st.button('rerun without cache')
    else:
        st.sidebar.markdown('_no cache match, querying es and sending to LLM_')
        resp, url = search_knn(query, es) # run kNN hybrid query
        llmAnswer = toLLM(resp, 
              url, 
              usr_prompt, 
              sys_prompt, 
              negResponse, 
              show_full_prompt, 
              engine
             )

        st.sidebar.markdown('_adding prompt and response to cache_')
        add_to_cache(cache, query, llmAnswer)

    # End timing and print the elapsed time
    elapsed_time = time.time() - start_time
    st.sidebar.markdown(f"_Time taken: {elapsed_time:.2f} seconds_")
    st.markdown(f"_Time taken: {elapsed_time:.2f} seconds_")

    apmclient.end_transaction("query", "success")

if refresh_button:
    apmclient.begin_transaction("refresh_cache")
    st.sidebar.markdown('_refreshing cache_')

    '''
    Cache Refresh idea: set an 'invalidated' flag in the 
    already cached document and then call the LLM
    '''

    elasticapm.label(search_method = "knn")
    elasticapm.label(query = query)

    # Start timing
    start_time = time.time()

    st.sidebar.markdown('_skipping cache check - sending to LLM_')

    resp, url = search_knn(query, es) # run kNN hybrid query
    llmAnswer = toLLM(resp,
          url,
          usr_prompt,
          sys_prompt,
          negResponse,
          show_full_prompt,
          engine
         )

    st.sidebar.markdown('_adding prompt and response to cache_')
    add_to_cache(cache, query, llmAnswer)

    # End timing and print the elapsed time
    elapsed_time = time.time() - start_time
    st.sidebar.markdown(f"_Time taken: {elapsed_time:.2f} seconds_")
    st.markdown(f"_Time taken: {elapsed_time:.2f} seconds_")

    apmclient.end_transaction("query", "success")

    st.sidebar.markdown('_cache refreshed_')
    apmclient.end_transaction("refresh_cache", "success")