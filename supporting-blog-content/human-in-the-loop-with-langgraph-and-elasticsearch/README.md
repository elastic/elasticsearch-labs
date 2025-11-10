# LangGraph + Elasticsearch Human-in-the-Loop

Flight search application using LangGraph for human-in-the-loop workflow and Elasticsearch for vector search.

## Prerequisites

- Node.js 18+
- Elasticsearch instance
- OpenAI API key

## Installation

### Quick Install 

```bash
npm install
```

### Manual Install (Alternative)

```bash
npm install @elastic/elasticsearch @langchain/community @langchain/core @langchain/langgraph @langchain/openai dotenv --legacy-peer-deps
npm install --save-dev tsx 
```

## Configuration

Create a `.env` file in the root directory:

```env
ELASTICSEARCH_ENDPOINT=https://your-elasticsearch-instance.com
ELASTICSEARCH_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-api-key
```

## Usage

```bash
npm start
```

## Features

- 🔍 Vector search with Elasticsearch
- 🤖 LLM-powered natural language selection
- 👤 Human-in-the-loop workflow with LangGraph
- 📊 Workflow visualization (generates `workflow_graph.png`)

## Workflow

1. **Retrieve Flights** - Search Elasticsearch with vector similarity
2. **Evaluate Results** - Auto-select if 1 result, show options if multiple
3. **Show Results** - Display flight options to user
4. **Request User Choice** - Pause workflow for user input (HITL)
5. **Disambiguate & Answer** - Use LLM to interpret selection and return final answer

