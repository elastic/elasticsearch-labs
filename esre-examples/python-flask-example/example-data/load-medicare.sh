#!/bin/sh

source ../api/.env

python3 index-data.py --index_name=search-medicare --file=medicare.json --es_password=$cloud_pass --cloud_id=$cloud_id
