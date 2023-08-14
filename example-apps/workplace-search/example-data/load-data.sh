#!/bin/sh

source ../api/.env

python3 index-data.py --index_name=search-workplace --file=data.json --es_password=$cloud_pass --cloud_id=$cloud_id
