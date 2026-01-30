
import os
import asyncio
from composio_core import Composio
from composio_openai import OpenAIProvider # Assuming OpenAIProvider for now, will adjust if needed

async def get_composio_tools(user_id: str):
    # Ensure API key is loaded
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        print("Error: COMPOSIO_API_KEY not found in environment variables.")
        return

    # Initialize Composio
    # Using OpenAIProvider as an example, as it's a common integration.
    # We can switch providers if needed based on Composio's docs and your setup.
    composio = Composio(provider=OpenAIProvider(), api_key=api_key)

    # Create an isolated session for the user
    # Composio recommends short-lived sessions, so creating one per "interaction"
    # or conversation thread is a good practice.
    print(f"Creating Composio session for user_id: {user_id}...")
    session = await composio.tool_router.create(
        user_id=user_id,
        toolkits=["*"],  # Request all available toolkits
        manage_connections=True
    )
    print(f"Session created with ID: {session.session_id}")
    print(f"MCP URL: {session.mcp.url}")

    # Fetch and list the tools available in this session
    print("\nFetching tools from Composio marketplace...")
    tools = await session.tools()

    if not tools:
        print("No tools found in Composio marketplace for this user_id.")
        return

    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name} (Slug: {tool.slug})")
        # Optionally print more details like description, parameters
        # print(f"    Description: {tool.description}")
        # print(f"    Parameters: {tool.parameters}")
    
    print("\nComposio integration successful! Tools are now available.")
    # In a real agent, you would pass these `tools` to your LLM.

if __name__ == "__main__":
    # Use Ben's Telegram ID as the Composio user ID for isolation
    ben_user_id = "1455611839"
    asyncio.run(get_composio_tools(ben_user_id))
