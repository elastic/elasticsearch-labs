const { Client } = require('@elastic/elasticsearch')
const { OpenAI } = require("openai");

console.log(`Connecting to Elastic URL: ${process.env.ELASTICSEARCH_URL}`);

const elasticsearchClient = new Client({
  node: process.env.ELASTICSEARCH_URL,
  auth: {
    username: process.env.ELASTICSEARCH_USER,
    password: process.env.ELASTICSEARCH_PASSWORD,
  },
});

const openai = new OpenAI();

module.exports = {
  getElasticsearchClient: () => elasticsearchClient,
  getOpenAIClient: () => openai,
  // Global variables
  // Modify these if you want to use a different file, index or model
  FILE: "sample_data/medicare.json",
  INDEX: "openai-integration",
  EMBEDDINGS_MODEL: process.env.EMBEDDINGS_MODEL || "text-embedding-ada-002",
};
