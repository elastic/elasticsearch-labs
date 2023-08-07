import os
import streamlit as st
import openai
from elasticsearch import Elasticsearch
import elasticapm
from threading import Thread
import time
import asyncio
import random

# This code is part of an Elastic Blog showing how to combine
# Elasticsearch's search relevancy power with 
# OpenAI's GPT's Question Answering power


# Required Environment Variables
# openai_api - OpenAI API Key
# cloud_id - Elastic Cloud Deployment ID
# cloud_user - Elasticsearch Cluster User
# cloud_pass - Elasticsearch User Password

openai.api_key = os.environ['openai_api_key']
openai.api_type = os.environ['openai_api_type']
openai.api_base = os.environ['openai_api_base']
openai.api_version = os.environ['openai_api_version']
openai.verify_ssl_certs = False
engine = os.environ['openai_api_engine']

# Connect to Elastic Cloud cluster
def es_connect(cid, user, passwd):
    print(cid)
    es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))
    return es

# Search ElasticSearch index and return body and URL of the result
def search(query_text, size):
    cid = os.environ['cloud_id']
    cp = os.environ['cloud_pass']
    cu = os.environ['cloud_user']
    es = es_connect(cid, cu, cp)

    # Elasticsearch query (BM25) and kNN configuration for hybrid search
    query = {
        "bool": {
            "should": [{
                "match": {
                    "title": {
                        "query": query_text,
                        "boost": 1,
                         "analyzer": "stop"
                    }
                }
            },
            {
                "match": {
                    "body_content": {
                        "query": query_text,
                        "boost": 2
                    }
                }
            },
            {
                "match": {
                    "product_name.stem": {
                        "query": query_text,
                        "boost": 5
                    }
                }
            }
            
            ],
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
        "boost": 1
    }
    #compile list of filters, depending on checkboxes in UI
    productFilters = []
    if st.session_state['checkboxes'] != [None] * 10:
        for filter in st.session_state['checkboxes']:
            if filter['state']:
                productFilters.append(filter['name'])
        
        if productFilters != []:
            # add terms filter to query
            query['bool']['filter'].append({
                    "terms": {
                        "product_name.enum": productFilters 
                    }
                })
            # add terms filter to knn
            knn['filter'] = {
                    "terms": {
                        "product_name.enum": productFilters 
                    }
                }
            
    agg =  {
    "all_products": {
      "global": {},
      "aggs": {
        "filtered": {
          "filter": {
            "bool": {
              "must": [
                {
                  "match": {
                    "title": {
                      "query": "how",
                      "boost": 1,
                      "analyzer": "stop"
                    }
                  }
                }
              ],
              "filter": [
                {
                  "exists": {
                    "field": "title-vector"
                  }
                }
              ]
            }
          },
          "aggs": {
            "products": {
              "terms": {
                "field": "product_name.enum",
                "size": 10
              }
            }
          }
        }
      }
    }
  }
    fields = ["title", "body_content", "url", "product_name"]
    index = 'search-elastic-docs,search-elastic-docs-2'
    resp = es.search(index=index,query=query,knn=knn,fields=fields,size=size,source=False, aggs=agg)
    return resp

# limit the prompt to the max tokens allowed
def truncate_text(text, max_tokens):
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text

    return ' '.join(tokens[:max_tokens])


# Generate a response from ChatGPT based on the given prompt
def chat_gpt(prompt, result, index, traceparent, apm, model="gpt-3.5-turbo", max_tokens=1024, max_context_tokens=4000, safety_margin=1000):
    # Truncate the prompt content to fit within the model's context length
    parent = elasticapm.trace_parent_from_string(traceparent)
    apm.begin_transaction('openai', trace_parent=parent)
    print("request to openai")
    truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)

    response = openai.ChatCompletion.create(engine=engine,
                                            temperature=0,
                                            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": truncated_prompt}])
    
    result[index] = response
    apm.end_transaction('openai', 'success')

# Generate a response from ChatGPT based on the given prompt, async version
async def achat_gpt(prompt, result, index, element, model="gpt-3.5-turbo", max_tokens=1024, max_context_tokens=4000, safety_margin=1000):
    # Truncate the prompt content to fit within the model's context length
    
    truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)
    
    tries = 0
    while tries < 5:
        try: 
            print("request to openai for task number: " + str(index) + " attempt: " + str(tries))
            output = ""
            counter = 0
            element.empty()
            async with elasticapm.async_capture_span('openaiChatCompletion', span_type='openai'):
                async for chunk in await openai.ChatCompletion.acreate(
                    engine=engine, 
                    messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": truncated_prompt}],
                    stream=True,
                    temperature=0,
                    presence_penalty=-1,
                    frequency_penalty=-1,
                    ):
                    content = chunk["choices"][0].get("delta", {}).get("content")
                    # the counter tracks the number of tokens we received
                    # this is not required, but it's a good way to track the cost later
                    counter += 1
                    # since we have the stream=True option, we can get the output as it comes in
                    # one iteration is one token
                    with elasticapm.capture_span("token", leaf=True, span_type="http"):
                        if content is not None:
                            # concatenate the output to the previous one, so have the full response at the end
                            output += content
                            # with every token we get, we update the element
                            #time.sleep(0.01)
                            element.markdown(output)
            break
        except Exception as e:
            client = elasticapm.get_client()
            client.capture_exception()
            tries += 1
            time.sleep(tries * tries / 2)
            if tries == 5:
                element.error("Error: " + str(e))
            else:
                print("retrying...")
        
    
    # add the output to the result dictionary, so we can access the full response later

    result[index] = {'usage': {"total_tokens":  counter }, "choices": [{"message": {"content": output}}]}

    # update the completed tasks counter, so the UI can show the progress if multiple requests are done in parallel
    st.session_state['completed'] = st.session_state['completed'] + 1
    
    # update the progress bar, with a workaround to limit the progress to 100%
    progress = st.session_state['completed']/(numberOfResults)
    if progress > 1:
        progress = 1
    st.session_state['topResult'].progress(progress, text=f"loading individual results...{st.session_state['completed']}/{numberOfResults}")
    print("##################finished request to openai for task number: " + str(index))
# exception handling for the async tasks, so we can show the error in the UI
def handle_exception(loop, context):
    client = elasticapm.get_client()    
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    exception = context.get("exception", context["message"])
    with st.session_state['topResult']:
        st.error(msg)
    #apmClient.ca()
    client = elasticapm.get_client()    
    elasticapm.set_transaction_outcome("failure")
    client.capture_exception(exc_info=("OpenAiError", exception, None))
    apmClient.end_transaction("user-query")
    print("Caught exception: #####################")
    print(msg)
    print(exception)
    #asyncio.create_task(shutdown(loop))


st.set_page_config(layout="wide")
st.title("ElasticDocs GPT")

@st.cache_resource
def initAPM():
    # the APM Agent is initialized
    apmClient = elasticapm.Client(service_name="elasticdocs-gpt-v2-streaming")
    # the default instrumentation is applied
    # this will instrument the most common libraries
    elasticapm.instrument()  
    return apmClient

apmClient = initAPM()


# start building the UI, adding a title and a sidebar

with st.sidebar:
        st.sidebar.title("Options")
        st.session_state['summarizeResults'] = ({ 'name': 'summarization', 'state': st.checkbox('summarization', value=True)})
        st.session_state['hideirrelevant'] = ({ 'name': 'hideirrelevant', 'state': st.checkbox('hide irrelevant', value=False)})
        st.sidebar.title("Filters")

# this number controls the number of results to show
# setting this higher will increase the cost, as more requests are made to the model
numberOfResults = 5

# initialize the session state
if 'resp' not in st.session_state:
    st.session_state['resp'] = None
    st.session_state['summary'] = None
    st.session_state['openai_tokens'] = 0
    st.session_state['runtime_es'] = 0
    st.session_state['runtime_openai'] = 0
    st.session_state['openai_tokens'] = 0
    st.session_state['openai_current_tokens'] = 0
    st.session_state['results'] = [None] * numberOfResults
    st.session_state['checkboxes'] = [None] * 10
    st.session_state['topResult'] = None
    st.session_state['completed'] = 0

# Main chat form
with st.form("chat_form", ):
    query = st.text_input("You: ")
    submit_button = st.form_submit_button("Search", )

    # placeholder for the top result that we can fill later
    st.session_state['topResult'] = st.empty()

# build a placeholder structure consisting of rows and columns
rows = [None] * numberOfResults

col0h, col1h, col2h = st.columns([1,3,3])
col1h.markdown(f"#### ChatGPT Results")
col2h.markdown(f"#### Docs Results")

for rowNum in range(numberOfResults):
    rows[rowNum] = st.empty()

# the user submitted a query
if submit_button:
    st.session_state['summary'] = None
    st.session_state['completed'] = 0
    # show a progress bar
    st.session_state['topResult'].progress(st.session_state['completed']/(numberOfResults), text=f"loading individual results...")

    # start the APM transaction
    apmClient.begin_transaction("user-query")
    try:
        # add custom labels to the transaction, so we can see the users question in the API UI
        elasticapm.label(query=query)
        start = time.time()
        # query Elasticsearch for the top N results
        resp = search(query, numberOfResults )
        end = time.time()
        st.session_state['runtime_es'] = end - start
        st.session_state['resp'] = resp
        counter = 0
        threads = []

        # initialize the result dictionary. This is used to store the results of the async tasks
        results = [None] * numberOfResults

        # build the loop for the async tasks
        loop = asyncio.new_event_loop()
        loop.set_exception_handler(handle_exception)
        asyncio.set_event_loop(loop)
        tasks = []
        
        # prepare the facets/filtering
        st.session_state['checkboxes'] = [None] * len(resp['aggregations']['all_products']['filtered']['products']['buckets'])


        #for hit in resp['hits']['hits']:
        #    body = hit['fields']['body_content'][0]
        #    url = hit['fields']['url'][0]
        #    counter += 1

        counter = 0
        with elasticapm.capture_span("individual-results", "openai"):
            for hit in resp['hits']['hits']:
                body = hit['fields']['body_content'][0]
                url = hit['fields']['url'][0]
                prompt = f"Answer this question: {query}\n. Don’t give information not mentioned in the CONTEXT INFORMATION. If the CONTEXT INFORMATION contains code or API requests, your response should include code snippets to use in Kibana DevTools Console. If the context does not contain relevant information, answer 'The provided page does not answer the question': \n {body}"
                counter += 1
                
                try:
                    with rows[counter-1]:
                        with st.container():
                            #col0, col1, col2 = rows[counter-1]
                            col0, col1, col2 = st.columns([1,3,3])
                            col0.markdown(f"***")
                            col0.write(f"**Result {counter}:** ", unsafe_allow_html=False)
                            col0.write(f"**{resp['hits']['hits'][counter-1]['fields']['product_name'][0]}** ", unsafe_allow_html=False)
                            col1.markdown(f"***")
                            col1.markdown(f"**{resp['hits']['hits'][counter-1]['fields']['title'][0].strip()}**")
                            element = col1.markdown('')
                            
                            tasks.append(loop.create_task(achat_gpt(prompt, results, counter -1, element)))
                            col2.markdown(f"***")
                            col2.markdown(f"**{resp['hits']['hits'][counter-1]['fields']['title'][0].strip() }**")

                            content = resp['hits']['hits'][counter-1]['fields']['body_content'][0]
                            # limit content length to 200 chars 
                            if len(content) > 200:
                                content = content[:1000] + "..."
                            col2.write(f"{content}", unsafe_allow_html=False)
                            col2.write(f"**Docs**: {resp['hits']['hits'][counter-1]['fields']['url']}", unsafe_allow_html=False)
                            col2.write(f"score: {resp['hits']['hits'][counter-1]['_score']}", unsafe_allow_html=False)    
                            rows[counter-1] = col0, col1, col2    
                except:
                    pass
                
                # t = Thread(target=chat_gpt, args=(prompt, results, counter, elasticapm.get_trace_parent_header(), apmClient))
                #element = st.empty()
                #element.markdown('')
                #tasks.append(loop.create_task(achat_gpt(prompt, results, counter, elasticapm.get_trace_parent_header(), apmClient, element)))
                
                #threads.append(t)

            #for thread in threads:
            #    thread.start()
            # Wait for all of them to finish

            start = time.time()
            #for x in threads:
            #    x.join()
            print("waiting for openai tasks to finish")
            loop.run_until_complete(asyncio.wait(tasks))
            st.session_state['results'] = results
            
            end = time.time()
            print("openai tasks done")
            st.session_state['runtime_openai'] = end - start
        counter = 0

        st.session_state['openai_current_tokens'] = 0
        for i, resultObject in enumerate(results):
            st.session_state['openai_current_tokens'] = st.session_state['openai_current_tokens'] + resultObject['usage']["total_tokens"]  + len(resp['hits']['hits'][i]['fields']['body_content'][0]) / 4
            st.session_state['openai_tokens'] = st.session_state['openai_tokens'] + st.session_state['openai_current_tokens']

        concatResult = ""
        for resultObject in results:            

            if not resultObject['choices'][0]["message"]["content"].startswith("The provided page does not answer the question"):
                concatResult += resultObject['choices'][0]["message"]["content"]
        #st.session_state['topResult'].progress(st.session_state['completed']/(numberOfResults), text=f"loading individual results...")
        if st.session_state['summarizeResults']['state']:
            results = [None] * 1
            tasks = []
            prompt = f"I will give you {numberOfResults} answers to this question.: \"{query}\"\n. They are ordered by their likelyhood to be correct. Come up with the best answer to the original question, using only the context I will provide you here. If the provided context contains code snippets or API requests, half of your response must be code snippets or API requests. If the context does not contain relevant information, answer 'The provided page does not answer the question': \n {concatResult}"
            element = None
            with st.session_state['topResult']:
                with st.container():
                    st.markdown(f"**Summary of all results:**")
                    element = st.empty()

            with elasticapm.capture_span("top-result", "openai"):
                task = loop.create_task(achat_gpt(prompt, results, counter, element))
                tasks.append(task)
                loop.set_exception_handler(handle_exception)
                loop.run_until_complete(asyncio.wait(tasks))
            st.session_state['summary'] = results[0]['choices'][0]["message"]["content"]
            st.session_state['openai_current_tokens'] += results[0]['usage']["total_tokens"]  + len(concatResult) / 4
            st.session_state['openai_tokens'] += st.session_state['openai_current_tokens']
            loop.close()
        else: 
            time.sleep(0.5)
            st.session_state['topResult'].empty()

        elasticapm.label(openapi_tokens = st.session_state['openai_current_tokens'])
        elasticapm.label(openapi_cost = st.session_state['openai_current_tokens'] / 1000 * 0.002)

        elasticapm.set_transaction_outcome("success")
        apmClient.end_transaction("user-query")
        
    except Exception as e:
      apmClient.capture_exception()
      elasticapm.set_transaction_outcome("failure")
      apmClient.end_transaction("user-query")
      print(e)
      st.error(e)
    
if st.session_state['resp'] != None:
    try:
        resp = st.session_state['resp']
        counter = 0

        threads = []
        st.session_state['checkboxes'] = [None] * (len(resp['aggregations']['all_products']['filtered']['products']['buckets']))
        

        for i, product in enumerate(resp['aggregations']['all_products']['filtered']['products']['buckets']):
            with st.sidebar:
                value = product['key'] + ' (' + str(product['doc_count']) + ')'
                st.session_state['checkboxes'][i] = ({ 'name': product['key'], 'state': st.checkbox(value, value=False)})

        for hit in resp['hits']['hits']:
            body = hit['fields']['body_content'][0]
            url = hit['fields']['url'][0]
            counter += 1

        counter = 0
        with col1h:
            with st.expander("See cost and runtime details"):
                st.markdown(f"OpenAi request cost: ${round(st.session_state['openai_current_tokens'] / 1000 * 0.002, 3)}")
                st.markdown(f"OpenAi running cost: ${round(st.session_state['openai_tokens'] / 1000 * 0.002, 3)}")
                st.markdown(f"OpenAi request duration: {round(st.session_state['runtime_openai'], 3)} seconds")
        with col2h:
            with st.expander("See runtime details"):
                st.markdown("")
                st.markdown("")
                st.markdown(f"Elasticsearch query duration: {round(st.session_state['runtime_es'], 3)} seconds")
        for resultObject in  st.session_state['results']:
            result = resultObject['choices'][0]["message"]["content"]
            counter += 1
            print("##################################")
            showResult = False
            if st.session_state['hideirrelevant']['state']:
                if result != "The provided page does not answer the question.":
                    showResult = True
            else: 
                showResult = True

            if showResult:
                print("relevant")
                try:
                    with rows[counter-1]:
                            with st.container():
                                col0, col1, col2 = st.columns([1,3,3])
                                col0.markdown(f"***")
                                col0.write(f"**Result {counter}:** ", unsafe_allow_html=False)
                                col0.write(f"**{resp['hits']['hits'][counter-1]['fields']['product_name'][0]}** ", unsafe_allow_html=False)

                                col1.markdown(f"***")

                                col1.markdown(f"**{resp['hits']['hits'][counter-1]['fields']['title'][0].strip()}**")
                                col1.write(f"{result.strip()}", unsafe_allow_html=False)

                                col2.markdown(f"***")
                                col2.markdown(f"**{resp['hits']['hits'][counter-1]['fields']['title'][0].strip() }**")

                                content = resp['hits']['hits'][counter-1]['fields']['body_content'][0]
                                # limit content length to length of result
                                content = content[:len(result*2)] + "..."
                                col2.write(f"{content}", unsafe_allow_html=False)
                                col2.write(f"**Docs**: {resp['hits']['hits'][counter-1]['fields']['url']}", unsafe_allow_html=False)
                                col2.write(f"score: {resp['hits']['hits'][counter-1]['_score']}", unsafe_allow_html=False)                    
                except:
                    continue
            else: 
                print("irrelevant")
        # display the top result if enabled
        if st.session_state['summarizeResults']['state']:
            with st.session_state['topResult']:
                with st.container():
                    # write the top result
                    st.write(st.session_state['summary'])

                    # iterate over hits and build a markdown string with the title and link to the documentation as a hyperlink, 
                    # if the response is not "The provided page does not answer the question."
                    st.write(f"**Find more information in our documentation**:")
                    markdownString = ""
                    for i, hit in enumerate(resp['hits']['hits']):
                        if st.session_state['results'][i]['choices'][0]["message"]["content"] != "The provided page does not answer the question.":
                            markdownString += f"[{hit['fields']['title'][0]}]({hit['fields']['url'][0]})\n\n"
                    st.write(markdownString)

        elasticapm.set_transaction_outcome("success")
        apmClient.end_transaction("user-query")
    except Exception as e:
        apmClient.capture_exception()
        elasticapm.set_transaction_outcome("failure")
        apmClient.end_transaction("user-query")
        st.error(e)

