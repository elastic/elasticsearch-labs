import { openai } from '@ai-sdk/openai';
import { convertToCoreMessages, streamText, tool } from 'ai';
const { Client } = require('@elastic/elasticsearch-serverless')
import { z } from 'zod';

const client = new Client({
  node: process.env.ELASTICSEARCH_URL, // serverless project URL
  auth: { apiKey: process.env.ES_API_KEY }, // project API key
})

// add a function findRelevantContent to retrieve relevant content from the knowledge base
async function findRelevantContent(question: string) {
  const body = await client.search({
    size: 3,
    index: 'search-faq',
    body: {
      query: {
        "semantic": {
            "field": "semantic",
            "query": question
          }
      }
    }
  });
  return body.hits.hits.map((hit: any) => ({
    content: hit._source.content
  }));
}

export async function POST(req: Request) {

  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4-turbo'),
    system: `You are a customer service assistant, please be concise in your answer. Check your knowledge base before answering any questions.
    Only respond to questions using information from tool calls.
    if no relevant information is found in the tool calls, respond, "Sorry, I don't know."`,
    messages: convertToCoreMessages(messages),
    tools: {
      getInformation: tool({
        description: `get information from your knowledge base to answer questions.`,
        parameters: z.object({
          question: z.string().describe('the users question'),
        }),
        execute: async ({ question }: { question: string }) => findRelevantContent(question),
      }),
    },
  });

  // Respond with the stream
  return result.toAIStreamResponse();
}
