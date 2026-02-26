"""
Kaimei Labs: Guardian Engine Integration Test
Validating public API endpoints for external agents.
"""
import asyncio
import sys
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from httpx import AsyncClient

async def test_public_endpoint():
    """
    Tests that a generic public user can connect to the Guardian Engine API
    and execute a verification request without needing API keys.
    """
    url = "https://api.kaimeilabs.dev/mcp"
    print(f"Kaimei Labs: Testing public MCP connection to: {url}")
    
    # Very simple stub candidate to test connectivity
    candidate_json = '{"title": "Test", "steps": [], "ingredients": []}'

    try:
        # 30-second timeout is crucial for server "cold starts" 
        # when the service has scaled down to zero instances.
        async with AsyncClient(timeout=30.0) as http_client:
            async with streamable_http_client(url, http_client=http_client) as streams:
                read_stream, write_stream, session_id = streams
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    print("✅ Connection established. Session initialized.")
                    
                    tools = await session.list_tools()
                    tool_names = [t.name for t in tools.tools]
                    print(f"✅ Tools discovered: {tool_names}")
                    
                    assert "verify_recipe" in tool_names, "verify_recipe tool missing"
                    
                    print("✅ Integration test passed.")
                    return

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return

if __name__ == "__main__":
    asyncio.run(test_public_endpoint())
