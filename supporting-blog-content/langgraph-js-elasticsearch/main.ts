import { writeFileSync } from "node:fs";
import { StateGraph, Annotation, START, END } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";
import {
  esClient,
  ingestDocuments,
  createSearchTemplates,
  INDEX_NAME,
  INVESTMENT_FOCUSED_TEMPLATE,
  MARKET_FOCUSED_TEMPLATE,
  createIndex,
} from "./elasticsearchSetup.js";

const llm = new ChatOpenAI({ model: "gpt-4o-mini" });

// Define state for workflow
const VCState = Annotation.Root({
  input: Annotation<string>(), // User's natural language query
  searchStrategy: Annotation<string>(), // Search strategy chosen by LLM
  searchParams: Annotation<any>(), // Prepared search parameters
  results: Annotation<any[]>(), // Search results
  final: Annotation<string>(), // Final formatted response
});

// Extract available filter values from Elasticsearch using aggregations
async function getAvailableFilters() {
  try {
    const response = await esClient.search({
      index: INDEX_NAME,
      size: 0,
      aggs: {
        industries: {
          terms: { field: "industry", size: 100 },
        },
        locations: {
          terms: { field: "location", size: 100 },
        },
        funding_stages: {
          terms: { field: "funding_stage", size: 20 },
        },
        business_models: {
          terms: { field: "business_model", size: 10 },
        },
        lead_investors: {
          terms: { field: "lead_investor", size: 100 },
        },
        funding_amount_stats: {
          stats: { field: "funding_amount" },
        },
      },
    });

    console.log(
      "✅ Available filters:",
      JSON.stringify(response.aggregations, null, 2)
    );

    return response.aggregations;
  } catch (error) {
    console.error("❌ Error getting available filters:", error);

    return {};
  }
}

// Node 1: Decide search strategy using LLM
async function decideSearchStrategy(state: typeof VCState.State) {
  // Zod schema for specialized search strategy decision
  const SearchDecisionSchema = z.object({
    search_type: z
      .enum(["investment_focused", "market_focused"])
      .describe("Type of specialized search strategy to use"),
    reasoning: z
      .string()
      .describe("Brief explanation of why this search strategy was chosen"),
  });

  const decisionLLM = llm.withStructuredOutput(SearchDecisionSchema);

  // Get dynamic filters from Elasticsearch
  const availableFilters = await getAvailableFilters();

  const prompt = `Query: "${state.input}"
    Available filters: ${JSON.stringify(availableFilters, null, 2)}

    Choose between two specialized search strategies:
    
    - investment_focused: For queries about funding stages, funding amounts, monthly revenue, lead investors, financial performance
    
    - market_focused: For queries about industries, locations, business models, market segments, geographic markets
    
    Analyze the query intent and choose the most appropriate strategy.
  `;

  try {
    const result = await decisionLLM.invoke(prompt);
    console.log(
      `🤔 Search strategy: ${result.search_type} - ${result.reasoning}`
    );

    return {
      searchStrategy: result.search_type,
    };
  } catch (error: any) {
    console.error("❌ Error in decideSearchStrategy:", error.message);
    return {
      searchStrategy: "investment_focused",
    };
  }
}

// Extract all possible filter values from user input
async function extractFilterValues(input: string) {
  const FilterValuesSchema = z.object({
    // Investment-focused filters
    funding_stage: z
      .array(z.string())
      .default([])
      .describe("Funding stage values mentioned in query"),
    funding_amount_gte: z
      .number()
      .default(0)
      .describe("Minimum funding amount in USD"),
    funding_amount_lte: z
      .number()
      .default(100000000)
      .describe("Maximum funding amount in USD"),
    lead_investor: z
      .array(z.string())
      .default([])
      .describe("Lead investor values mentioned in query"),
    monthly_revenue_gte: z
      .number()
      .default(0)
      .describe("Minimum monthly revenue in USD"),
    monthly_revenue_lte: z
      .number()
      .default(10000000)
      .describe("Maximum monthly revenue in USD"),
    industry: z
      .array(z.string())
      .default([])
      .describe("Industry values mentioned in query"),
    location: z
      .array(z.string())
      .default([])
      .describe("Location values mentioned in query"),
    business_model: z
      .array(z.string())
      .default([])
      .describe("Business model values mentioned in query"),
  });

  const extractorLLM = llm.withStructuredOutput(FilterValuesSchema);
  const availableFilters = await getAvailableFilters();

  const extractPrompt = `Extract ALL relevant filter values from: "${input}"
    Available options: ${JSON.stringify(availableFilters, null, 2)}
    Extract only values explicitly mentioned in the query. Leave fields empty if not mentioned.`;

  return await extractorLLM.invoke(extractPrompt);
}

// Node 2A: Prepare Investment-Focused Search Parameters
async function prepareInvestmentSearch(state: typeof VCState.State) {
  console.log(
    "💰 Preparing INVESTMENT-FOCUSED search parameters with financial emphasis..."
  );

  try {
    // Extract all filter values from input
    const values = await extractFilterValues(state.input);

    let searchParams: any = {
      template_id: INVESTMENT_FOCUSED_TEMPLATE,
      query_text: state.input,
      ...values,
    };

    return { searchParams };
  } catch (error) {
    console.error("❌ Error preparing investment-focused params:", error);
    return {
      searchParams: {},
    };
  }
}

// Node 2B: Prepare Market-Focused Search Parameters
async function prepareMarketSearch(state: typeof VCState.State) {
  console.log(
    "🔍 Preparing MARKET-FOCUSED search parameters with market emphasis..."
  );

  try {
    // Extract all filter values from input
    const values = await extractFilterValues(state.input);

    let searchParams: any = {
      template_id: MARKET_FOCUSED_TEMPLATE,
      query_text: state.input,
      ...values,
    };

    return { searchParams };
  } catch (error) {
    console.error("❌ Error preparing market-focused params:", error);
    return {};
  }
}

// Node 3: Execute Search
async function executeSearch(state: typeof VCState.State) {
  const { searchParams } = state;

  try {
    // getting formed query from template for debugging
    const renderedTemplate = await esClient.renderSearchTemplate({
      id: searchParams.template_id,
      params: searchParams,
    });

    console.log(
      "📋 Complete query:",
      JSON.stringify(renderedTemplate.template_output, null, 2)
    );

    const results = await esClient.searchTemplate({
      index: INDEX_NAME,
      id: searchParams.template_id,
      params: searchParams,
    });

    return {
      results: results.hits.hits.map((hit: any) => hit._source),
    };
  } catch (error: any) {
    console.error(`❌ ${state.searchParams.search_type} search error:`, error);
    return { results: [] };
  }
}

// Node 4: Visualize results
async function visualizeResults(state: typeof VCState.State) {
  const results = state.results || [];

  let formattedResults = `🎯 Found ${results.length} startups matching your criteria:\n\n`;

  results.forEach((startup: any, index: number) => {
    formattedResults += `${index + 1}. **${startup.company_name}**\n`;
    formattedResults += `   📍 ${startup.location} | 🏢 ${startup.industry} | 💼 ${startup.business_model}\n`;
    formattedResults += `   💰 ${startup.funding_stage} - $${(
      startup.funding_amount / 1000000
    ).toFixed(1)}M\n`;
    formattedResults += `    $${(startup.monthly_revenue / 1000).toFixed(
      0
    )}K MRR\n`;
    formattedResults += `   🏦 Lead: ${startup.lead_investor}\n`;
    formattedResults += `   📝 ${startup.description}\n\n`;
  });

  return {
    final: formattedResults,
  };
}

async function saveGraphImage(app: any): Promise<void> {
  try {
    const drawableGraph = app.getGraph();
    const image = await drawableGraph.drawMermaidPng();
    const arrayBuffer = await image.arrayBuffer();

    const filePath = "./workflow_graph.png";
    writeFileSync(filePath, new Uint8Array(arrayBuffer));
    console.log(`📊 Workflow graph saved as: ${filePath}`);
  } catch (error: any) {
    console.log("⚠️  Could not save graph image:", error.message);
  }
}

async function main() {
  await createIndex();
  await createSearchTemplates();
  await ingestDocuments();

  // Create the workflow graph with shared state
  const workflow = new StateGraph(VCState)
    // Register nodes - these are the processing functions
    .addNode("decideStrategy", decideSearchStrategy)
    .addNode("prepareInvestment", prepareInvestmentSearch)
    .addNode("prepareMarket", prepareMarketSearch)
    .addNode("executeSearch", executeSearch)
    .addNode("visualizeResults", visualizeResults)
    // Define execution flow with conditional branching
    .addEdge(START, "decideStrategy") // Start with strategy decision
    .addConditionalEdges(
      "decideStrategy",
      (state: typeof VCState.State) => state.searchStrategy, // Conditional function
      {
        investment_focused: "prepareInvestment", // If investment focused -> RRF template preparation
        market_focused: "prepareMarket", // If market focused -> dynamic query preparation
      }
    )
    .addEdge("prepareInvestment", "executeSearch") // Investment prep -> execute
    .addEdge("prepareMarket", "executeSearch") // Market prep -> execute
    .addEdge("executeSearch", "visualizeResults") // Execute -> visualize
    .addEdge("visualizeResults", END); // End workflow

  const app = workflow.compile();

  await saveGraphImage(app);

  // Investment-focused query (emphasizes funding, revenue, financial metrics)
  const query =
    "Find startups with Series A or Series B funding between $8M-$25M and monthly revenue above $500K";

  // Market-focused query (emphasizes industry, geography, market positioning)
  // const query =
  //   "Find fintech and healthcare startups in San Francisco, New York, or Boston";
  // console.log("🔍 Query:", query);

  const marketResult = await app.invoke({ input: query });
  console.log(marketResult.final);
}

main().catch(console.error);
