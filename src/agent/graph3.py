import asyncio
import json
from typing import Dict, Any, List
import traceback

from langchain_core.messages import ToolMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph

from agent.env_utils import ZHIPU_API_KEY
from agent.my_llm import llm

# 外网上公开MCP服务器的连接配置
zhipuai_mcp_server_config = {
    "url": "https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization="+ZHIPU_API_KEY,
    "transport": "sse",
}

# {
#   "mcpServers": {
#     "Railway-Real-Time-MCP-Server": {
#       "type": "sse",
#       "url": "https://mcp.api-inference.modelscope.net/a449f2753ae049/sse"
#     }
#   }
# }
# my12306_mcp_server_config = {
#     "url": "https://mcp.api-inference.modelscope.net/a449f2753ae049/sse",
#     "transport": "sse",
# }

# {
#   "mcpServers": {
#     "mcp-server-chart": {
#       "type": "sse",
#       "url": "https://mcp-.api-inference.modelscope.net/sse"
#     }
#   }
# }https://mcp.api-inference.modelscope.net/4d0abb8d1a7048/sse
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

class BasicToolsNode:
    """
    异步工具节点，用于并发执行AIMessage中请求的工具调用

    功能:
    1. 接收工具列表并建立名称索引
    2. 并发执行消息中的工具调用请求
    3. 自动处理同步/异步工具适配
    """

    def __init__(self, tools: list):
        """
        初始化工具节点

        Args:
            tools: 工具列表，每个工具需包含 name 属性
        """
        # 所有工具名字 -> 工具对象
        self.tools_by_name = {
            tool.name: tool
            for tool in tools
        }

    async def __call__(
        self,
        state: Dict[str, Any]
    ) -> Dict[str, List[ToolMessage]]:
        """
        异步调用入口

        Args:
            state: 输入字典，需包含 "messages" 字段

        Returns:
            包含 ToolMessage 列表的字典

        Raises:
            ValueError: 当输入无效时抛出
        """

        # 1. 输入验证
        if not (messages := state.get("messages")):
            raise ValueError("输入数据中未找到消息内容")

        message: AIMessage = messages[-1]  # 取最新消息：AIMessage

        # 2. 并发执行工具调用
        outputs = await self._execute_tool_calls(
            message.tool_calls
        )

        return {
            "messages": outputs
        }

    async def _execute_tool_calls(
        self,
        tool_calls: List[Dict]
    ) -> List[ToolMessage]:
        """
        执行实际工具调用

        Args:
            tool_calls: 工具调用请求列表

        Returns:
            ToolMessage 结果列表
        """

        async def _invoke_tool(
            tool_call: Dict
        ) -> ToolMessage:
            """
            执行单个工具调用

            Args:
                tool_call: 工具调用请求字典，
                           需包含 name / args / id 字段

            Returns:
                封装的 ToolMessage

            Raises:
                KeyError: 工具未注册时抛出
                RuntimeError: 工具调用失败时抛出
            """

            try:
                # 3. 异步调用工具
                tool = self.tools_by_name.get(
                    tool_call["name"]
                )

                # 验证工具是否在之前的工具集合中
                if not tool:
                    raise KeyError(
                        f"未注册的工具: {tool_call['name']}"
                    )

                if hasattr(tool, "ainvoke"):
                    # 优先使用异步方法
                    tool_result = await tool.ainvoke(
                        tool_call["args"]
                    )

                else:
                    # 同步工具通过线程池转异步
                    loop = asyncio.get_running_loop()

                    tool_result = await loop.run_in_executor(
                        None,
                        tool.invoke,
                        tool_call["args"]
                    )

                # 4. 构造 ToolMessage
                return ToolMessage(
                    content=json.dumps(
                        tool_result,
                        ensure_ascii=False
                    ),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )

            except Exception as e:
                raise RuntimeError(
                    f"工具调用失败: {tool_call['name']}"
                ) from e

        try:
            # 5. 并发执行所有工具调用
            #
            # asyncio.gather() 是 Python 异步编程中用于
            # 并发调度多个协程的核心函数，其核心行为包括:
            #
            # 并发执行:
            # 所有传入的协程会被同时调度到事件循环中，
            # 通过非阻塞 I/O 实现并行处理。
            #
            # 结果收集:
            # 按输入顺序返回所有协程的结果，
            # 与任务完成顺序无关。
            #
            # 异常处理:
            # 默认情况下，任一任务失败会立即取消其他任务并抛出异常。
            # 若设置 return_exceptions=True，
            # 则异常会作为结果返回。

            return await asyncio.gather(
                *[
                    _invoke_tool(tool_call)
                    for tool_call in tool_calls
                ]
            )

        except Exception as e:
            raise RuntimeError(
                "并发执行工具时发生错误"
            ) from e



class BasicToolsNode3:

    def __init__(self, tools: list):
        # tool.name -> tool对象
        self.tools_by_name = {
            tool.name: tool
            for tool in tools
        }

        print("=" * 80)
        print(f"已注册工具数量: {len(self.tools_by_name)}")

        for i, tool_name in enumerate(
            self.tools_by_name.keys(),
            start=1
        ):
            print(f"{i:03d}. {tool_name}")

        print("=" * 80)

    async def __call__(
        self,
        state: Dict[str, Any]
    ) -> Dict[str, List[ToolMessage]]:

        messages = state.get("messages")

        if not messages:
            raise ValueError(
                "输入数据中未找到 messages"
            )

        message = messages[-1]

        if not isinstance(message, AIMessage):
            raise TypeError(
                f"tools 节点期望 AIMessage，"
                f"实际类型: {type(message).__name__}"
            )

        tool_calls = getattr(
            message,
            "tool_calls",
            None
        ) or []

        if not tool_calls:
            print("⚠️ 当前 AIMessage 没有 tool_calls")
            return {
                "messages": []
            }

        print("=" * 80)
        print(f"本轮工具调用数量: {len(tool_calls)}")

        for i, tool_call in enumerate(
            tool_calls,
            start=1
        ):
            print(
                f"[ToolCall {i}] "
                f"name={tool_call.get('name')} "
                f"id={tool_call.get('id')} "
                f"args={tool_call.get('args')}"
            )

        print("=" * 80)

        outputs = await self._execute_tool_calls(
            tool_calls
        )

        return {
            "messages": outputs
        }

    async def _invoke_tool(
        self,
        tool_call: Dict[str, Any]
    ) -> ToolMessage:

        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")

        if not tool_name:
            raise ValueError(
                f"tool_call 缺少 name: {tool_call}"
            )

        tool = self.tools_by_name.get(tool_name)

        if tool is None:
            raise KeyError(
                f"未注册的工具: {tool_name}"
            )

        print(
            f"🚀 开始执行工具: {tool_name}"
        )
        print(
            f"   tool_call_id: {tool_call_id}"
        )
        print(
            f"   args: {json.dumps(tool_args, ensure_ascii=False, default=str)}"
        )

        try:

            # 优先异步
            if hasattr(tool, "ainvoke"):

                result = await tool.ainvoke(
                    tool_args
                )

            else:

                # 同步工具丢到线程池
                loop = asyncio.get_running_loop()

                result = await loop.run_in_executor(
                    None,
                    tool.invoke,
                    tool_args
                )

            print(
                f"✅ 工具执行成功: {tool_name}"
            )

            print(
                f"   result type: {type(result).__name__}"
            )

            # 统一转换 ToolMessage content
            if isinstance(result, str):

                content = result

            else:

                try:
                    content = json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str
                    )

                except Exception:
                    content = str(result)

            return ToolMessage(
                content=content,
                name=tool_name,
                tool_call_id=tool_call_id
            )

        except Exception as e:

            print("=" * 80)
            print(
                f"❌ 工具执行失败: {tool_name}"
            )
            print(
                f"   tool_call_id: {tool_call_id}"
            )
            print(
                f"   args: {json.dumps(tool_args, ensure_ascii=False, default=str)}"
            )
            print(
                f"   exception type: {type(e).__name__}"
            )
            print(
                f"   exception: {e}"
            )

            traceback.print_exc()

            print("=" * 80)

            # 注意：
            # 不要这里直接 raise，
            # 否则 gather 会导致整个 tools 节点失败。
            return ToolMessage(
                content=json.dumps(
                    {
                        "success": False,
                        "tool": tool_name,
                        "error_type": type(e).__name__,
                        "error": str(e),
                    },
                    ensure_ascii=False
                ),
                name=tool_name,
                tool_call_id=tool_call_id
            )

    async def _execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[ToolMessage]:

        if not tool_calls:
            return []

        # 并发执行
        results = await asyncio.gather(
            *[
                self._invoke_tool(
                    tool_call
                )
                for tool_call in tool_calls
            ],
            return_exceptions=True
        )

        outputs: List[ToolMessage] = []

        for tool_call, result in zip(
            tool_calls,
            results
        ):

            # 理论上 _invoke_tool 已经自己捕获异常
            # 这里再做一道保险
            if isinstance(
                result,
                Exception
            ):

                tool_name = tool_call.get(
                    "name",
                    "unknown"
                )

                print(
                    f"❌ gather 捕获异常: "
                    f"{tool_name}: "
                    f"{type(result).__name__}: "
                    f"{result}"
                )

                outputs.append(
                    ToolMessage(
                        content=json.dumps(
                            {
                                "success": False,
                                "tool": tool_name,
                                "error_type": type(result).__name__,
                                "error": str(result),
                            },
                            ensure_ascii=False
                        ),
                        name=tool_name,
                        tool_call_id=tool_call.get(
                            "id"
                        )
                    )
                )

            else:
                outputs.append(result)

        return outputs

class State(MessagesState):
    pass

def route_tools_func(state: State):
    """
    动态路由函数，如果从大模型输出后的AIMessage，中包含有工具调用的请求(指令)，就进入到tooLs节点， 否则则结束
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

async def create_graph():
    tools = await mcp_client.get_tools() # 30个以上的工具，全部来自MCP服务端

    builder = StateGraph(State)

    llm_with_tools = llm.bind_tools(tools)

    async def chatbot(state: State):
        return {'messages': [ await llm_with_tools.ainvoke(state["messages"])]}

    builder.add_node('chatbot', chatbot)
    tool_node = BasicToolsNode(tools)
    builder.add_node('tools', tool_node)

    builder.add_conditional_edges(
        "chatbot",
        route_tools_func,
    {"tools": "tools", END: END}
    )
    builder.add_edge('tools', 'chatbot')
    builder.add_edge(START, 'chatbot')
    graph = builder.compile()
    return graph

graph = asyncio.run(create_graph())
