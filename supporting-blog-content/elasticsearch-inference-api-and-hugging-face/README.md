# Elasticsearch Inference API with Hugging Face Models

This notebook demonstrates how to use the Elasticsearch Inference API along with Hugging Face models to build a question and answer system. This notebook is based on the [Using Elasticsearch Inference API along Hugging Face models](https://www.elastic.co/search-labs/blog/elasticsearch-inference-api-and-hugging-face).

## Environment Setup

This project requires environment variables to be configured in a `.env` file. Follow the steps below to create and configure your `.env` file.

### Step 1: Create the `.env` file

In the root directory of this project, create a new file named `.env`:

```bash
touch .env
```

### Step 2: Add Required Variables

Open the `.env` file and add the following variables with your actual values:

```env
ELASTICSEARCH_API_KEY="your_elasticsearch_api_key_here"
ELASTICSEARCH_URL="https://your-cluster.es.region.cloud.es.io:9243"
HUGGING_FACE_API_KEY="your_hugging_face_api_key_here"
HUGGING_FACE_INFERENCE_ENDPOINT_URL="https://api-inference.huggingface.co/models/your-model-endpoint"
```
