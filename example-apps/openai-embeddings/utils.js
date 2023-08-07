const { Client } = require('@elastic/elasticsearch')
const { Configuration, OpenAIApi } = require("openai");

console.log(`Connecting to Elastic Cloud: ${process.env.ELASTIC_CLOUD_ID}`);

const elasticsearchClient = new Client({
  cloud: {
    id: process.env.ELASTIC_CLOUD_ID,
  },
  auth: {
    username: process.env.ELASTIC_USERNAME,
    password: process.env.ELASTIC_PASSWORD,
  },
});

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

module.exports = {
  getElasticsearchClient: () => elasticsearchClient,
  getOpenAIClient: () => openai,
  // Global variables
  // Modify these if you want to use a different file, index or model
  FILE: "sample_data/medicare.json",
  INDEX: "openai-integration",
  MODEL: "text-embedding-ada-002",
};
