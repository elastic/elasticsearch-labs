Example of AI Conversational Search using Elasticsearch, OpenAI and Vercel. 

# Load the data

Export the following environment variables: 
- ELASTICSEARCH_URL: You can find it in your Elasticsearch deployment
- ES_API_KEY: Your Elasticsearch API Key

Run the script ingest.py: `python ingest.py` to index the data. 


# Chat application

## Install dependencies

Go to the folder `chat-example/app` and execute `yarn install` to install the project dependencies. 

## Provide environment variable

Export the following environment variables: 
- ELASTICSEARCH_URL: You can find it in your Elasticsearch deployment
- ES_API_KEY: Your Elasticsearch API Key
- OPENAI_API_KEY: Your OpenAI API Key

## Run the application 

Run the application: `yarn dev` 

Your browser should open directly to the URL: [http://localhost:3000](http://localhost:3000)

## Try it 

Ask the question: "How to get a refund?", the chat will retrieve the relevant information from Elasticsearch and OpenAI will use this to formulate an answer. 


