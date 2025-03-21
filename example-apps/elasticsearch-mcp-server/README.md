# Elasticsearch MCP Server

Connect to your Elasticsearch data directly from any MCP Client (like Claude Desktop) using the Model Context Protocol (MCP).

This server connects agents to your Elasticsearch data using the Model Context Protocol (MCP). It allows you to interact with your Elasticsearch indices through natural language conversations.

## Features

- **List Indices**: View all available Elasticsearch indices
- **Get Mappings**: Inspect field mappings for specific indices
- **Search**: Execute Elasticsearch queries using full Query DSL capabilities with automatic highlighting

## Prerequisites

- Node.js (v22+)
- An Elasticsearch instance
- Elasticsearch API key with appropriate permissions
- Claude Desktop App (free version is sufficient)

## Setup Guide

Make sure you use a supported Node.js version:

```
nvm use
```

### 1. Install Dependencies

```bash
npm install
```

### 2. Build the Project

```bash
npm run build
```


### 3. Configure Claude Desktop App

1. Open Claude Desktop App
2. Go to Settings > Developer > MCP Servers
3. Click `Edit Config` and add a new MCP Server with the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Elasticsearch MCP Server": {
      "command": "npx",
      "args": [
        "-y",
        "node@22",
        "/path/to/your/project/dist/index.js"
      ],
      "env": {
        "ES_URL": "...",
        "ES_API_KEY": "..."
      }
    }
  }
}
```

Replace `/path/to/your/elasticsearch-mcp/dist/index.js` with the actual path to the built JavaScript file, and fill in your Elasticsearch URL and API key.

### 4. Start a Conversation

1. Open a new conversation in Claude Desktop App
2. The MCP server should connect automatically
3. You can now ask Claude questions about your Elasticsearch data

## Example Questions

- "What indices do I have in my Elasticsearch cluster?"
- "Show me the field mappings for the 'products' index"
- "Find all orders over $500 from last month"
- "Which products received the most 5-star reviews?"

## How It Works

When you ask Claude a question about your data:

1. Claude analyzes your request and determines which Elasticsearch operations are needed
2. The MCP server carries out these operations (listing indices, fetching mappings, performing searches)
3. Claude processes the results and presents them in a user-friendly format

## Troubleshooting

- If the server isn't connecting, check that the path in your MCP configuration is correct
- Ensure your Elasticsearch URL is accessible from your machine
- Verify that your API key has the necessary permissions
- Check the terminal output for any error messages

You can also use the inspector tool to debug your MCP server:

```bash
npm run inspector
```

## Security Best Practices

You can create a dedicated Elasticsearch API key with minimal permissions to control access to your data:

```
POST /_security/api_key
{
  "name": "es-mcp-server-access",
  "role_descriptors": {
    "claude_role": {
      "cluster": ["monitor"],
      "indices": [
        {
          "names": ["index-1", "index-2", "index-pattern-*"],
          "privileges": ["read", "view_index_metadata"]
        }
      ]
    }
  }
}
```
