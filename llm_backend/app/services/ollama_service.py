from typing import List, Dict, AsyncGenerator, Optional
import aiohttp
import json
from app.core.config import settings
from app.core.logger import get_logger
from app.services.redis_semantic_cache import RedisSemanticCache
import time
import asyncio

logger = get_logger(service="ollama")

class OllamaService:
    def __init__(self):
        logger.info("Initializing Ollama Service")
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL
        self.reason_model = settings.OLLAMA_REASON_MODEL

    async def _stream_cached_response(self, response: str, delay: float = 0.05) -> AsyncGenerator[str, None]:
        """模拟流式返回缓存的响应"""
        chunks = [response[i:i + 4] for i in range(0, len(response), 4)]
        for chunk in chunks:
            await asyncio.sleep(delay)  # 50ms延迟
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    async def generate_stream(
        self, 
        messages: List[Dict],
        user_id: Optional[int] = None,
        model: str = "deepseek-r1:32b"
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            # 为每个用户创建独立的缓存实例
            cache = RedisSemanticCache(
                prefix="ollama",
                user_id=user_id,
                max_cache_size=1000
            )
            
            start_time = time.time()
            
            # 检查缓存
            cached_response = await cache.lookup(messages)
            if cached_response:
                response_time = time.time() - start_time
                logger.info(f"Cache hit! Response time: {response_time:.4f} seconds")
                
                # 模拟流式返回
                async for chunk in self._stream_cached_response(cached_response):
                    yield chunk
                return

            # 缓存未命中,调用API
            model = self.chat_model or model
            logger.info(f"Generating response with model: {model}")
            
            full_response = []
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                     json={
                        "model": self.chat_model,
                        "messages": messages,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                json_line = json.loads(line)
                                if content := json_line.get("message", {}).get("content"):
                                    full_response.append(content)
                                    content = json.dumps(content, ensure_ascii=False)
                                    yield f"data: {content}\n\n"
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error: {str(e)}", exc_info=True)
                                continue

            # 完整响应
            complete_response = "".join(full_response)
            
            # 更新缓存
            await cache.update(messages, complete_response)
            
            response_time = time.time() - start_time
            logger.info(f"Cache miss. Response time: {response_time:.4f} seconds")

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