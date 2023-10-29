import os
import time
#print(os.environ['ELASTIC_CLOUD_ID'])
#time.sleep(10)
from elasticsearch import Elasticsearch

from elasticsearch_llm_cache import (
    ElasticsearchLLMCache,  # Import the class from the file
)

from pprint import pprint
import time

# Initialize Elasticsearch client
es_client = Elasticsearch(
    cloud_id=os.environ['ELASTIC_CLOUD_ID'],
    basic_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASSWORD']),
    request_timeout=30)

# Initialize your caching class
cache = ElasticsearchLLMCache(es_client=es_client, index_name="llm_cache_test")
#print(cache)

# Example prompt, response, and prompt vector
example_prompt = "What is the capital of France?"
example_response = "The capital of France is Paris."
print(f'example prompt: {example_prompt}')
print(f'example LLM Response: {example_response}')

#
print ('first pass attempt')
q1= 'What is the capital of France?'
print(f'query 1: {q1}')
query_result_1 = cache.query(prompt_text=q1)
print("Query result 1:") 
pprint(query_result_1)
print()


# Add document to cache
add_result = cache.add(prompt=example_prompt, response=example_response)
print("Add result to cache: ")
pprint(add_result)
print()
time.sleep(5)

# Query the cache (simulating later, separate operations)
print()
print ('Second pass attempt')
print("Testing cached similar results\n")
print()

q1= 'What is the capital of France?'
print(f'query 1: {q1}')
query_result_1 = cache.query(prompt_text=q1)
print("Query result 1:") 
pprint(query_result_1)
print()

q2= 'What is the currency of the UK?'
print(f'query 1: {q2}')
query_result_2 = cache.query(prompt_text=q2)
print("Query result 2:") 
pprint(query_result_2)
