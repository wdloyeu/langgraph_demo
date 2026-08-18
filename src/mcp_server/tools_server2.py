# from fastmcp import FastMCP
# from fastmcp.server.auth.providers.jwt import RSAKeyPair, JWTVerifier
# from zhipuai import ZhipuAI
# from fastmcp.prompts import PromptMessage
# from mcp.types import TextContent
# from fastmcp.server.dependencies import AccessToken, get_access_token
#
# from agent.env_utils import ZHIPU_API_KEY
#
# zhipuai_client = ZhipuAI(api_key=ZHIPU_API_KEY)
#
# # 1、生成RSA密钥对
# key_pair = RSAKeyPair.generate()
#
# # print(key_pair.public_key)
#
# # 2、配置认证提供方
# # auth = BearerAuthProvider(
# #     public_key=key_pair.public_key, # 公钥用于校验签名
# #     issuer="https://www.cn86trading.com", # 令牌签发方标识
# #     audience="my-dev-server" # 服务商的一个标识
# # )
# auth = JWTVerifier(
#     # jwks_uri="https://your-auth-server.com/.well-known/jwks.json",
#     public_key=key_pair.public_key,
#     issuer="https://www.cn86trading.com",
#     audience="my-dev-server",
# )
#
# # 3、服务器，模拟生成一个token。正常是通过用户调用api接口生成token.
# token = key_pair.create_token(
#     subject="dev_user",
#     issuer="https://www.cn86trading.com",
#     audience="my-dev-server",
#     scopes=['cn86trding', 'invoke_tools'], # token中包含的数据
#     expires_in_seconds=3600 # 1小时后过期
# )
# print(token)
#
# server = FastMCP(
#     name="老王的MCP",
#     instructions="老王的Python代码实现MCP服务器",
#     auth=auth, # 用于服务校验token的
# )
#
# @server.tool(name="zhipuai_search")
# def my_search(query: str) -> str:
#     """搜索互联网上的内容，包括实时天气等"""
#     try:
#         print("执行我的Python中的工具，输入的参数为：", query)
#
#         access_token: AccessToken = get_access_token()
#         if access_token:
#             print("<整个token:>", access_token)
#             print(access_token.scopes)
#         else:
#             return "由于没有权限 ，所以不能搜索到任何内容！"
#
#         response = zhipuai_client.web_search.web_search(
#             search_engine="search_pro",
#             search_query=query,
#         )
#         # print(response)
#         if response.search_result:
#             return "\n\n".join([d.content for d in response.search_result])
#         return "没有搜索到任何内容！"
#     except Exception as e:
#         print(e)
#         return "没有搜索到任何内容！"
#
# @server.tool()
# def say_hello(username: str) -> str:
#     """给某个用户打个招呼"""
#     return f"{username}，你好，今天天气不错！"
#
# @server.prompt
# def ask_about_topic(topic: str) -> str:
#     """生成请求解释特定主题的用户消息模板"""
#     return f"能否请您解释一下'{topic}'这个概念？"
#
# # 高级提示模板：返回结构化消息对象
# @server.prompt
# def generate_code_request(language: str, task_description: str) -> PromptMessage:
#     """生成代码编写请求的用户消息模板"""
#     content = f"请用{language}编写一个实现以下功能的函数：{task_description}"
#     return PromptMessage(
#         role="user",
#         content=TextContent(type="text", text=content),
#     )
#
# # 结构化资源： 自动序列化字典为JSON
# # @server.resource("data://config")
# @server.resource("resource://config")
# def get_config() -> dict:
#     """以JSON格式返回应用配置"""
#     return {
#         "theme": "dark", # 界面主题配置
#         "version": "1.2.0", # 当前版本号
#         "features": ["tools", "resources"], # 已启用的功能模块
#     }