from typing import List, Dict, AsyncGenerator
import aiohttp
import json
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(service="ollama")

class OllamaService:
    def __init__(self):
        logger.info("Initializing Ollama Service")
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL
        self.reason_model = settings.OLLAMA_REASON_MODEL

    async def generate_stream(self, messages: List[Dict], model: str = "deepseek-r1:32b") -> AsyncGenerator[str, None]:
        try:

            # 优先使用配置中的 OLLAMA_CHAT_MODEL，其次使用传入的 model
            model = self.chat_model or model
            logger.info(f"Generating response with model: {model}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                     json={
                        "model": self.chat_model,
                        "messages": messages,
                        "stream": True,
                        "keep_alive": -1,  # 保持连接
                        "options": {
                            "temperature": 0.7,   # Deepseek r1 模型建议 temperature 为 0.6 ~ 0.8
                        }
                    }
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                json_line = json.loads(line)
                                if content := json_line.get("message", {}).get("content"):
                                    content = json.dumps(content, ensure_ascii=False)
                                    yield f"data: {content}\n\n"
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error: {str(e)}", exc_info=True)
                                continue

        except Exception as e:
            logger.error(f"Error in generate_stream: {str(e)}", exc_info=True)
            error_msg = json.dumps(f"生成回复时出错: {str(e)}", ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    async def generate(self, messages: List[Dict]) -> str:
        """非流式生成回复"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.chat_model,
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