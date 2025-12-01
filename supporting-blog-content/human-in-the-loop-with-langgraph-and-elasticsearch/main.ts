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
import { ingestData, Document } from "./dataIngestion.ts";

const VECTOR_INDEX = "legal-precedents";

const llm = new ChatOpenAI({ model: "gpt-4o-mini" });
const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
});

const esClient = new Client({
  node: process.env.ELASTICSEARCH_ENDPOINT,
  auth: {
    apiKey: process.env.ELASTICSEARCH_API_KEY ?? "",
  },
});

const vectorStore = new ElasticVectorSearch(embeddings, {
  client: esClient,
  indexName: VECTOR_INDEX,
});

// Define the state schema for legal research workflow
const LegalResearchState = Annotation.Root({
  query: Annotation<string>(),
  precedents: Annotation<Document[]>(),
  selectedPrecedent: Annotation<Document | null>(),
  draftAnalysis: Annotation<string>(),
  ambiguityDetected: Annotation<boolean>(),
  userClarification: Annotation<string>(),
  finalAnalysis: Annotation<string>(),
});

// Node 1: Search for relevant legal precedents
async function searchPrecedents(state: typeof LegalResearchState.State) {
  console.log(
    "📚 Searching for relevant legal precedents with query:\n",
    state.query
  );

  const results = await vectorStore.similaritySearch(state.query, 5);
  const precedents = results.map((d) => d as Document);

  console.log(`Found ${precedents.length} relevant precedents:\n`);

  for (let i = 0; i < precedents.length; i++) {
    const p = precedents[i];
    const m = p.metadata;
    console.log(
      `${i + 1}. ${m.title} (${m.caseId})\n` +
        `   Type: ${m.contractType}\n` +
        `   Outcome: ${m.outcome}\n` +
        `   Key reasoning: ${m.reasoning}\n` +
        `   Delay period: ${m.delayPeriod}\n`
    );
  }

  return { precedents };
}

// Node 2: HITL #1 - Request lawyer to select most relevant precedent
function precedentSelection(state: typeof LegalResearchState.State) {
  console.log("\n⚖️  HITL #1: Human input needed\n");
  const userChoice = interrupt({
    question: "👨‍⚖️  Which precedent is most similar to your case? ",
  });
  return { userChoice };
}

// Node 3: Process precedent selection
async function selectPrecedent(state: typeof LegalResearchState.State) {
  const precedents = state.precedents || [];
  const userInput = (state as any).userChoice || "";

  const precedentsList = precedents
    .map((p, i) => {
      const m = p.metadata;
      return `${i + 1}. ${m.caseId}: ${m.title} - ${m.outcome}`;
    })
    .join("\n");

  const structuredLlm = llm.withStructuredOutput({
    name: "precedent_selection",
    schema: {
      type: "object",
      properties: {
        selected_number: {
          type: "number",
          description:
            "The precedent number selected by the lawyer (1-based index)",
          minimum: 1,
          maximum: precedents.length,
        },
      },
      required: ["selected_number"],
    },
  });

  const prompt = `
    The lawyer said: "${userInput}"

    Available precedents:
    ${precedentsList}

    Which precedent number (1-${precedents.length}) matches their selection?
  `;

  const response = await structuredLlm.invoke([
    {
      role: "system",
      content:
        "You are an assistant that interprets lawyer's selection and returns the corresponding precedent number.",
    },
    { role: "user", content: prompt },
  ]);

  const selectedIndex = response.selected_number - 1;
  const selectedPrecedent = precedents[selectedIndex] || precedents[0];

  console.log(`✅ Selected: ${selectedPrecedent.metadata.title}\n`);
  return { selectedPrecedent };
}

// Node 4: Draft initial legal analysis
async function createDraft(state: typeof LegalResearchState.State) {
  console.log("📝 Drafting initial legal analysis...\n");

  const precedent = state.selectedPrecedent;
  if (!precedent) return { draftAnalysis: "" };

  const m = precedent.metadata;

  const structuredLlm = llm.withStructuredOutput({
    name: "draft_analysis",
    schema: {
      type: "object",
      properties: {
        needs_clarification: {
          type: "boolean",
          description:
            "Whether the analysis requires clarification about contract terms or context",
        },
        analysis_text: {
          type: "string",
          description: "The draft legal analysis or the ambiguity explanation",
        },
        missing_information: {
          type: "array",
          items: { type: "string" },
          description:
            "List of specific information needed if clarification is required (empty if no clarification needed)",
        },
      },
      required: ["needs_clarification", "analysis_text", "missing_information"],
    },
  });

  const prompt = `
    Based on this precedent:
    Case: ${m.title}
    Outcome: ${m.outcome}
    Reasoning: ${m.reasoning}
    Key terms: ${m.keyTerms}

    And the lawyer's question: "${state.query}"

    Draft a legal analysis applying this precedent to the question.
    
    If you need more context about the specific contract terms, timeline details, 
    or other critical information to provide accurate analysis, set needs_clarification 
    to true and list what information is missing.
    
    Otherwise, provide the legal analysis directly.
  `;

  const response = await structuredLlm.invoke([
    {
      role: "system",
      content:
        "You are a legal research assistant that analyzes cases and identifies when additional context is needed.",
    },
    { role: "user", content: prompt },
  ]);

  let displayText: string;
  if (response.needs_clarification) {
    const missingInfoList = response.missing_information
      .map((info: string, i: number) => `${i + 1}. ${info}`)
      .join("\n");
    displayText = `AMBIGUITY DETECTED:\n${response.analysis_text}\n\nMissing information:\n${missingInfoList}`;
  } else {
    displayText = `ANALYSIS:\n${response.analysis_text}`;
  }

  console.log(displayText + "\n");

  return {
    draftAnalysis: displayText,
    ambiguityDetected: response.needs_clarification,
  };
}

// Node 5: HITL #2 - Request clarification from lawyer
function requestClarification(state: typeof LegalResearchState.State) {
  console.log("\n⚖️  HITL #2: Additional context needed\n");
  const userClarification = interrupt({
    question: "👨‍⚖️  Please provide clarification about your contract terms:",
  });
  return { userClarification };
}

// Node 6: Generate final analysis with clarification
async function generateFinalAnalysis(state: typeof LegalResearchState.State) {
  console.log("📋 Generating final legal analysis...\n");

  const precedent = state.selectedPrecedent;
  if (!precedent) return { finalAnalysis: "" };

  const m = precedent.metadata;

  const prompt = `
    Original question: "${state.query}"
    
    Selected precedent: ${m.title}
    Outcome: ${m.outcome}
    Reasoning: ${m.reasoning}
    
    Lawyer's clarification: "${state.userClarification}"
    
    Provide a comprehensive legal analysis integrating:
    1. The selected precedent's reasoning
    2. The lawyer's specific contract context
    3. Conditions for breach vs. no breach
    4. Practical recommendations
  `;

  const response = await llm.invoke([
    {
      role: "system",
      content:
        "You are a legal research assistant providing comprehensive analysis.",
    },
    { role: "user", content: prompt },
  ]);

  const finalAnalysis = response.content as string;

  console.log(
    "\n" +
      "=".repeat(80) +
      "\n" +
      "⚖️  FINAL LEGAL ANALYSIS\n" +
      "=".repeat(80) +
      "\n\n" +
      finalAnalysis +
      "\n\n" +
      "=".repeat(80) +
      "\n"
  );

  return { finalAnalysis };
}

// Build the legal research workflow graph
const workflow = new StateGraph(LegalResearchState)
  .addNode("searchPrecedents", searchPrecedents)
  .addNode("precedentSelection", precedentSelection)
  .addNode("selectPrecedent", selectPrecedent)
  .addNode("createDraft", createDraft)
  .addNode("requestClarification", requestClarification)
  .addNode("generateFinalAnalysis", generateFinalAnalysis)
  .addEdge("__start__", "searchPrecedents")
  .addEdge("searchPrecedents", "precedentSelection") // HITL #1
  .addEdge("precedentSelection", "selectPrecedent")
  .addEdge("selectPrecedent", "createDraft")
  .addConditionalEdges(
    "createDraft",
    (state: typeof LegalResearchState.State) => {
      // If ambiguity detected, request clarification (HITL #2)
      if (state.ambiguityDetected) return "needsClarification";
      // Otherwise, generate final analysis
      return "final";
    },
    {
      needsClarification: "requestClarification",
      final: "generateFinalAnalysis",
    }
  )
  .addEdge("requestClarification", "generateFinalAnalysis") // HITL #2
  .addEdge("generateFinalAnalysis", "__end__");

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
  await ingestData();

  // Compile workflow
  const app = workflow.compile({ checkpointer: new MemorySaver() });
  const config = { configurable: { thread_id: "hitl-circular-thread" } };

  await saveGraphImage(app);

  // Execute workflow
  const legalQuestion =
    "Does a pattern of repeated delays constitute breach even if each individual delay is minor?";

  console.log(`⚖️  LEGAL QUESTION: "${legalQuestion}"\n`);

  let currentState = await app.invoke({ query: legalQuestion }, config);

  // Handle all interruptions in a loop
  while ((currentState as any).__interrupt__?.length > 0) {
    console.log("\n💭 APPLICATION PAUSED WAITING FOR USER INPUT...");

    const interruptQuestion = (currentState as any).__interrupt__[0]?.value
      ?.question;
    const userChoice = await getUserInput(
      interruptQuestion || "👤 YOUR CHOICE: "
    );

    currentState = await app.invoke(
      new Command({ resume: userChoice }),
      config
    );
  }
}

// Run main function
await main();
