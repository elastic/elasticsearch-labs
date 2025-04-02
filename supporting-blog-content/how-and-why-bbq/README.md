# How to implement Better Binary Quantization (BBQ) into your use case and why you should
Vector search underpins semantic search for text and similarity search for images, videos, or audio. It uses mathematical representations called vectors, which can be large and slow. Better Binary Quantization (BBQ) helps compress these vectors, enabling faster searching while maintaining accuracy. 

This repository contains all the queries corresponding to the article "How to implement Better Binary Quantization (BBQ) into your use case and why you should." This code demonstrates how to use BBQ and the `rescore_vector` feature, which automatically resizes vectors for quantized indices.

## Prerequisites

- Elasticsearch version 8.18 or higher (BBQ was introduced in 8.16, but `rescore_vector` is available from 8.18)
- A machine learning node in your cluster
- For Elastic Cloud serverless, select an instance optimized for vectors

## How to use the code in this repoistory
This repository has two folders, `Queries` and `Outputs`. `Queries` contain commands that you will run the queries from the [Kibana Dev Tools Console](https://www.elastic.co/guide/en/kibana/8.18/console-kibana.html), while `Outputs` has the corresponding JSON outputs of those commands.
