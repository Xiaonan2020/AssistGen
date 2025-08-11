from typing import List, Dict, AsyncGenerator
import aiohttp
import json
from app.core.config import settings

class OllamaService:
    def __init__(self, model: str = None):
        self.base_url = settings.OLLAMA_BASE_URL
        # 优先使用传入的 model，其次使用配置中的模型
        self.model = model or settings.OLLAMA_CHAT_MODEL

    async def generate_stream(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "keep_alive": -1,
                        "options": {
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    async for line in response.content:
                        if line:
                            chunk = json.loads(line)
                            if chunk.get("message", {}).get("content"):
                                content = json.dumps(
                                    chunk["message"]["content"], 
                                    ensure_ascii=False
                                )
                                yield f"data: {content}\n\n"

        except Exception as e:
            print(f"Stream generation error: {str(e)}")
            raise

    async def generate(self, messages: List[Dict]) -> str:
        """非流式生成回复"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "keep_alive": -1,
                        "options": {
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    result = await response.json()
                    return result["message"]["content"]

        except Exception as e:
            print(f"Generation error: {str(e)}")
            raise 