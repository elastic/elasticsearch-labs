import asyncio
from dotenv import load_dotenv
import httpx
import os
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent


async def main():
    load_dotenv()
    a2a_agent_host = os.getenv("ES_AGENT_URL")
    a2a_agent_key = os.getenv("ES_API_KEY")

    print(f"Connection to Elastic A2A agent at: {a2a_agent_host}")

    custom_headers = {"Authorization": f"ApiKey {a2a_agent_key}"}

    async with httpx.AsyncClient(timeout=60.0, headers=custom_headers) as http_client:
        # Resolve the A2A Agent Card
        resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_agent_host)
        agent_card = await resolver.get_agent_card(
            relative_card_path="/helloworld_agent.json"
        )
        print(f"Found Agent: {agent_card.name} - {agent_card.description}")

        # Use the Agent
        agent = A2AAgent(
            name=agent_card.name,
            description=agent_card.description,
            agent_card=agent_card,
            url=a2a_agent_host,
            http_client=http_client,
        )
        prompt = input("Enter Greeting >>> ")
        print("\nSending message to Elastic A2A agent...")
        response = await agent.run(prompt)
        print("\nAgent Response:")
        for message in response.messages:
            print(message.text)


if __name__ == "__main__":
    asyncio.run(main())
