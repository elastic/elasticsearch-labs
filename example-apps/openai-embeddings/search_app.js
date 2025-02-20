const express = require("express");
const {
  getElasticsearchClient,
  getOpenAIClient,
  INDEX,
  EMBEDDINGS_MODEL,
} = require("./utils");

// Initialize clients and web app
const elasticsearchClient = getElasticsearchClient();
const openaiClient = getOpenAIClient();
const app = express();

async function generateEmbeddingsWithOpenAI(text) {
  // Generate OpenAI embedding for input text
  console.log(
    `Calling OpenAI API to apply embedding on text "${text}" with model ${EMBEDDINGS_MODEL}`
  );

  const result = await openaiClient.embeddings.create({
    model: EMBEDDINGS_MODEL,
    input: text,
  });

  return result.data[0].embedding;
}

async function runSemanticSearch(query) {
  // Generate OpenAI embedding for query
  const embedding = await generateEmbeddingsWithOpenAI(query);

  // Perform approximate kNN search
  // See https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html for details
  const knn = {
    field: "embedding",
    query_vector: embedding,
    k: 10,
    num_candidates: 100,
  };
  const result = await elasticsearchClient.search({
    index: INDEX,
    knn,
    _source: ["url", "title", "content"],
    size: 10,
  });

  return result;
}

app.set("view engine", "hbs");
app.set("views", "./views");

// Express route handler for /
app.get("/", (_req, res) => {
  res.render("search");
});

// Express route handler for /search
app.get("/search", async (req, res) => {
  const query = req.query.q;

  const searchResult = await runSemanticSearch(query);
  const hits = searchResult.hits.hits.map((hit) => {
    const source = hit._source;

    return {
      _id: hit._id,
      score: hit._score,
      ...source,
    };
  });

  res.render("search", {
    query,
    hits,
  });
});

app.listen(3000, () => {
  console.log("Express app listening on port 3000");
});
