# Elastic Agent Builder A2A Example App : RTG+ (Rock Paper Scissors +) 

**Getting started with Agent Builder and A2A using Strands Agents SDK**

This is an example Python console app that demonstrates how to connect and utilize an [Elastic Agent Builder](https://www.elastic.co/elasticsearch/agent-builder) agent via the Agent2Agent (A2A) Protocol orchestrated with the [Strands Agents SDK](https://strandsagents.com).

## Prerequisites

1. An Elasticsearch project/deployment running in [Elastic Cloud](https://cloud.elastic.co/registration?utm_source=github&utm_content=elasticsearch-labs-example-apps). 
   * Requires Elasticsearch serverless project (or for hosted deployments at least Elasticsearch version 9.2.0).
2. A text editor or an integrated development environment (IDE) like [Visual Studio Code](https://code.visualstudio.com/download) running on your local computer.  
3. [Python version 3.10 or greater](https://www.python.org/downloads/) installed on your local computer.

## Set up your Elasticsearch project

1. Create an index named `game-docs` in your Elasticsearch project by running the following command in Elastic Developer Tools:

        PUT /game-docs
        {
            "mappings": {
                "properties": {
                    "title": { "type": "text" },
                    "content": { 
                        "type": "text"
                    },
                    "filename": { "type": "keyword" },
                    "last_modified": { "type": "date" }
                }
            }
        }
2. Insert a document into your index named `RPS+.md` by running the following command in Elastic Developer Tools:

        PUT /game-docs/_doc/rps+-md
        {
            "title": "Rock Paper Scissors +",
            "content": "
        # Game Name
        RPS+

        # Starting Prompt
        Let's play RPS+ !
        ---
        What do you choose?

        # Game Objects
        1. Rock 🪨 👊
        2. Paper 📜 🖐
        3. Scissors ✄ ✌️
        4. Light ☼ 👍
        5. Dark Energy ☄ 🫱

        # Judgement of Victory
        * Rock beats Scissors
          * because rocks break scissors
        * Paper beats Rock
          * because paper covers rock
        * Scissors beat Paper
          * because scissors cut paper
        * Rock beats Light
          * because you can build a rock structure to block out light
        * Paper beats Light
          * because knowledge stored in files and paper books helps us understand light
        * Light beats Dark Energy
          * because light enables humans to lighten up and laugh in the face of dark energy as it causes the eventual heat death of the universe
        * Light beats Scissors
          * because light is needed to use scissors safely
        * Dark Energy beats Rock
          * because dark energy rocks more than rocks. It rocks rocks and everything else in its expansion of the universe
        * Dark Energy beats Paper
          * because humans, with their knowledge stored in files and paper books, can't explain dark energy 
        * Scissors beat Dark Energy
          * because a human running with scissors is darker than dark energy

        # Invalid Input
        I was hoping for an worthy opponent
          - but alas it appears that time has past
          - but alas there's little time for your todo list when [todo:fix this] is so vast 

        # Cancel Game
        The future belongs to the bold. Goodbye..

        ",
            "filename": "RPS+.md",
            "last_modified": "2025-11-25T12:00:00Z"
        }

3. In Elastic Agent Builder, create a **tool** with the following values:  
* **Type**: `ES|QL`  
* **Tool ID**: `example.get_game_docs` 
* **Description**: `Get RPS+ doc from Elasticsearch game-docs index.`  
* **ES|QL**:

        FROM game-docs | WHERE filename == "RPS+.md"

1. In Elastic Agent Builder, create an **agent** with the following values:  
* **Agent ID**: `rps_plus_agent`
* **Custom Instructions**:

        When prompted, if the prompt contains an integer, then select the corresponding numbered item in the list of "Game Objects" from your documents. Otherwise select a random game object. This is your chosen game object for a single round of the game.

        # General Game Rules
        * 2 players
            - the user: the person playing the game
            - you: the agent playing the game and serving as the game master
        * Each player chooses a game object which will be compared and cause them to tie, win or lose.

        # Start the game
        1. This is the way each new game always starts. You make the first line of your response only the name of your chosen game object. 

        2. The remainder of your response should be the "Starting Prompt" text from your documents and generate a list of "Game Objects" for the person playing the game to choose a game object from.  

        # End of Game: The game ends in one of the following three outcomes:
        3. Invalid Input: If the player responds with an invalid game object choice, respond with variations of the "Invalid Input" text from your documents and then end the game.

        4. Tie: The game ends in a tie if the user chooses the same game object as your game object choice.

        5. Win or Lose: The game winner is decided based on the "Judgement of Victory" conditions from your documents. Compare the user's game object choice and your game object choice and determine who chose the winning game object.

        # Game conclusion
        Respond with a declaration of the winner of the game by outputting the corresponding text in the "Judgement of Victory" section of your documents.

* **Display Name**: `RPS+ Agent` 
* **Display Description**: `An agent that plays the game RPS+`

   

## Clone the example app

1. Open a terminal and clone the Search Labs source code repository which contains the Elastic Agent Builder A2A App example: RPS+. Run the following command to clone the example app:

        git clone https://github.com/elastic/elasticsearch-labs

3.  `cd` to change directory to the example code located in the `supporting-blog-content/agent-builder-a2a-strands-agents` subdirectory.
 
        cd elasticsearch-labs/supporting-blog-content/agent-builder-a2a-strands-agents

## Set up the environment variables

1. Set up the environment variables with values copied from your Elastic project. 
   1. Make a copy of the file `env.example` and name the new file `.env ` 
   2. Edit the `.env` file to set the values of the environment variables to use the values copied from your Elastic project. 
   * Replace <YOUR-ELASTIC-AGENT-BUILDER-URL\>  
      1. In your Elastic project, go to the Elastic Agent Builder - Tools page. Click the **MCP Server** dropdown at the top of the Tools page. Select **Copy MCP Server URL.**   
      2. Add the **MCP Server URL** value to the `.env` file. 
         * Find where the placeholder text “**<YOUR-ELASTIC-AGENT-BUILDER-URL\>**” appears and paste in the copied **MCP Server URL** to replace the placeholder text. Now edit the pasted **MCP Server URL**. Delete the text “mcp” at the end of the URL and replace it with the text “a2a”.  The edited URL should look something like this

            `https://rps-game-project-12345a.kb.us-east-1.aws.elastic.cloud/api/agent_builder/a2a`

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

3. Install the [Strands Agents SDK](https://strandsagents.com) along with its necessary Python packages by running the following `pip` command:

        pip install -r requirements.txt

4. Run the example app by entering the following command into the terminal:

        python elastic_agent_builder_a2a_rps+.py
   
## Running the example app with Docker

1. Run the example app with Docker by entering the following command into the terminal:

        docker compose run elastic-agent-builder-a2a-strands-agents
