import { config } from "dotenv";
import { Client } from "@elastic/elasticsearch";
import { readFileSync } from "fs";

config();

const INDEX_NAME = "documents";
const ELASTICSEARCH_ENDPOINT =
  process.env.ELASTICSEARCH_ENDPOINT ?? "http://localhost:9200";
const ELASTICSEARCH_API_KEY = process.env.ELASTICSEARCH_API_KEY ?? "";

const client = new Client({
  node: ELASTICSEARCH_ENDPOINT,
  auth: {
    apiKey: ELASTICSEARCH_API_KEY,
  },
});

async function setup() {
  try {
    // Check if index exists
    const exists = await client.indices.exists({ index: INDEX_NAME });

    if (!exists) {
      await client.indices.create({
        index: INDEX_NAME,
        mappings: {
          properties: {
            id: {
              type: "keyword",
            },
            title: {
              type: "text",
              fields: {
                keyword: {
                  type: "keyword",
                },
              },
            },
            content: {
              type: "text",
            },
            tags: {
              type: "keyword",
            },
          },
        },
      });

      console.log(`Index '${INDEX_NAME}' created.`);
    } else {
      console.log(`Index '${INDEX_NAME}' already exists.`);
    }

    // Load dataset
    const DATASET_PATH = "./dataset.json";
    const docs = JSON.parse(readFileSync(DATASET_PATH, "utf-8"));

    const bulkBody = docs.flatMap((doc: any) => [
      { index: { _index: INDEX_NAME, _id: doc.id } },
      doc,
    ]);

    const response = await client.bulk({ refresh: true, body: bulkBody });
    const errors = response.errors
      ? response.items.filter((item: any) => item.index?.error)
      : [];

    console.log(`${docs.length} documents indexed successfully`);

    if (errors.length) {
      console.error("Errors during indexing:", errors);
    }
  } catch (e: any) {
    console.error(
      `Error: ${e.message}, please wait some seconds and try again.`
    );
    process.exit(1);
  }
}

setup().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
