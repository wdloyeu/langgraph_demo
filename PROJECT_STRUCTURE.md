# langgraph_demo 项目结构分析

> 一个基于 [LangGraph](https://github.com/langchain-ai/langgraph) 的智能体项目：
> 注册入口 `langgraph.json` → `src/agent/graph5.py`，通过 MCP 客户端接入智谱 web_search 与 ModelScope 图表服务，
> 同时包含本地 FastMCP 服务器与 9 个自定义工具（demo 用途）。

## 1. 目录结构图（mermaid mindmap）

```mermaid
mindmap
  root((langgraph_demo))
    langgraph.json
    pyproject.toml
    Makefile
    README.md
    LICENSE
    .env
    .gitignore
    uv.lock
    src
      agent
        __init__.py
        env_utils.py
        my_llm.py
        my_state.py
        graph.py
        graph2.py
        graph3.py
        graph4.py
        graph5.py
        graph6.py
        mcp_agent.py
        mcp_agent2.py
        my_agent2.py
        tools
          tool_demo1.py
          tool_demo2.py
          tool_demo3.py
          tool_demo4.py
          tool_demo5.py
          tool_demo6.py
          tool_demo7.py
          tool_demo8.py
          tool_demo9.py
      mcp_server
        __init__.py
        tools_server.py
        tools_server2.py
        start_sse_server.py
        start_streamable_server.py
    tests
      conftest.py
      my_test_sync.py
      my_test_async.py
      unit_tests
        test_configuration.py
      integration_tests
        test_graph.py
    .github
      workflows
        unit-tests.yml
        integration-tests.yml
    static
      studio_ui.png
    .langgraph_api
      checkpoint 与 store 状态文件
    .idea
    .vscode
    agent.egg-info
```

## 2. 模块依赖图（mermaid flowchart）

```mermaid
flowchart LR
  env[".env 密钥"] --> env_utils["env_utils.py"]

  env_utils --> my_llm["my_llm.py<br/>deepseek-v4-flash / gpt-4-turbo"]

  my_llm --> g2["graph2.py"]
  my_llm --> g3["graph3.py"]
  my_llm --> g4["graph4.py"]
  my_llm --> g5["graph5.py"]
  my_llm --> g6["graph6.py"]
  my_llm --> mcpA1["mcp_agent.py"]
  my_llm --> mcpA2["mcp_agent2.py"]
  my_llm --> myA2["my_agent2.py"]
  my_llm --> td3["tools/tool_demo3.py"]
  my_llm --> td6["tools/tool_demo6.py"]

  env_utils --> td7["tools/tool_demo7.py"]
  env_utils --> ms1["mcp_server/tools_server.py"]
  env_utils --> ms2["mcp_server/tools_server2.py"]

  my_state["my_state.py"] --> g1["graph.py"]
  my_state --> td9["tools/tool_demo9.py"]

  td3 --> g1
  td6 --> g1
  td7 --> g1
  td8["tools/tool_demo8.py"] --> g1
  td9 --> g1

  td6 --> myA2
  td7 --> myA2

  g1 --> init["agent/__init__.py"]

  ms1 --> sse["start_sse_server.py"]
  ms2 --> stream["start_streamable_server.py"]
```

## 3. 注册主图 graph5 的运行时架构（mermaid flowchart）

```mermaid
flowchart TD
  START(["START"]) --> chatbot["chatbot 节点<br/>llm.bind_tools(MCP tools)"]

  chatbot --> cond{"tools_condition"}
  cond -->|"需要调用工具"| tools["tools 节点<br/>ToolNode(tools)"]
  cond -->|"无工具调用"| ENDX(["END"])
  tools --> chatbot

  tools -. "interrupt_before=['tools']<br/>人工审批：输入 y 放行 / 输入理由拒绝" .-> human["人类审批<br/>Human-in-the-loop"]

  subgraph mcp["MultiServerMCPClient (graph5.py)"]
    z["zhipuai_mcp<br/>智谱 web_search (SSE)"]
    c["chart_mcp<br/>ModelScope 图表生成 (SSE)"]
  end
  mcp -->|"get_tools() 30+ 个工具"| tools

  mem["MemorySaver checkpointer<br/>thread_id 持久化状态"] -. "读写状态" .- chatbot
  mem -. "读写状态" .- tools
```

## 4. 各文件职责速查

| 文件 | 职责 |
|---|---|
| `langgraph.json` | LangGraph 服务器配置，注册入口 `agent = src/agent/graph5.py:graph` |
| `src/agent/env_utils.py` | 加载 `.env`，暴露 OPENAI / DEEPSEEK / LOCAL / ZHIPU 密钥 |
| `src/agent/my_llm.py` | LLM 工厂：当前用 deepseek-v4-flash，另有大量本地/云端模型配置（注释） |
| `src/agent/my_state.py` | 自定义状态 `CustomState`（继承 AgentState） |
| `src/agent/graph.py` | `create_react_agent` + 本地工具（demo3/6/7/8/9），模板默认图 |
| `src/agent/graph2.py` | 最简单的 StateGraph：LLM + StrOutputParser 链 |
| `src/agent/graph3.py` | MCP 客户端图 + 自研 `BasicToolsNode`（异步并发执行工具） |
| `src/agent/graph4.py` | MCP 客户端图 + 标准 `ToolNode` / `tools_condition` |
| `src/agent/graph5.py` | **注册主图**：MCP + ToolNode + MemorySaver + `interrupt_before` 人工审批循环 |
| `src/agent/graph6.py` | 进阶版：`BasicToolsNode` + `interrupt`/`Command` + MemorySaver |
| `src/agent/mcp_agent.py` | `create_react_agent` 直接接入 MCP 客户端 |
| `src/agent/mcp_agent2.py` | 同上变体 |
| `src/agent/my_agent2.py` | `create_react_agent` + sqlite/PostgresSaver 持久化 + 本地工具 |
| `src/agent/tools/` | 9 个工具 demo：`@tool`、pydantic 参数、LCEL Runnable 工具、BaseTool 搜索工具、注入工具（InjectedState/InjectedToolCallId/Command） |
| `src/mcp_server/tools_server.py` | FastMCP 服务器「老王的MCP」：搜索工具、打招呼、提示模板、资源 |
| `src/mcp_server/tools_server2.py` | FastMCP + JWT 认证（RSAKeyPair / JWTVerifier / AccessToken） |
| `src/mcp_server/start_sse_server.py` | 以 SSE 方式启动 tools_server |
| `src/mcp_server/start_streamable_server.py` | 以 Streamable HTTP 方式启动 tools_server2 |
| `tests/` | 单元/集成测试 + 手写 sync/async 测试 |
| `.github/workflows/` | CI：unit-tests / integration-tests |
| `.langgraph_api/` | `langgraph dev` 运行产生的 checkpoint / store 状态 |

## 5. 发现的问题（建议关注）

- `langgraph.json` 注册的符号是 `src/agent/graph5.py:graph`，但 `graph5.py` 中只有
  `create_graph()` 异步工厂，**没有模块级变量 `graph`**（`graph` 只是 `run_graph()` 内的局部变量），
  `langgraph dev` 加载该图可能会报错。可改为 `graph5.py:create_graph`，或在模块级补一个
  `graph = asyncio.run(create_graph())`。
- `agent/__init__.py` 导出的是 `agent.graph` 中的图，与 `langgraph.json` 注册的 `graph5` 不一致；
  README 描述的入口（graph.py）也与实际注册（graph5.py）不一致。
