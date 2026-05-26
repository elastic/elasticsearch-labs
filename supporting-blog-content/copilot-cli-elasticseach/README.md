# GitHub Copilot CLI - Elasticsearch Plugin

The official Elasticsearch plugin for the GitHub Copilot CLI. Search, retrieve, and analyze Elasticsearch data directly in your agentic workflows using the Model Context Protocol (MCP).

## Prerequisites
You need an active Elasticsearch deployment (Serverless or 9.3+) and its corresponding MCP server URL and API Key.

Set the following environment variables in your shell (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export ELASTIC_MCP_URL="your-elasticsearch-mcp-url"
export ELASTIC_API_KEY="your-encoded-api-key"
