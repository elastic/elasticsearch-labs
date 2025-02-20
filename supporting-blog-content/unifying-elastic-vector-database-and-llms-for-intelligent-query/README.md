
# Unifying Elastic Vector Database and LLMs for Intelligent Retrieval

## Overview
This notebook demonstrates how to integrate Elasticsearch as a vector database (VectorDB) with search templates and LLM functions to build an intelligent query layer. By leveraging vector search, dynamic query templates, and natural language processing, this approach enhances search precision, adaptability, and efficiency.

## Features
- **Elasticsearch as a VectorDB**: Efficiently stores and retrieves dense vector embeddings for advanced search capabilities.
- **Search Templates**: Dynamically structure queries by mapping user inputs to the appropriate index parameters.
- **LLM Functions**: Extract key search parameters from natural language queries and inject them into search templates.
- **Hybrid Search**: Combines structured filtering with semantic search to improve search accuracy and relevance.

## Components
- **Geocode Location Function**: Converts location names into latitude and longitude for geospatial queries.
- **Handle Extract Hotel Search Parameters Function**: Processes extracted search parameters, ensuring essential values like distance are correctly assigned.
- **Call Elasticsearch Function**: Executes structured search queries using dynamically populated search templates.
- **Format and Print Messages Functions**: Enhances query debugging by formatting and displaying responses in a structured format.
- **Run Conversation Function**: Orchestrates interactions between user queries, LLM functions, and Elasticsearch search execution.
- **Search Template Management Functions**: Defines, creates, and deletes search templates to optimize query processing.

  
## Usage
1. Set up an Elasticsearch cluster and ensure vector search capabilities are enabled.
2. Define search templates to map query parameters to the index schema.
3. Use LLM functions to extract and refine search parameters from user queries.
4. Run queries using the intelligent query layer to retrieve more relevant and accurate results.


### Prerequisites
- Elastic Cloud instance
  - With ML nodes
- Azure OpenAI
  - Completions endpoint such as GPT-4o
    - For more information on getting started with Azure OpenAI, check out the official [Azure OpenAI ChatGPT Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Ctypescript%2Cpython-new&pivots=programming-language-studio).
  - Azure OpenAI Key
- Google Maps API Key
  - https://developers.google.com/maps/documentation/embed/get-api-key

