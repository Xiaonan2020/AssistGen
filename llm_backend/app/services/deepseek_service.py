from typing import List, Dict, AsyncGenerator
from openai import AsyncOpenAI
from app.core.config import settings
import json
from app.core.logger import get_logger

logger = get_logger(service="deepseek")

class DeepseekService:
    def __init__(self, model: str = "deepseek-chat"):
        logger.info("Initializing Deepseek Service")
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        # 优先使用配置中的 DEEPSEEK_MODEL，其次使用传入的 model
        self.model = settings.DEEPSEEK_MODEL or model 

    async def generate_stream(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            logger.info(f"Generating response for messages with model: {self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    # 使用 ensure_ascii=False 来保持中文字符
                    content = json.dumps(chunk.choices[0].delta.content, ensure_ascii=False)
                    yield f"data: {content}\n\n"
        except Exception as e:
            logger.error(f"Error in generate_stream: {str(e)}", exc_info=True)  # exc_info=True 用于在记录错误时提供详细的错误信息
            error_msg = json.dumps(f"生成回复时出错: {str(e)}", ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    async def generate(self, messages: List[Dict]) -> str:
        """非流式生成回复"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Generation error: {str(e)}")
            raise 