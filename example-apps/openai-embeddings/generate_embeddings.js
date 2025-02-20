const { trace } = require("@opentelemetry/api");
const fs = require("fs");
const {
  getElasticsearchClient,
  getOpenAIClient,
  FILE,
  INDEX,
  EMBEDDINGS_MODEL,
} = require("./utils");

// Initialize clients
const elasticsearchClient = getElasticsearchClient();
const openaiClient = getOpenAIClient();

const tracer = trace.getTracer("openai-embeddings");

async function maybeCreateIndex() {
  // Check if index exists, if not create it
  indexExists = await elasticsearchClient.indices.exists({
    index: INDEX,
  });

  if (!indexExists) {
    console.log(`Creating index ${INDEX}...`);

    await elasticsearchClient.indices.create({
      index: INDEX,
      settings: {
        index: {
          number_of_shards: 1,
          number_of_replicas: 1,
        },
      },
      mappings: {
        properties: {
          url: {
            type: "keyword",
          },
          title: {
            type: "text",
            analyzer: "english",
          },
          content: {
            type: "text",
            analyzer: "english",
          },
          embedding: {
            type: "dense_vector",
            dims: 1536, // must match query vector size
            index: true,
            similarity: "cosine",
          },
        },
      },
    });
  }
}

async function bulkIndexDocs(docs) {
  // Create actions for bulk indexing
  // See https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/api-reference.html#_bulk
  // for details
  const operations = docs.flatMap((doc) => [
    { index: { _id: doc["url"] } },
    doc,
  ]);

  console.log(`Indexing ${docs.length} documents to index ${INDEX}...`);

  await elasticsearchClient.bulk({
    index: INDEX,
    operations,
  });
}

async function generateEmbeddingsWithOpenAI(docs) {
  // Generate OpenAI embeddings from the content of the documents
  // See https://platform.openai.com/docs/api-reference/embeddings for details
  const input = docs.map((doc) => doc["content"]);

  console.log(
    `Calling OpenAI API for ${input.length} embeddings with model ${EMBEDDINGS_MODEL}`
  );

  const result = await openaiClient.embeddings.create({
    model: EMBEDDINGS_MODEL,
    input,
  });

  return result.data.map((data) => data.embedding);
}

async function processFile() {
  console.log(`Reading from file ${FILE}`);

  // Read the JSON documents from the file
  const docsRaw = fs.readFileSync(FILE);
  const docs = JSON.parse(docsRaw);

  console.log(`Processing ${docs.length} documents...`);

  // Split the list of documents into batches of 10
  const BATCH_SIZE = 10;
  for (let i = 0; i < docs.length; i += BATCH_SIZE) {
    const docsBatch = docs.slice(i, i + BATCH_SIZE);

    console.log(`Processing batch of ${docsBatch.length} documents...`);

    // Generate embeddings and add them to the documents
    const embeddings = await generateEmbeddingsWithOpenAI(docsBatch);
    docsBatch.forEach((doc, i) => (doc.embedding = embeddings[i]));

    // Index batch of documents
    await bulkIndexDocs(docsBatch);

    // Uncomment these lines if you're hitting the OpenAI rate limit due to the number of requests
    // console.log("Sleeping for 2 seconds to avoid reaching OpenAI rate limit...")
    // await timer(2000)
  }

  console.log("Processing complete");
}

async function run() {
  return tracer.startActiveSpan("generate", async (span) => {
    try {
      await maybeCreateIndex();
      await processFile();
    } finally {
      span.end();
    }
  });
}

run().catch(console.error);
