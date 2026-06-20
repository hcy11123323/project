"""
Example 05: MCP Client -- Connecting to the Server Programmatically

Demonstrates:
- Starting the MCP server as a subprocess
- Connecting to it via stdio transport
- Calling MCP tools (ping, browser_launch, run_script, etc.)
- Receiving structured responses

Prerequisites:
    - The project must be installed or on PYTHONPATH
    - Playwright browsers must be installed

Usage:
    # First, start the server in another terminal:
    agentic-playwright-mcp serve --transport sse --port 8000

    # Then run this example:
    python examples/05_mcp_client.py

    # Or run the self-contained stdio version:
    python examples/05_mcp_client.py --stdio
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def run_stdio_client():
    """Connect to the MCP server via stdio (launches server as subprocess)."""
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    print("--- MCP stdio Client ---\n")

    # Server parameters: launch the server as a subprocess
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.server"],
        cwd=str(Path(__file__).resolve().parent.parent),
    )

    print("[1] Starting MCP server subprocess...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            print("[2] Initializing session...")
            await session.initialize()
            print("    Session initialized.\n")

            # List available tools
            print("[3] Listing available tools...")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"    - {tool.name}: {tool.description[:60]}...")

            # Call ping
            print("\n[4] Calling ping...")
            result = await session.call_tool("ping")
            print(f"    Response: {result.content[0].text}")

            # Call browser_launch
            print("\n[5] Calling browser_launch...")
            result = await session.call_tool("browser_launch")
            print(f"    Response: {result.content[0].text}")

            # Call run_script
            print("\n[6] Calling run_script...")
            script = """
goto("https://example.com")
print(f"Title: {get_title()}")
print(f"URL: {get_url()}")
screenshot("examples/output/mcp_client_screenshot.png")
"""
            result = await session.call_tool("run_script", arguments={"code": script})
            print(f"    Response:\n    {result.content[0].text}")

            # Call browse_skills
            print("\n[7] Calling browse_skills...")
            result = await session.call_tool("browse_skills", arguments={"query": "搜索"})
            print(f"    Response:\n    {result.content[0].text}")

    print("\n--- Client session ended ---")


async def run_sse_client(host: str = "localhost", port: int = 8000):
    """Connect to the MCP server via SSE transport."""
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client

    print("--- MCP SSE Client ---\n")
    print(f"Connecting to http://{host}:{port}/sse...")

    async with sse_client(f"http://{host}:{port}/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected!\n")

            # List tools
            tools = await session.list_tools()
            print(f"Available tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"  - {tool.name}")

            # Ping
            result = await session.call_tool("ping")
            print(f"\nping -> {result.content[0].text}")

    print("\n--- Client session ended ---")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="MCP Client Example")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Use stdio transport (launches server as subprocess)",
    )
    parser.add_argument("--host", default="localhost", help="SSE server host")
    parser.add_argument("--port", type=int, default=8000, help="SSE server port")
    args = parser.parse_args()

    print("=== Example 05: MCP Client ===\n")

    if args.stdio:
        asyncio.run(run_stdio_client())
    else:
        print("To use SSE transport, first start the server:")
        print("  agentic-playwright-mcp serve --transport sse --port 8000")
        print()
        print("Then run:")
        print("  python examples/05_mcp_client.py --stdio")
        print("  # or")
        print(f"  python examples/05_mcp_client.py --host {args.host} --port {args.port}")
        print()
        print("Running stdio mode instead (self-contained)...\n")
        asyncio.run(run_stdio_client())


if __name__ == "__main__":
    main()
