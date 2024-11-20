#!/bin/bash

EXEMPT_NOTEBOOKS=(
    # Add any notebooks that are currently not testable to the exempt list
    "notebooks/esql/esql-getting-started.ipynb"
    "notebooks/search/07-inference.ipynb"
    "notebooks/search/08-learning-to-rank.ipynb"
    "notebooks/search/10-semantic-reranking-retriever-cohere.ipynb"
    "notebooks/search/11-semantic-reranking-hugging-face.ipynb"
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
    "notebooks/integrations/cohere/cohere-elasticsearch.ipynb"
    "notebooks/integrations/cohere/inference-cohere.ipynb"
    "notebooks/integrations/llama-index/intro.ipynb"
    "notebooks/integrations/gemini/vector-search-gemini-elastic.ipynb"
    "notebooks/integrations/gemini/qa-langchain-gemini-elasticsearch.ipynb"
    "notebooks/integrations/openai/openai-KNN-RAG.ipynb"
    "notebooks/integrations/openai/function-calling.ipynb"
    "notebooks/integrations/gemma/rag-gemma-huggingface-elastic.ipynb"
    "notebooks/integrations/llama3/rag-elastic-llama3-elser.ipynb"
    "notebooks/integrations/llama3/rag-elastic-llama3.ipynb"
    "notebooks/integrations/azure-openai/vector-search-azure-openai-elastic.ipynb"
    "notebooks/enterprise-search/app-search-engine-exporter.ipynb",
    "notebooks/playground-examples/bedrock-anthropic-elasticsearch-client.ipynb",
    "notebooks/playground-examples/openai-elasticsearch-client.ipynb",
    "notebooks/integrations/cohere/updated-cohere-elasticsearch-inference-api.ipynb",
    "notebooks/integrations/alibabacloud-ai-search/inference-alibabacloud-ai-search.ipynb"
)

# Per-version testing exceptions
# use variables named EXEMPT_NOTEBOOKS__{major}_[minor} to list notebooks that
# cannot run on that stack version or older
# Examples:
# EXEMPT_NOTEBOOKS__8 for notebooks that must be skipped on all versions 8.x and older
# EXEMPT_NOTEBOOKS__8_12 for notebooks that must be skipped on versions 8.12 and older

EXEMPT_NOTEBOOKS__8_12=(
    # Add any notebooks that must be skipped on versions 8.12 or older here
    "notebooks/document-chunking/with-index-pipelines.ipynb"
    "notebooks/document-chunking/with-langchain-splitters.ipynb"
    "notebooks/integrations/hugging-face/loading-model-from-hugging-face.ipynb"
    "notebooks/langchain/langchain-using-own-model.ipynb"
)

EXEMPT_NOTEBOOKS__8_14=(
    # Add any notebooks that must be skipped on versions 8.14 or older here
    "notebooks/search/09-semantic-text.ipynb",
    # This notebook has the text_expansion deprecation notice for 8.15. 
    # Only running on 8.15 so includes the deprecation notice and newer so the local output is the same as CI
    "notebooks/langchain/langchain-vector-store-using-elser.ipynb",
)

# this function parses a version given as M[.N[.P]] or M[_N[_P]] into a numeric form
function parse_version { echo "$@" | awk -F'[._]' '{ printf("%02d%02d\n", $1, $2); }'; }

# this is the version CI is running
ci_version=$(parse_version ${ES_STACK:-99.99})

ALL_NOTEBOOKS=$(find notebooks -name "*.ipynb" | grep -v "_nbtest" | grep -v ".ipynb_checkpoints" | sort)
for notebook in $ALL_NOTEBOOKS; do
    skip=
    # check the master exception list
    if [[ "${EXEMPT_NOTEBOOKS[@]}" =~ $notebook ]]; then
        skip=yes
    else
        # check the versioned exception lists
        for exempt_key in ${!EXEMPT_NOTEBOOKS__*}; do
            exempt_version=$(parse_version ${exempt_key/EXEMPT_NOTEBOOKS__/})
            if [ $exempt_version -ge $ci_version ]; then
                exempt_notebooks=$(eval 'echo ${'${exempt_key}'[@]}')
                if [[ "${exempt_notebooks[@]}" =~ $notebook ]]; then
                    skip=yes
                fi
            fi
        done
    fi
    if [[ "$skip" == "" ]]; then
        echo $notebook
    fi
done
