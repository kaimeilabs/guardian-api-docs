"""
Kaimei Labs | Guardian Engine — Python SDK Example
===================================================
Guardian Engine is the symbolic verification layer for neuro-symbolic AI pipelines. It catches recipe
hallucinations before they reach the pan — modelling each recipe as a directed acyclic graph
(DAG) of culinary state transformations, then verifying temperatures, durations, techniques,
and ingredient interactions against curated master recipes from professional kitchens.
LLMs generate, Guardian verifies.

This minimal client demonstrates how to connect to the public Guardian Engine MCP API and
submit a structured JSON recipe for physics-based verification.

Endpoint : https://api.kaimeilabs.dev/mcp
Transport: Streamable HTTP (mcp.client.streamable_http)
"""
import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from httpx import AsyncClient

# Guardian Engine public MCP endpoint (Kaimei Labs hosted)
GUARDIAN_URL = "https://api.kaimeilabs.dev/mcp"

async def verify_my_recipe():
    """
    Connect to the Guardian Engine MCP API and verify an AI-generated recipe.

    This example submits a deliberately flawed Basque Cheesecake recipe — one that an AI
    agent might hallucinate — to illustrate what Guardian catches:
      - Missing required culinary state transformations (e.g. baking before cooling)
      - Incomplete ingredient list (eggs and heavy cream are required for a Basque Cheesecake)
      - Invalid technique sequencing in the DAG (cooling without prior heat application)

    Guardian returns a structured authenticity report with a verification score (0–100%)
    and a breakdown of each failed physics or technique constraint.
    """
    print(f"Connecting to Guardian Engine at {GUARDIAN_URL}...")

    # A deliberately flawed recipe — the kind of hallucination an AI agent might produce.
    # It skips the required baking step and is missing key ingredients (eggs, heavy cream).
    # Guardian will model this as a DAG and flag the broken state transformations.
    my_candidate_recipe = {
        "title": "Agent's Bad Cheesecake",
        "steps": [
            {
                "step_index": "1.0",
                "technique": "mixing",
                "instruction_english": "Mix all ingredients.",
                "intent": "preparation"
            },
            {
                "step_index": "2.0",
                "technique": "cooling",
                "instruction_english": "Put in fridge to set.",
                "intent": "setting"
            }
        ],
        "ingredients": [
            {"name": "cream cheese", "quantity": "1 kg"},
            {"name": "sugar", "quantity": "400g"}
        ]
    }

    try:
        async with AsyncClient(timeout=30.0) as http_client:
            async with streamable_http_client(GUARDIAN_URL, http_client=http_client) as streams:
                read_stream, write_stream, session_id = streams
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    # Call the `verify_recipe` MCP tool with the target dish and candidate JSON.
                    # Use `list_dishes` first if you need the current catalog of supported recipes.
                    print("\nSending recipe for physics verification...")
                    result = await session.call_tool("verify_recipe", arguments={
                        "dish": "basque-cheesecake",
                        "candidate_json": json.dumps(my_candidate_recipe)
                    })

                    # The authenticity report scores the recipe 0–100% and lists each
                    # failed constraint — broken technique sequences, missing ingredients,
                    # incorrect state transformations, and physics violations.
                    print("\n--- Guardian Engine: Authenticity Report ---")
                    for content in result.content:
                        print(content.text)

    except Exception as e:
        print(f"Failed to connect to Guardian Engine: {e}")

if __name__ == "__main__":
    asyncio.run(verify_my_recipe())
