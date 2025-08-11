from typing import List, Dict, AsyncGenerator
import json
import asyncio
from app.tools.search import SearchTool
from openai import AsyncOpenAI
from app.core.config import settings

class SearchService:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )

        self.search_tool = SearchTool()
        self.model = settings.DEEPSEEK_MODEL or model 

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "搜索互联网上的实时信息。必须使用此函数获取最新信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询词，例如'2025年的DeepSeek最新进展'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    async def _call_with_tool(self, messages: List[Dict]) -> Dict:
        """调用模型并获取工具调用结果"""
        try:
            # 先尝试强制使用工具
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你必须使用search函数来获取信息。"
                            "不要直接回答，而是调用search函数。"
                            "格式示例：search(\"关键词\")"
                        )
                    },
                    {"role": "user", "content": messages}  # 直接使用传入的查询文本
                ],
                tools=self.tools,
                tool_choice={"type": "function", "function": {"name": "search"}},
                stream=False
            )


            message = response.choices[0].message

            # 如果返回的是函数调用文本，手动解析
            if message.content and "search(" in message.content:
                # 提取搜索查询
                query = message.content.split('search("')[1].split('")')[0]
                
                # 构造工具调用对象
                tool_call = {
                    "id": "call_" + str(hash(query)),
                    "type": "function",
                    "function": {
                        "name": "search",
                        "arguments": json.dumps({"query": query}, ensure_ascii=False)
                    }
                }
                
                return {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                }
            
        except Exception as e:
            # print(f"Tool call error: {str(e)}")
            pass


    async def generate_stream(self, query: str) -> AsyncGenerator[str, None]:
        """流式生成带搜索功能的回复"""
        try:
            # 添加系统消息
            system_message = {
                "role": "system",
                "content": (
                    "你是一个能够搜索互联网的AI助手。"
                    "请基于搜索结果提供完整、准确的回答。"
                    "回答时请引用具体来源，并说明信息的时效性。"
                    "如果搜索结果不相关，请说明并尝试基于已知信息回答。"
                )
            }
            
            try:
                # 第一步：获取工具调用
                message = await self._call_with_tool(query)
                
                # 如果有工具调用
                if message.get("tool_calls"):
                    tool_call = message["tool_calls"][0]
                    
                    try:
                        # 解析搜索参数
                        args = json.loads(tool_call["function"]["arguments"])
        
                        # 执行搜索
                        search_results = await asyncio.to_thread(
                            self.search_tool.search,
                            args["query"]
                        )
                        
                        if search_results:
                            # 构建搜索结果对象
                            search_data = {
                                "type": "search_results",
                                "total": len(search_results),
                                "query": args["query"],
                                "results": [
                                    {
                                        "title": result["title"],
                                        "url": result["url"],
                                        "snippet": result["snippet"]
                                    }
                                    for result in search_results
                                ]
                            }
                            
                            # 使用 ensure_ascii=False 输出搜索结果
                            content = json.dumps(search_data, ensure_ascii=False)
                            yield f"data: {content}\n\n"
                            
                            # 构建上下文内容
                            context = []
                            for result in search_results:
                                context.append(
                                    f"来源：{result['title']}\n"
                                    f"链接：{result['url']}\n"
                                    f"内容：{result['snippet']}\n"
                                )
                            
                            # 构造带上下文的提示
                            context_prompt = (
                                "请基于以下搜索结果回答用户的问题。\n\n"
                                "搜索结果：\n\n" + 
                                "\n---\n".join(context) +
                                "\n\n用户问题：" + query +
                                "\n\n要求：\n"
                                "1. 提供完整、准确的回答\n"
                                "2. 引用具体来源和链接\n"
                                "3. 说明信息的时效性\n"
                                "4. 如果信息不足，说明局限性"
                            )
                            
                            # # 生成总结回复标题
                            # content = json.dumps("\n\n### 🤖 联网检索结果显示：\n\n", ensure_ascii=False)
                            # yield f"data: {content}\n\n"
                            
                            # 使用新的消息上下文生成回复
                            async for chunk in await self.client.chat.completions.create(
                                model=self.model,
                                messages=[
                                    system_message,
                                    {"role": "user", "content": context_prompt}
                                ],
                                stream=True
                            ):
                                if chunk.choices[0].delta.content:
                                    content = json.dumps(chunk.choices[0].delta.content, ensure_ascii=False)
                                    yield f"data: {content}\n\n"
             
                    except Exception as e:
                        pass
                
            except Exception as e:
                    pass
                
        except Exception as e:
                    pass