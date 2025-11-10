# LangGraph.js + Elasticsearch

This application was developed to demonstrate the integration of LangGraph.js with Elasticsearch for advanced search workflows, as part of the Search Labs blog post [LangGraph JS + Elasticsearch
](https://www.elastic.co/search-labs/blog/langgraph-js-elasticsearch).

**Practical example:** A smart startup search system that combines LangGraph.js workflow orchestration with Elasticsearch's hybrid search capabilities to find venture capital opportunities using natural language queries.

## Prerequisites

- Node.js 18+
- Elasticsearch 9.x running locally or remotely
- OpenAI API key

## Setup

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `ELASTICSEARCH_URL` - Elasticsearch endpoint 
- `ELASTICSEARCH_API_KEY` - Elasticsearch API key

1. Install dependencies:
```bash
npm install
```

2. Run the application:
```bash
npm start
```


## Example usage queries

- **Market focused:**
```
Find fintech and healthcare startups in San Francisco, New York, or Boston
```

- **Invest focused:**
```
Find startups with Series A or Series B funding between $8M-$25M and monthly revenue above $500K 
```