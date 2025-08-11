import httpx
import asyncio
import json
from typing import List, Dict

MODEL_NAME = "deepseek-r1:1.5b"
BASE_URL = "http://192.168.110.131:11434"

async def test_model_info():
    """获取模型信息"""
    try:
        async with httpx.AsyncClient() as client:
            # 获取所有可用模型
            response = await client.get(f"{BASE_URL}/api/tags")
            print("Available models:", json.dumps(response.json(), indent=2))

            # 获取特定模型信息
            response = await client.post(f"{BASE_URL}/api/show", json={
                "model": MODEL_NAME
            })
            print("\nModel info:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error getting model info: {str(e)}")

async def test_generate():
    """测试生成 API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/api/generate", json={
                "model": MODEL_NAME,
                "prompt": "你好，请介绍一下你自己",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            })
            print("\nGenerate response:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error in generate: {str(e)}")

async def test_stream_generate():
    """测试流式生成"""
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream('POST', f"{BASE_URL}/api/generate", json={
                "model": MODEL_NAME,
                "prompt": "你好，请介绍一下你自己",
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }) as response:
                print("\nStream generate response:")
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if data.get("response"):
                            print(data["response"], end="", flush=True)
                print()  # 打印一个换行
    except Exception as e:
        print(f"Error in stream generate: {str(e)}")

if __name__ == "__main__":
    print(f"Testing Ollama API with model: {MODEL_NAME}")
    
    asyncio.run(test_model_info())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(test_generate())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(test_stream_generate()) 