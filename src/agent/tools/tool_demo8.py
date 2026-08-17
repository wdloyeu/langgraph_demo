from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


# @tool(return_direct=True)
@tool
def get_user_info_by_name(config: RunnableConfig) -> float:
    """获取用户的所有信息，包括：性别，年龄等"""
    user_name = config["configurable"].get("user_name", "zs")
    print(f"调用工具，传入的用户名是：{user_name}")
    # 模拟查询数据库
    return {"username": user_name, "sex": "男", "age": 18}

# print(calculate.name)
# print(calculate.description)
# print(calculate.args)
# print(calculate.args_schema.model_json_schema())
# print(calculate.return_direct)
# print(calculate.invoke({'a': 40, 'b': 2, 'operation': 'multiply'}))
