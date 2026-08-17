from langgraph_sdk import get_sync_client

# 调用智能体agent发布的API接口
client = get_sync_client(url="http://localhost:2024")

def main():
    for chunk in client.runs.stream(
        None,
        "agent",
        input={
            "messages": [{
                "role": "human",
                "content": "给当前用户一个祝福语" # 告诉我当前用户的年龄？
            }]
        },
        stream_mode="messages-tuple",
        # stream_mode="updates",
        # stream_mode="messages",
        config={"configurable": {"user_name": "user_123"}},
    ):
        # print(f"Receiving new event of type: {chunk.event}...")
        # print(chunk.data)
        if isinstance(chunk.data, list) and 'type' in chunk.data[0] and chunk.data[0]['type'] == 'AIMessageChunk':
            print(chunk.data[0]['content'], end='|')
        # print("\n\n")

if __name__ == '__main__':
    main()