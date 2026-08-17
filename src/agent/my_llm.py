
from langchain_openai import ChatOpenAI

from agent.env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LOCAL_BASE_URL, OPENAI_API_KEY, OPENAI_BASE_URL

# 本地vllm 私有化部署的大模型： 采用--tool-call-parser == hermes
# 流式输出的时候，会有错误
# llm = ChatOpenAI(
#     model="Qwen3-14B",
#     temperature=0.8,
#     api_key="none",
#     base_url=LOCAL_BASE_URL,
#     extra_body={"chat_template_kwargs": {"enable_thinking": True}}
# )

# 本地sglang 本地私有化部署的大模型： 采用--tool-call-parser == qwen25
# llm = ChatOpenAI(
#     model="Qwen3-14B",
#     temperature=0.8,
#     api_key="none",
#     base_url="http://i-2.gpushare.com:42124/v1",
#     extra_body={"chat_template_kwargs": {"enable_thinking": True}}
# )

# llm = ChatOpenAI(
#     model="deepseek-reasoner",
#     temperature=0.8,
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
#     model_kwargs={"response_format": {"type": "json_object"}},
# )

# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0.8,
#     api_key=OPENAI_API_KEY,
#     base_url=OPENAI_BASE_URL,
# )

# llm = ChatOpenAI(
#     model="claude-3-7-sonnet-20250219",
#     temperature=0.8,
#     api_key=OPENAI_API_KEY,
#     base_url=OPENAI_BASE_URL,
# )

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    temperature=0.8,
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


# 多模态大模型
# multiModal_llm = ChatOpenAI( 
#     model="Qwen2.5-Omni-3B",
#     api_key='xx',
#     base_url=LOCAL_BASE_URL,
# )


multiModal_llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0.8,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

if __name__ == "__main__":
    messages = [
        ("system", "你是一个智能助手，帮助用户解决问题。"),
        ("human", "请介绍一下什么是深度学习？"),
    ]

    resp = multiModal_llm.invoke(messages)
    print(resp)
