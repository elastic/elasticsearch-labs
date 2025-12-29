# LangGraph + Elasticsearch Human-in-the-Loop

This is a supporting blog content for the article: [Building Human-in-the-Loop AI Agents with LangGraph and Elasticsearch](https://www.elastic.co/search-labs/blog/human-in-the-loop-with-langgraph-and-elasticsearch).

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
ELASTICSEARCH_API_KEY="your-api-key"
OPENAI_API_KEY="your-openai-api-key"
```

## Usage

```bash
npm start
```