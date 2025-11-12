# Elastic Agent Builder A2A App 

**Getting started with Agent Builder and A2A using Microsoft Agent Framework**

This is a example Python console app that demonstrates how to connect and utilize an [Elastic Agent Builder](https://www.elastic.co/elasticsearch/agent-builder) agent via the Agent2Agent (A2A) Protocol orchestrated with the [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview).

## Prerequisites

1. An Elasticsearch deployment running in [Elastic Cloud](https://cloud.elastic.co/registration?utm_source=github&utm_content=elasticsearch-labs-example-apps). 
   * Requires Elasticsearch Serverless (or for hosted deployments at least Elasticsearch version 9.2.0).
2. An integrated development environment (IDE)  like [Visual Studio Code](https://code.visualstudio.com/download) running on your local computer.  
3. [Python version 3.10 or greater](https://www.python.org/downloads/) installed on your local computer.

## Setup your Elasticsearch deployment

1. Create an index named `my-docs` in your Elasticsearch deployment by running the following command in Elastic Developer Tools:

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
* **Description**: `Get greetings doc from Elasticsearch my\docs index.`  
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

   

## Running the example app

1. Open Visual Studio Code and open a new terminal within the Visual Studio Code editor. 
2. In the open terminal, clone the Search Labs source code repository which contains the Elastic Agent Builder A2A App example.

        git clone https://github.com/elastic/elasticsearch-labs

3.  `cd` to change directory to the example code located in the `example-apps/agent-builder-a2a-agent-framework` subdirectory.
 
        cd elasticsearch-labs/example-apps/agent-builder-a2a-agent-framework

4. Replace placeholder values in `elastic_agent_builder_a2a.py` with values copied from your Elastic deployment.   
   1. Open the file `elastic_agent_builder_a2a.py` in the Visual Studio editor.  
   2. Replace <YOUR-ELASTIC-AGENT-BUILDER-URL\>  
      1. In your Elastic deployment, go to the Elastic Agent Builder - Tools page. Click the **MCP Server** dropdown at the top of the Tools page. Select **Copy MCP Server URL.**   
      2. In Visual Studio add the **MCP Server URL** value to the `elastic-agent-builder-a2a.py` file. 
         * Find where the placeholder text “**\<YOUR-ELASTIC-AGENT-BUILDER-URL\>**” appears and paste in the copied **MCP Server URL** to replace the placeholder text. Now edit the pasted **MCP Server URL**. Delete the text “mcp” at the end of the URL and replace it with the text “a2a”.  The edited URL should look something like this

            `https://example-project-a123.kb.westus2.azure.elastic.cloud/api/agent_builder/a2a`

   3. Replace \<YOUR-ELASTIC-API-KEY\>  
      1. In your Elastic deployment, click **Elasticsearch** in the navigation menu to go to your deployment’s home page.  
      2. Click **Create API key** to create a new API key.   
      3. After the API key is created, copy the API Key value.  
      4. In Visual Studio add the API Key value to the `elastic-agent-builder-a2a.pys` file.
         * Find where the placeholder text “**\<YOUR-ELASTIC-API-KEY\>**” appears and paste in the copied API Key value to replace the placeholder text.

   4. Confirm the **relative_card_path** is set correctly in the `elastic-agent-builder-a2a.py` file by finding the code line that starts with the text “agent_card”. Confirm that the **relative_card_path** matches the Agent ID you specified when you created the agent in Elastic Agent Builder. If your Agent ID is “helloworld_agent” then the **relative_card_path** should be set to `/helloworld_agent.json`   
   5. Save the `elastic_agent_builder_a2a.py` file in the Visual Studio editor.

5.  Create a Python virtual environment by running the following code in the Visual Studio Code terminal.

        python \-m venv .venv
     
6. Activate the Python virtual environment.  
    * If you’re running MacOS, the command to activate the virtual environment is:

            source .venv/bin/activate

    * If you’re on Windows, the command to activate the virtual environment is:
 
            .venv\Scripts\activate

7. Install the Microsoft Agent Framework with the following `pip` command:

        pip install agent-framework

8. Run the example code by entering the following command into the terminal:

        python elastic-agent-builder-a2a.py
   
## Running the example test

1. Setup the environment variables.  
   1. Make a copy of the file `env.example` and name the new file `.env ` 
   2. Edit the `.env` file to replace the placeholder text with actual values from your Elastic deployment. See instructions on where to get these values in the [Running the example app](#running-the-example-app) section of this `README.md` file.  
        * Replace **YOUR-ELASTIC-AGENT-BUILDER-URL** 
        * Replace **YOUR-ELASTIC-API-KEY**
2. Run the test directly with Python.

        python test_elastic_agent_builder_a2a.py

3. Run the test with Docker.

        docker compose up
