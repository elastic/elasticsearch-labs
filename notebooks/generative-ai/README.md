# Generative AI notebooks

This folder contains notebooks that demonstrate various use cases for Elasticsearch as the retrieval engine and vector store for LLM-powered applications.

The following notebooks are available:

- [Question answering](#question-answering)
- [Chatbot](#chatbot)

## Notebooks

### Question answering

In the [`question-answering.ipynb`](./question-answering.ipynb) notebook you'll learn how to:

- Retrieve sample workplace documents from a given URL.
- Set up an Elasticsearch client.
- Chunk documents into 800-character passages with an overlap of 400 characters using the `CharacterTextSplitter` from `langchain`.
- Use `OpenAIEmbeddings` from `langchain` to create embeddings for the content.
- Retrieve embeddings for the chunked passages using OpenAI.
- Persist the passage documents along with their embeddings into Elasticsearch.
- Set up a question-answering system using `OpenAI` and `ElasticKnnSearch` from `langchain` to retrieve answers along with their source documents.

### Chatbot

In the [`chatbot.ipynb`](./chatbot.ipynb) notebook you'll learn how to:

- Retrieve sample workplace documents from a given URL.
- Set up an Elasticsearch client.
- Chunk documents into 800-character passages with an overlap of 400 characters using the `CharacterTextSplitter` from `langchain`.
- Use `OpenAIEmbeddings` from `langchain` to create embeddings for the content.
- Retrieve embeddings for the chunked passages using OpenAI.
- Run hybrid search in Elasticsearch to find documents that answers asked questions.
- Maintain conversational memory for follow-up questions.
