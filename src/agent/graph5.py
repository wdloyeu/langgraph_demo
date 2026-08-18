import os

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


# ============================================================
# Environment
# ============================================================

TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_BASE_URL = os.environ["OPENAI_BASE_URL"]


# ============================================================
# LLM
# ============================================================

llm = ChatOpenAI(
    model=os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini",
    ),
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)


# ============================================================
# MCP Client
# ============================================================

mcp_client = MultiServerMCPClient(
    {
        "tavily": {
            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={TAVILY_API_KEY}"
            ),
            "transport": "streamable_http",
        }
    }
)


# ============================================================
# Graph
# ============================================================

async def build_graph():

    tools = await mcp_client.get_tools()

    print("Loaded MCP tools:")

    for tool in tools:
        print(
            f"  {tool.name}: "
            f"{getattr(tool, 'description', '')[:100]}"
        )

    return create_react_agent(
        model=llm,
        tools=tools,
    )


# ============================================================
# LangGraph API
# ============================================================

import asyncio

graph = asyncio.run(build_graph())