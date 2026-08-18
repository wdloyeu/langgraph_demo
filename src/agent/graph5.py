import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent.env_utils import ZHIPU_API_KEY
from agent.my_llm import llm


zhipuai_mcp_server_config = {
    "url": (
        "https://open.bigmodel.cn/api/mcp/web_search/sse"
        "?Authorization=" + ZHIPU_API_KEY
    ),
    "transport": "sse",
}


mcp_client = MultiServerMCPClient(
    {
        "zhipuai_mcp": zhipuai_mcp_server_config,
    }
)


class State(MessagesState):
    pass


async def create_graph():

    tools = await mcp_client.get_tools()

    print(f"加载 MCP Tools 数量: {len(tools)}")

    builder = StateGraph(State)

    llm_with_tools = llm.bind_tools(tools)

    async def chatbot(state: State):
        response = await llm_with_tools.ainvoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }

    builder.add_node(
        "chatbot",
        chatbot
    )

    tool_node = ToolNode(tools)

    builder.add_node(
        "tools",
        tool_node
    )

    builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge(
        "tools",
        "chatbot"
    )

    builder.add_edge(
        START,
        "chatbot"
    )

    graph = builder.compile(
        interrupt_before=["tools"]
    )

    return graph


graph = asyncio.run(create_graph())