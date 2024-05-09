#!/bin/bash
# add any notebooks that are currently not testable to the exempt list
EXEMPT_NOTEBOOKS=(
    "notebooks/esql/esql-getting-started.ipynb"
    "notebooks/search/07-inference.ipynb"
    "notebooks/search/08-learning-to-rank.ipynb"
    "notebooks/images/image-similarity.ipynb"
    "notebooks/langchain/langchain-vector-store.ipynb"
    "notebooks/langchain/self-query-retriever-examples/chatbot-example.ipynb"
    "notebooks/langchain/self-query-retriever-examples/chatbot-with-bm25-only-example.ipynb"
    "notebooks/langchain/self-query-retriever-examples/langchain-self-query-retriever.ipynb"
    "notebooks/langchain/multi-query-retriever-examples/chatbot-with-multi-query-retriever.ipynb"
    "notebooks/langchain/multi-query-retriever-examples/langchain-multi-query-retriever.ipynb"
    "notebooks/generative-ai/question-answering.ipynb"
    "notebooks/generative-ai/chatbot.ipynb"
    "notebooks/integrations/amazon-bedrock/langchain-qa-example.ipynb"
    "notebooks/integrations/cohere/inference-cohere.ipynb"
    "notebooks/integrations/llama-index/intro.ipynb"
    "notebooks/integrations/gemini/vector-search-gemini-elastic.ipynb"
    "notebooks/integrations/gemini/qa-langchain-gemini-elasticsearch.ipynb"
    "notebooks/integrations/openai/openai-KNN-RAG.ipynb"
    "notebooks/integrations/gemma/rag-gemma-huggingface-elastic.ipynb"
    "notebooks/integrations/azure-openai/vector-search-azure-openai-elastic.ipynb"
    "notebooks/enterprise-search/app-search-engine-exporter.ipynb"
    # "notebooks/ingestion-and-chunking/json-chunking-ingest.ipynb"
    "notebooks/ingestion-and-chunking/pdf-chunking-ingest.ipynb"
    "notebooks/ingestion-and-chunking/website-chunking-ingest.ipynb"
)

ALL_NOTEBOOKS=$(find notebooks -name "*.ipynb" | grep -v "_nbtest" | grep -v ".ipynb_checkpoints" | sort)
for notebook in $ALL_NOTEBOOKS; do
    if [[ ! "${EXEMPT_NOTEBOOKS[@]}" =~ $notebook ]]; then
        echo $notebook
    fi
done
