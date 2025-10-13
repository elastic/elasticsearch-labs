import fs from "node:fs/promises";
import { Client } from "@elastic/elasticsearch";
import { z } from "zod";
import dotenv from "dotenv";

dotenv.config();

const INDEX_NAME: string = "startups-index";
const INVESTMENT_FOCUSED_TEMPLATE = "investment-focused-template";
const MARKET_FOCUSED_TEMPLATE = "market-focused-template";
const ELASTICSEARCH_ENDPOINT: string = process.env.ELASTICSEARCH_ENDPOINT ?? "";
const ELASTICSEARCH_API_KEY: string = process.env.ELASTICSEARCH_API_KEY ?? "";

const esClient = new Client({
  node: ELASTICSEARCH_ENDPOINT,
  auth: {
    apiKey: ELASTICSEARCH_API_KEY,
  },
});

const StartupDocumentSchema = z.object({
  description: z.string(),
  semantic_field: z.string(),
  company_name: z.string(),
  industry: z.string(),
  location: z.string(),
  funding_stage: z.string(),
  funding_amount: z.number(),
  lead_investor: z.string(),
  monthly_revenue: z.number(),
  business_model: z.string(),
});

type StartupDocumentType = z.infer<typeof StartupDocumentSchema>;

async function loadDataset(path: string): Promise<StartupDocumentType[]> {
  const raw = await fs.readFile(path, "utf-8");
  const data = JSON.parse(raw);

  return data;
}

async function createIndex() {
  const indexExists = await esClient.indices.exists({ index: INDEX_NAME });

  if (indexExists) {
    console.log("✅ Index already exists.");
    return;
  }

  await esClient.indices.create({
    index: INDEX_NAME,
    mappings: {
      properties: {
        description: {
          type: "text",
          copy_to: "semantic_field",
        },
        company_name: {
          type: "keyword",
          copy_to: "semantic_field",
        },
        industry: {
          type: "keyword",
          copy_to: "semantic_field",
        },
        location: {
          type: "keyword",
          copy_to: "semantic_field",
        },
        funding_stage: {
          type: "keyword",
          copy_to: "semantic_field",
        },
        funding_amount: { type: "long" },
        lead_investor: {
          type: "keyword",
          copy_to: "semantic_field",
        },
        monthly_revenue: { type: "long" },
        business_model: {
          type: "keyword",
          copy_to: "semantic_field",
        },
        semantic_field: { type: "semantic_text" },
      },
    },
  });

  console.log("✅ Index created successfully!");
}

async function ingestDocuments() {
  const indexCount = await esClient.count({ index: INDEX_NAME });
  const documentCount = indexCount.count;

  if (documentCount == 0) {
    const datasetPath = "./dataset.json";
    const documents = await loadDataset(datasetPath);

    console.log("Ingesting documents...");

    try {
      const body = documents.flatMap((doc) => [
        { index: { _index: INDEX_NAME } },
        doc,
      ]);

      await esClient.bulk({ body });

      console.log("✅ Documents ingested successfully!");
    } catch (error: any) {
      console.error("❌ Error during ingestion:", error.message);
    }
  }
}

// Register RRF hybrid search templates in Elasticsearch
async function createSearchTemplates() {
  try {
    await esClient.putScript({
      id: INVESTMENT_FOCUSED_TEMPLATE,
      script: {
        lang: "mustache",
        source: `{
          "size": 5,
          "retriever": {
            "rrf": {
              "retrievers": [
                {
                  "standard": {
                    "query": {
                      "semantic": {
                        "field": "semantic_field",
                        "query": "{{query_text}}"
                      }
                    }
                  }
                },
                {
                  "standard": {
                    "query": {
                      "bool": {
                        "filter": [
                          {"terms": {"funding_stage": {{#join}}{{#toJson}}funding_stage{{/toJson}}{{/join}}}},
                          {"range": {"funding_amount": {"gte": {{funding_amount_gte}}{{#funding_amount_lte}},"lte": {{funding_amount_lte}}{{/funding_amount_lte}}}}},
                          {"terms": {"lead_investor": {{#join}}{{#toJson}}lead_investor{{/toJson}}{{/join}}}},
                          {"range": {"monthly_revenue": {"gte": {{monthly_revenue_gte}}{{#monthly_revenue_lte}},"lte": {{monthly_revenue_lte}}{{/monthly_revenue_lte}}}}}
                        ]
                      }
                    }
                  }
                }
              ],
              "rank_window_size": 100,
              "rank_constant": 20
            }
          }
        }`,
      },
    });

    console.log("✅ Investment-focused template created successfully!");

    await esClient.putScript({
      id: MARKET_FOCUSED_TEMPLATE,
      script: {
        lang: "mustache",
        source: `{
          "size": 5,
          "retriever": {
            "rrf": {
              "retrievers": [
                {
                  "standard": {
                    "query": {
                      "semantic": {
                        "field": "semantic_field",
                        "query": "{{query_text}}"
                      }
                    }
                  }
                },
                {
                  "standard": {
                    "query": {
                      "bool": {
                        "filter": [
                          {"terms": {"industry": {{#join}}{{#toJson}}industry{{/toJson}}{{/join}}}},
                          {"terms": {"location": {{#join}}{{#toJson}}location{{/toJson}}{{/join}}}},
                          {"terms": {"business_model": {{#join}}{{#toJson}}business_model{{/toJson}}{{/join}}}}
                        ]
                      }
                    }
                  }
                }
              ],
              "rank_window_size": 50,
              "rank_constant": 10
            }
          }
        }`,
      },
    });

    console.log("✅ Market-focused template created successfully!");
  } catch (error) {
    console.error("❌ Error creating RRF templates:", error);
  }
}

export {
  createIndex,
  ingestDocuments,
  createSearchTemplates,
  esClient,
  INDEX_NAME,
  INVESTMENT_FOCUSED_TEMPLATE,
  MARKET_FOCUSED_TEMPLATE,
};
