
from tqdm import tqdm
from elasticsearch import Elasticsearch, helpers
import argparse
import os
import json

parser = argparse.ArgumentParser()
# required args
parser.add_argument('--data_folder', dest='data_folder',
                    required=False, default='./data')
parser.add_argument('--es_user', dest='es_user',
                    required=False, default='elastic')
parser.add_argument('--es_password', dest='es_password', required=True)
parser.add_argument('--cloud_id', dest='cloud_id', required=True)
parser.add_argument('--index_name', dest='index_name',
                    required=False, default='search-workplace')
parser.add_argument('--file', dest='file',
                    required=False, default='data.json')

args = parser.parse_args()


def data_generator(file_json, index, pipeline):
    for doc in file_json:
        doc['_run_ml_inference'] = True
        yield {
            "_index": index,
            'pipeline': pipeline,
            "_source": doc,
        }


print("Init Elasticsearch client")
es = Elasticsearch(
    cloud_id=args.cloud_id,
    basic_auth=(args.es_user, args.es_password),
    request_timeout=600
)

print("Indexing documents, this might take a while...")
with open(args.file, 'r') as file:
    file_json = json.load(file)
total_documents = len(file_json)
progress_bar = tqdm(total=total_documents, unit="documents")
success_count = 0

for response in helpers.streaming_bulk(client=es, actions=data_generator(file_json, args.index_name, args.index_name)):
    if response[0]:
        success_count += 1
    progress_bar.update(1)
    progress_bar.set_postfix(success=success_count)

progress_bar.close()

# Calculate the success percentage
success_percentage = (success_count / total_documents) * 100
print(f"Indexing completed! Success percentage: {success_percentage}%")
print("Done indexing documents!")
