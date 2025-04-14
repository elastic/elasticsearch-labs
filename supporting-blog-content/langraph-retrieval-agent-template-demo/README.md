
# LangGraph RAG Workflow with Elasticsearch

This project contains the code to create a custom agent using the LangGraph Retrieval Agent Template with Elasticsearch to build an efficient Retrieval-Augmented Generation (RAG) workflow for AI-driven responses.


## Introduction

LangGraph, developed by LangChain, simplifies the creation of retrieval-based question-answering systems. By using LangGraph Studio and LangGraph CLI, you can quickly build agents that index and retrieve documents using Elasticsearch.

## Prerequisites

Before you start, ensure you have the following installed:

- Elasticsearch (Cloud or on-prem, version 8.0.0 or higher)
- Python 3.9+
- Access to an LLM provider like Cohere, OpenAI, or Anthropic

## Steps to Set Up the LangGraph App

### 1. Install LangGraph CLI

```bash
pip install --upgrade "langgraph-cli[inmem]"
```
### 2. Create LangGraph App
```
mkdir lg-agent-demo
cd lg-agent-demo
langgraph new lg-agent-demo
```
### 3. Install Dependencies
Create a virtual environment and install the dependencies:

For macOS:
```
python3 -m venv lg-demo
source lg-demo/bin/activate
pip install -e .
```
For Windows:
```
python3 -m venv lg-demo
lg-demo\Scripts\activate
pip install -e .
```
### 4. Set Up Environment
Create a .env file by copying the example:

```
cp .env.example .env
```
Then, configure your .env file with your API keys and URLs for Elasticsearch and LLM.

### 5. Update configuration.py
Modify the configuration.py file to set up your LLM models, like Cohere (or OpenAI/Anthropic), as shown below:


```embedding_model = "cohere/embed-english-v3.0"
response_model = "cohere/command-r-08-2024"
query_model = "cohere/command-r-08-2024"
```

## Running the Agent

### 1. Launch LangGraph Server
```
cd lg-agent-demo
langgraph dev
```
This starts the LangGraph API server locally.

### 2. Open LangGraph Studio
You can now access the LangGraph Studio UI and see the following:
<img width="1306" alt="Screenshot 2025-04-01 at 6 02 31 PM" src="https://github.com/user-attachments/assets/c7c13645-99a1-48b2-8d3c-c1135fd33f54" />
Indexer Graph: Indexes documents into Elasticsearch.

<img width="776" alt="Screenshot 2025-03-11 at 6 08 09 PM" src="https://github.com/user-attachments/assets/5d61b9d0-ae9e-4d66-9e99-fa27bce7a1d0" />


Retrieval Graph: Retrieves data from Elasticsearch and answers queries using the LLM.

### 3. Index Sample Documents
Index the sample documents into Elasticsearch (representing the NoveTech Solutions reports).

### 4. Run the Retrieval Graph
Enter a query like:

```
What was NovaTech Solutions' total revenue in Q1 2025?
The system will retrieve relevant documents and provide an answer.
```
## Customizing the Retrieval Agent
## Query Prediction
To enhance user experience, add a query prediction feature based on the context from previous queries and retrieved documents. Here’s what to do:

1. Add predict_query function in graph.py.

2. Modify the respond function to return a response object.

3. Update the graph structure to include a new node for query prediction.

4. Modify Prompts and Configuration
Update prompts.py to define a prompt for predicting the next question. Then, modify configuration.py to add this new prompt.

```
predict_next_question_prompt: str = "Your prompt here"
```
Re-run the Retrieval Graph
Run the query again to see the predicted next three questions based on the context.
<img width="732" alt="Screenshot 2025-03-17 at 3 06 54 PM" src="https://github.com/user-attachments/assets/88832fa6-4dc9-41cc-894d-d3d437bf4d80" />

## Conclusion
By using the LangGraph Retrieval Agent template with Elasticsearch, you can:

- Accelerate development by using pre-configured templates.

- Easily deploy with built-in API support and scaling.

- Customize workflows to fit your specific use case.
