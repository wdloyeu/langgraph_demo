import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from agent.env_utils import ZHIPU_API_KEY
from agent.my_llm import llm

# Python MCP 服务器端的连接配置
python_mcp_server_config = {
    # "url": "http://127.0.0.1:8080/sse",
    # "transport": "sse",
    "url": "http://127.0.0.1:8080/streamable",
    "transport": "streamable_http",
}

#  Java MCP 服务端的连接配置
java_mcp_server_config = {
    # "url": "http://127.0.0.1:8086/sse",
    # "transport": "sse",
    "url": "http://127.0.0.1:8086/streamable",
    "transport": "streamable_http",
}

# 外网上公开MCP服务器的连接配置
zhipuai_mcp_server_config = {
    "url": "https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization="+ZHIPU_API_KEY,
    "transport": "sse",
}

# MCP 的客户端
mcp_client = MultiServerMCPClient(
    {
        # "python_mcp": python_mcp_server_config,
        # "java_mcp": java_mcp_server_config,
        "zhipuai_mcp": zhipuai_mcp_server_config,
    }
)

async def create_agent():
    """必须是异步函数中"""
    mcp_tools = await mcp_client.get_tools()
    print(mcp_tools)
    # p = await mcp_client.get_prompt(server_name="python_mcp", prompt_name="ask_about_topic", arguments={"topic": "深度学习"})
    # print(p)
    #
    # data = await mcp_client.get_resources(server_name="python_mcp", uris="resource://config")
    # print(data)
    # print(data[0])
    # print(data[0].data) # json数据

    return create_react_agent(
        llm,
        tools=mcp_tools,
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    )

agent = asyncio.run(create_agent())