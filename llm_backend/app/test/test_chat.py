from openai import OpenAI

# 直接硬编码配置，仅用于测试
API_KEY = "sk-fb7369c51357447d9bfa082b012346d4"
BASE_URL = "https://api.deepseek.com/v1"

def test_sync():
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一位乐于助人的智能小助手"},
            {"role": "user", "content": "你好，请你介绍一下你自己。"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)

def test_stream():
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一位乐于助人的智能小助手"},
            {"role": "user", "content": "你好，请你介绍一下你自己。"},
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

if __name__ == "__main__":
    print("Testing sync chat:")
    test_sync()
    print("\nTesting stream chat:")
    test_stream() 