# 本地私有化部署的大模型
# import os
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from agent.my_llm import llm
from agent.my_state import CustomState
from agent.tools.tool_demo3 import calculate
from agent.tools.tool_demo6 import runnable_tool
from agent.tools.tool_demo7 import MySearchTool
from agent.tools.tool_demo8 import get_user_info_by_name
from agent.tools.tool_demo9 import greet_user, get_user_name

# load_dotenv(verbose=True)
# LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL")
# llm = ChatOpenAI(
#     model="Qwen3-14B",
#     temperature=0.8,
#     api_key="none",
#     base_url=LOCAL_BASE_URL,
#     extra_body={"chat_template_kwargs": {"enable_thinking": True}}
# )

# def get_weather(city: str) -> str:
#     """Get weather for a given city."""
#     return f"城市：{city}，今天的天气晴朗，气温在28摄氏度！"

# graph = create_react_agent(
#     llm,
#     tools=[get_weather],
#     prompt="你是智能助手！"
# )
# 这是一个网络搜索的工具
search_tool = MySearchTool()

# 提示词模板的函数： 由用户传入内容，组成一个动态的系统提示词
def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
    user_name = config['configurable'].get('user_name', 'zs')
    print(user_name)
    # system_message = f"你是一个智能助手，当前用户的名字是： {user_name}"
    system_message = f"你是一个智能助手，尽可能的调用工具回答用户的问题，当前用户的名字是： {user_name}"
    return [{"role": "system", "content": system_message}] + state['messages']

graph = create_react_agent(
    llm,
    # tools=[calculate, runnable_tool, search_tool, get_user_info_by_name],
    tools=[calculate, runnable_tool, search_tool, get_user_name, greet_user],
    # prompt="你是一个智能助手，尽可能的调用工具回答用户的问题"
    prompt=prompt,
    state_schema=CustomState, # 指定自定义的状态类
)


# 执行智能体，不需要严格的目录结构
# graph.invoke()
# result = graph.stream(
#     input={"messages": [{"role": "user", "content": "计算一下（3+5）x12的结果"}]},
#     stream_mode="messages-tuple"
# )
#
# for chunk in result:
#     print(chunk)