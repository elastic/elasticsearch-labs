import asyncio
from dotenv import load_dotenv
from uuid import uuid4
import httpx
import os
import random
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart

DEFAULT_TIMEOUT = 60  # set request timeout to 1 minute


def create_message(*, role: Role = Role.user, text: str, context_id=None) -> Message:
    return Message(
        kind="message",
        role="user",
        parts=[Part(TextPart(kind="text", text=text))],
        message_id=uuid4().hex,
        context_id=context_id,
    )


async def main():
    load_dotenv()
    a2a_agent_host = os.getenv("ES_AGENT_URL")
    a2a_agent_key = os.getenv("ES_API_KEY")
    custom_headers = {"Authorization": f"ApiKey {a2a_agent_key}"}

    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT, headers=custom_headers
    ) as httpx_client:
        # Get agent card
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=a2a_agent_host)
        agent_card = await resolver.get_agent_card(
            relative_card_path="/rps_plus_agent.json"
        )
        # Create client using factory
        config = ClientConfig(
            httpx_client=httpx_client,
            streaming=True,
        )
        factory = ClientFactory(config)
        client = factory.create(agent_card)
        # Use the client to communicate with the agent
        print("\nSending 'start game' message to Elastic A2A agent...")
        random_game_object = random.randint(1, 5)
        msg = create_message(text=f"start with game object {random_game_object}")
        async for event in client.send_message(msg):
            if isinstance(event, Message):
                context_id = event.context_id
                response_complete = event.parts[0].root.text
                # Get agent choice from the first line of the response
                parsed_response = response_complete.split("\n", 1)
                agent_choice = parsed_response[0]
                print(parsed_response[1])
        # User choice sent for game results from the agent
        prompt = input("Your Choice  : ")
        msg = create_message(text=prompt, context_id=context_id)
        async for event in client.send_message(msg):
            if isinstance(event, Message):
                print(f"Agent Choice : {agent_choice}")
                print(event.parts[0].root.text)


if __name__ == "__main__":
    asyncio.run(main())
