# Elasticsearch MCP Server

Connect to your Elasticsearch data directly from any MCP Client (like Claude Desktop) using the Model Context Protocol (MCP).

This server connects agents to your Elasticsearch data using the Model Context Protocol (MCP). It allows you to interact with your Elasticsearch indices through natural language conversations.

## Features

* **List Indices**: View all available Elasticsearch indices
* **Get Mappings**: Inspect field mappings for specific indices
* **Search**: Execute Elasticsearch queries using full Query DSL capabilities with automatic highlighting

## Prerequisites

* Node.js (v22+)
* An Elasticsearch instance
* Elasticsearch API key with appropriate permissions
* Claude Desktop App (free version is sufficient)

## Installation & Setup

### Using the Published NPM Package

The easiest way to use Elasticsearch MCP Server is through the published npm package:

1. **Configure Claude Desktop App**
   - Open Claude Desktop App
   - Go to Settings > Developer > MCP Servers
   - Click `Edit Config` and add a new MCP Server with the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-server-elasticsearch"
      ],
      "env": {
        "ES_URL": "your-elasticsearch-url",
        "ES_API_KEY": "your-api-key"
      }
    }
  }
}
```

2. **Start a Conversation**
   - Open a new conversation in Claude Desktop App
   - The MCP server should connect automatically
   - You can now ask Claude questions about your Elasticsearch data

### Developing Locally

If you want to develop or modify the server locally:

1. **Use the correct Node.js version**
```bash
nvm use
```

2. **Install Dependencies**
```bash
npm install
```

3. **Build the Project**
```bash
npm run build
```

4. **Configure Claude Desktop for local development**
   - Open Claude Desktop App
   - Go to Settings > Developer > MCP Servers
   - Click `Edit Config` and add a new MCP Server with the following configuration:

```json
{
  "mcpServers": {
    "Elasticsearch MCP Server (Local)": {
      "command": "node",
      "args": [
        "/path/to/your/project/dist/index.js"
      ],
      "env": {
        "ES_URL": "your-elasticsearch-url",
        "ES_API_KEY": "your-api-key"
      }
    }
  }
}
```

5. **Debugging**
```bash
npm run inspector
```

## Example Questions

* "What indices do I have in my Elasticsearch cluster?"
* "Show me the field mappings for the 'products' index"
* "Find all orders over $500 from last month"
* "Which products received the most 5-star reviews?"

## How It Works

When you ask Claude a question about your data:
1. Claude analyzes your request and determines which Elasticsearch operations are needed
2. The MCP server carries out these operations (listing indices, fetching mappings, performing searches)
3. Claude processes the results and presents them in a user-friendly format

## Security Best Practices

You can create a dedicated Elasticsearch API key with minimal permissions to control access to your data:

```
POST /_security/api_key
{
  "name": "es-mcp-server-access",
  "role_descriptors": {
    "claude_role": {
      "cluster": [
        "monitor"
      ],
      "indices": [
        {
          "names": [
            "index-1",
            "index-2",
            "index-pattern-*"
          ],
          "privileges": [
            "read",
            "view_index_metadata"
          ]
        }
      ]
    }
  }
}
```

## Troubleshooting

* If the server isn't connecting, check that your MCP configuration is correct
* Ensure your Elasticsearch URL is accessible from your machine
* Verify that your API key has the necessary permissions
* Check the terminal output for any error messages
