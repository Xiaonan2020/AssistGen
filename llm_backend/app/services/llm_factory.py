from typing import Union
from app.core.config import settings, ServiceType
from app.services.deepseek_service import DeepseekService
from app.services.ollama_service import OllamaService

class LLMFactory:
    @staticmethod
    def create_chat_service():
        """创建聊天服务"""
        if settings.CHAT_SERVICE == ServiceType.DEEPSEEK:
            return DeepseekService()
        else:
            return OllamaService(model=settings.OLLAMA_CHAT_MODEL)

    @staticmethod
    def create_reasoner_service():
        """创建推理服务"""
        if settings.REASON_SERVICE == ServiceType.DEEPSEEK:
            return DeepseekService()
        else:
            return OllamaService(model=settings.OLLAMA_REASON_MODEL) 