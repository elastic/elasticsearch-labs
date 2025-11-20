# Elastic Agent Builder A2A App 

**Getting started with Agent Builder and A2A using Microsoft Agent Framework**

This is an example Python console app that demonstrates how to connect and utilize an [Elastic Agent Builder](https://www.elastic.co/elasticsearch/agent-builder) agent via the Agent2Agent (A2A) Protocol orchestrated with the [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview).

## Prerequisites

1. An Elasticsearch project/deployment running in [Elastic Cloud](https://cloud.elastic.co/registration?utm_source=github&utm_content=elasticsearch-labs-example-apps). 
   * Requires Elasticsearch serverless project (or for hosted deployments at least Elasticsearch version 9.2.0).
2. A text editor or an integrated development environment (IDE) like [Visual Studio Code](https://code.visualstudio.com/download) running on your local computer.  
3. [Python version 3.10 or greater](https://www.python.org/downloads/) installed on your local computer.

## Set up your Elasticsearch project

1. Create an index named `my-docs` in your Elasticsearch project by running the following command in Elastic Developer Tools:

        PUT /my-docs
        {
            "mappings": {
                "properties": {
                    "title": { "type": "text" },
                    "content": { 
                        "type": "semantic_text"
                    },
                    "filename": { "type": "keyword" },
                    "last_modified": { "type": "date" }
                }
            }
        }
2. Insert a document into your index named `greetings.md` by running the following command in Elastic Developer Tools:

        PUT /my-docs/_doc/greetings-md
        {
            "title": "Greetings",
            "content": "
        # Greetings
        ## Basic Greeting
        Hello!

        ## Helloworld Greeting
        Hello World! 🌎

        ## Not Greeting
        I'm only a greeting agent. 🤷

        ",
            "filename": "greetings.md",
            "last_modified": "2025-11-04T12:00:00Z"
        }

3. In Elastic Agent Builder, create a **tool** with the following values:  
* **Type**: `ES|QL`  
* **Tool ID**: `example.get_greetings` 
* **Description**: `Get greetings doc from Elasticsearch my-docs index.`  
* **ES|QL**:

        FROM my-docs | WHERE filename == "greetings.md"

4. In Elastic Agent Builder, create an **agent** with the following values:  
* **Agent ID**: `helloworld_agent`
* **Custom Instructions**:

        If the prompt contains greeting text like "Hi" or "Hello" then respond with only the Basic Hello text from your documents.

        If the prompt contains the text “Hello World” then respond with only the Hello World text from your documents.

        In all other cases where the prompt does not contain greeting words, then respond with only the Not Greeting text from your documents.

* **Display Name**: `HelloWorld Agent` 
* **Display Description**: `An agent that responds to greetings.`

   

## Clone the example app

1. Open a terminal and clone the Search Labs source code repository which contains the Elastic Agent Builder A2A App example. Run the following command to clone the example app:

        git clone https://github.com/elastic/elasticsearch-labs

3.  `cd` to change directory to the example code located in the `supporting-blog-content/agent-builder-a2a-agent-framework` subdirectory.
 
        cd elasticsearch-labs/supporting-blog-content/agent-builder-a2a-agent-framework

## Set up the environment variables

1. Set up the environment variables with values copied from your Elastic project. 
   1. Make a copy of the file `env.example` and name the new file `.env ` 
   2. Edit the `.env` file to set the values of the environment variables to use the values copied from your Elastic project. 
   * Replace <YOUR-ELASTIC-AGENT-BUILDER-URL\>  
      1. In your Elastic project, go to the Elastic Agent Builder - Tools page. Click the **MCP Server** dropdown at the top of the Tools page. Select **Copy MCP Server URL.**   
      2. Add the **MCP Server URL** value to the `.env` file. 
         * Find where the placeholder text “**<YOUR-ELASTIC-AGENT-BUILDER-URL\>**” appears and paste in the copied **MCP Server URL** to replace the placeholder text. Now edit the pasted **MCP Server URL**. Delete the text “mcp” at the end of the URL and replace it with the text “a2a”.  The edited URL should look something like this

            `https://example-project-a123.kb.westus2.azure.elastic.cloud/api/agent_builder/a2a`

   * Replace <YOUR-ELASTIC-API-KEY\>  
      1. In your Elastic project, click **Elasticsearch** in the navigation menu to go to your project’s home page.  
      2. Click **Create API key** to create a new API key.   
      3. After the API key is created, copy the API Key value.  
      4. Add the API Key value to the `.env` file.
         * Find where the placeholder text “**<YOUR-ELASTIC-API-KEY\>**” appears and paste in the copied API Key value to replace the placeholder text.
 
   3. Save the changes to the  `.env` file.

## Running the example app with Python

1.  Create a Python virtual environment by running the following code in the terminal.

        python -m venv .venv
     
2. Activate the Python virtual environment.  
    * If you’re running MacOS, the command to activate the virtual environment is:

            source .venv/bin/activate

    * If you’re on Windows, the command to activate the virtual environment is:
 
            .venv\Scripts\activate

3. Install the Microsoft Agent Framework along with its necessary Python packages by running the following `pip` command:

        pip install -r requirements.txt

4. Run the example app by entering the following command into the terminal:

        python elastic_agent_builder_a2a.py
   
## Running the example app with Docker

1. Run the example app with Docker by entering the following command into the terminal:

        docker compose run elastic-agent-builder-a2a
