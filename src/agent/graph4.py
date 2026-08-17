import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent.env_utils import ZHIPU_API_KEY
from agent.my_llm import llm

# 外网上公开MCP服务器的连接配置
zhipuai_mcp_server_config = {
    "url": "https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization="+ZHIPU_API_KEY,
    "transport": "sse",
}

chart_mcp_server_config = {
    "url": "https://mcp.api-inference.modelscope.net/4d0abb8d1a7048/sse",
    "transport": "sse",
}

# MCP 的客户端
mcp_client = MultiServerMCPClient(
    {
        "chart_mcp": chart_mcp_server_config,
        # "my12306_mcp": my12306_mcp_server_config,
        "zhipuai_mcp": zhipuai_mcp_server_config,
    }
)

class State(MessagesState):
    pass

async def create_graph():
    tools = await mcp_client.get_tools() # 30个以上的工具，全部来自MCP服务端

    builder = StateGraph(State)

    llm_with_tools = llm.bind_tools(tools)

    async def chatbot(state: State):
        return {'messages': [ await llm_with_tools.ainvoke(state["messages"])]}

    builder.add_node('chatbot', chatbot)
    # tool_node = BasicToolsNode(tools)
    tool_node = ToolNode(tools)
    builder.add_node('tools', tool_node)

    builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        # route_tools_func,
    {"tools": "tools", END: END}
    )
    builder.add_edge('tools', 'chatbot')
    builder.add_edge(START, 'chatbot')
    graph = builder.compile()
    return graph

graph = asyncio.run(create_graph())
