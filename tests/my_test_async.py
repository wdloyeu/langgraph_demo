from langgraph_sdk import get_client
import asyncio

# 调用智能体agent发布的API接口
client = get_client(url="http://localhost:2024")

async def main():
    async for chunk in client.runs.stream(
        None,
        "agent",
        input={
            "messages": [{
                "role": "human",
                # "content": "今天，北京的天气怎么样？"
                "content": "给当前用户一个祝福语？"
            }]
        },
        config={"configurable": {"user_name": "老王"}}
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("\n\n")

if __name__ == '__main__':
    asyncio.run(main())