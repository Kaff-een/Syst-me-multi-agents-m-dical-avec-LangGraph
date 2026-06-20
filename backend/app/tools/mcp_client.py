import asyncio
import os
import sys
from langchain_core.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.normpath(
    os.path.join(_THIS_DIR, "..", "..", "..", "mcp_server", "server.py")
)

server_params = StdioServerParameters(
    command=sys.executable,   # utilise le même interpréteur Python que le backend
    args=[SERVER_SCRIPT],
)


async def _call_mcp_tool(tool_name: str, arguments: dict) -> str:
    if not os.path.exists(SERVER_SCRIPT):
        return f"Erreur MCP : serveur introuvable à {SERVER_SCRIPT}. Vérifiez le chemin."

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)

            texts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(texts) if texts else str(result)


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()


@tool
def fetch_mcp_protocol(symptom: str) -> str:
    """
    Interroge le serveur MCP (mcp_server/server.py) pour récupérer
    le protocole médical standard correspondant à un symptôme donné.
    """
    try:
        return _run_async(_call_mcp_tool("get_standard_protocol", {"symptom": symptom}))
    except Exception as e:
        return f"Erreur MCP : impossible de contacter le serveur de protocoles ({e})."