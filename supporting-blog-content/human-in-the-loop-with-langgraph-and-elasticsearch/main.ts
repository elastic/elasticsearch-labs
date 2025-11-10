import {
  StateGraph,
  Annotation,
  interrupt,
  Command,
  MemorySaver,
} from "@langchain/langgraph";
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { ElasticVectorSearch } from "@langchain/community/vectorstores/elasticsearch";
import { Client } from "@elastic/elasticsearch";
import { writeFileSync } from "node:fs";
import readline from "node:readline";
import { ingestData, Document, DocumentMetadata } from "./dataIngestion.ts";

const VECTOR_INDEX = "flights-offerings";

const llm = new ChatOpenAI({ model: "gpt-4o-mini" });
const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
});

const esClient = new Client({
  node: process.env.ELASTICSEARCH_ENDPOINT!,
  auth: {
    apiKey: process.env.ELASTICSEARCH_API_KEY!,
  },
});

const vectorStore = new ElasticVectorSearch(embeddings, {
  client: esClient,
  indexName: VECTOR_INDEX,
});

// Define the state schema for application workflow
const SupportState = Annotation.Root({
  input: Annotation<string>(),
  candidates: Annotation<Document[]>(),
  userChoice: Annotation<string>(),
  selected: Annotation<Document>(),
  final: Annotation<string>(),
});

// Node 1: Retrieve data from Elasticsearch
async function retrieveFlights(state: typeof SupportState.State) {
  const results = await vectorStore.similaritySearch(state.input, 2);
  const candidates = results.map((d) => d as Document);

  console.log(`📋 Found ${candidates.length} different flights`);
  return { candidates };
}

// Node 2: Evaluate if there are 1 or multiple responses
function evaluateResults(state: typeof SupportState.State) {
  const candidates = state.candidates || [];

  // If there is 1 result, auto-select it
  if (candidates.length === 1) {
    const metadata = candidates[0].metadata || {};

    return {
      selected: candidates[0],
      final: formatFlightDetails(metadata),
    };
  }

  return { candidates };
}

// Node 3: Request user choice (separate from showing)
function requestUserChoice() {
  const userChoice = interrupt({
    question: `Which flight do you prefer?:`,
  });

  return { userChoice };
}

// Node 4: Disambiguate user choice and provide final answer
async function disambiguateAndAnswer(state: typeof SupportState.State) {
  const candidates = state.candidates || [];
  const userInput = state.userChoice || "";

  const prompt = `
    Based on the user's response: "${userInput}"

    These are the available flights:
    ${candidates
      .map(
        (d, i) =>
          `${i}. ${d.metadata?.title} - ${d.metadata?.to_city} (${d.metadata?.airport_code}) - ${d.metadata?.airline} - $${d.metadata?.price} - ${d.metadata?.time_approx}`
      )
      .join("\n")}

      Which flight is the user selecting? Respond ONLY with the flight number (1, 2, or 3).
  `;

  const llmResponse = await llm.invoke([
    {
      role: "system",
      content:
        "You are an assistant that interprets user selection. Respond ONLY with the selected flight number.",
    },
    { role: "user", content: prompt },
  ]);

  const selectedNumber = Number.parseInt(llmResponse.content as string, 10); // Convert to zero-based index
  const selectedFlight = candidates[selectedNumber] ?? candidates[0]; // Fallback to first option

  return {
    selected: selectedFlight,
    final: formatFlightDetails(selectedFlight.metadata),
  };
}

// Node 5: Show results only
function showResults(state: typeof SupportState.State) {
  const candidates = state.candidates || [];
  const formattedOptions = candidates
    .map((d: Document, index: number) => {
      const m = d.metadata || {};

      return `${index + 1}. ${m.title} - ${m.to_city} - ${m.airport_name}(${
        m.airport_code
      }) airport - ${m.airline} - $${m.price} - ${m.time_approx}`;
    })
    .join("\n");

  console.log(`\n📋 Flights found:\n${formattedOptions}\n`);

  return state;
}

// Helper function to format flight details
function formatFlightDetails(metadata: DocumentMetadata): string {
  return `Selected flight: ${metadata.title} - ${metadata.airline}
    From: ${metadata.from_city} (${
    metadata.from_city?.slice(0, 3).toUpperCase() || "N/A"
  })
    To: ${metadata.to_city} (${metadata.airport_code})
    Airport: ${metadata.airport_name}
    Price: $${metadata.price}
    Duration: ${metadata.time_approx}
    Date: ${metadata.date}`;
}

// Build the graph
const workflow = new StateGraph(SupportState)
  .addNode("retrieveFlights", retrieveFlights)
  .addNode("evaluateResults", evaluateResults)
  .addNode("showResults", showResults)
  .addNode("requestUserChoice", requestUserChoice)
  .addNode("disambiguateAndAnswer", disambiguateAndAnswer)
  .addEdge("__start__", "retrieveFlights")
  .addEdge("retrieveFlights", "evaluateResults")
  .addConditionalEdges(
    "evaluateResults",
    (state: typeof SupportState.State) => {
      if (state.final) return "complete"; // 0 or 1 result
      return "multiple"; // multiple results
    },
    {
      complete: "__end__",
      multiple: "showResults",
    }
  )
  .addEdge("showResults", "requestUserChoice")
  .addEdge("requestUserChoice", "disambiguateAndAnswer")
  .addEdge("disambiguateAndAnswer", "__end__");

/**
 * Get user input from the command line
 * @param question - Question to ask the user
 * @returns User's answer
 */
function getUserInput(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

/**
 * Save workflow graph as PNG image
 * @param app - Compiled workflow application
 */
async function saveGraphImage(app: any): Promise<void> {
  try {
    const graph = app.getGraph();
    const graphImage = await graph.drawMermaidPng();
    const graphArrayBuffer = await graphImage.arrayBuffer();

    const filePath = "./workflow_graph.png";
    writeFileSync(filePath, new Uint8Array(graphArrayBuffer));
    console.log(`📊 Workflow graph saved as: ${filePath}`);
  } catch (error) {
    console.log("⚠️  Could not save graph image:", (error as Error).message);
  }
}

/**
 * Main execution function
 */
async function main() {
  // Ingest data
  await ingestData();

  // Compile workflow
  const app = workflow.compile({ checkpointer: new MemorySaver() });
  const config = { configurable: { thread_id: "hitl-thread" } };

  // Save graph image
  await saveGraphImage(app);

  // Execute workflow
  const question = "Flights to Tokyo"; // User query
  console.log(`🔍 SEARCHING USER QUESTION: "${question}"\n`);

  let currentState = await app.invoke({ input: question }, config);

  // Handle interruption
  if ((currentState as any).__interrupt__?.length > 0) {
    console.log("\n💭 APPLICATION PAUSED WAITING FOR USER INPUT...");
    const userChoice = await getUserInput("👤 CHOICE ONE OPTION: ");

    currentState = await app.invoke(
      new Command({ resume: userChoice }),
      config
    );
  }

  console.log("\n✅ Final result: \n", currentState.final);
}

// Run main function
await main();
