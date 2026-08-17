import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from agent.my_llm import llm
test_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJkZXZfdXNlciIsImlzcyI6Imh0dHBzOi8vd3d3LmNuODZ0cmFkaW5nLmNvbSIsImlhdCI6MTc4NjY5MDc0NCwiZXhwIjoxNzg2Njk0MzQ0LCJhdWQiOiJteS1kZXYtc2VydmVyIiwic2NvcGUiOiJjbjg2dHJkaW5nIGludm9rZV90b29scyJ9.bEKIzSG61U9LwZd4QX0cw-5jhxVRVJFKoO5-ILg5fHOXNltMv1P3V5UU6ub3WnEJjnrFinUj8fV-GZexdizbXKc9xmKl5hAzoMQz7OBTOUT2A2tS4usERApQzywa99ip0ia74jqJYZfiPZjmTAmczuiGMps_RN8uNjifyGBUYqxbEIsTcwOxvkTo30SOekf0FJkJGfsHkqXj0wYZdpaAPq3vMQAof1tLNbnyQI5oryGoIchIzudqs1d502pmxtsgmuJQThxb_wzW0jm2NTAAfR48cinU2K-PwFIy0Dfllm9YTgg7gc5LnWQR0q7dIO_DdhpkSW1l6Fv0ANINb9x1Rg"
# Python MCP 服务器端的连接配置
python_mcp_server_config = {
    # "url": "http://127.0.0.1:8080/sse",
    # "transport": "sse",
    "url": "http://127.0.0.1:8080/streamable",
    "transport": "streamable_http",
    "headers": {
        "Authorization": f"Bearer {test_token}",
    }
}

# MCP 的客户端
mcp_client = MultiServerMCPClient(
    {
        "python_mcp": python_mcp_server_config,
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

    # return create_react_agent(
    #     llm,
    #     tools=mcp_tools,
    #     prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    # )
    agent = create_react_agent(
        llm,
        tools=mcp_tools,
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    )
    # 自已写代码调用。不用langgraph dev启动，记住在调用MCP只能用异步调用
    rest = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "今天上海的天气怎么样？"}]}
    )
    print(rest["messages"])
    print(rest["messages"][-1].content)
    # print(rest["messages"][-1]["content"])

# agent = asyncio.run(create_agent())
if __name__ == '__main__':
    asyncio.run(create_agent())