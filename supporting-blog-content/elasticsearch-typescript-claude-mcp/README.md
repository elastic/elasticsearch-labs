# Elasticsearch RAG MCP Server using Typescript SDK


This MCP server enables Claude Desktop to search through documents stored in Elasticsearch, generate AI-powered summaries, and cite sources.

Built as a companion to the Elastic Search Labs article: [Developing an Elasticsearch MCP with Typescript](https://www.elastic.co/search-labs/blog/elasticsearch-javascript-claude-mcp)

## Tools

1. `search_docs` - Search for relevant documents in Elasticsearch
2. `summarize_and_cite` - Generate AI summaries with source citations

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables in Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "elasticsearch-rag-mcp": {
      "command": "node",
      "args": ["/path/to/App/dist/index.js"],
      "env": {
        "ELASTICSEARCH_ENDPOINT": "https://your-endpoint:443",
        "ELASTICSEARCH_API_KEY": "your-api-key",
        "OPENAI_API_KEY": "your-openai-key"
      }
    }
  }
}
```

3. Build the project:
```bash
npm run build
```

4. Load sample data (optional):
```bash
npm run setup
```

5. Restart Claude Desktop

## Requirements

- Node.js 20+
- Elasticsearch 9.x
- OpenAI API key
- Claude Desktop


