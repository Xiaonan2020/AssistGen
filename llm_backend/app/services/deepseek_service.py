from typing import List, Dict, AsyncGenerator
import asyncio
from openai import AsyncOpenAI
from app.core.config import settings
import json

class DeepseekService:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        # 优先使用传入的 model，其次使用配置中的 DEEPSEEK_MODEL，最后使用默认值
        self.model = settings.DEEPSEEK_MODEL or model 

    async def generate_stream(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
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
            print(f"Stream generation error: {str(e)}")
            raise

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