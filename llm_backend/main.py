from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from app.services.llm_factory import LLMFactory
from app.services.search_service import SearchService

from fastapi.staticfiles import StaticFiles



app = FastAPI(title="AssistGen REST API")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中要设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReasonRequest(BaseModel):
    messages: List[Dict[str, str]]

class ChatMessage(BaseModel):
    messages: List[Dict[str, str]]


@app.post("/chat")
async def chat_endpoint(request: ChatMessage):
    """聊天接口"""
    try:
        chat_service = LLMFactory.create_chat_service()
                
        return StreamingResponse(
            chat_service.generate_stream(request.messages),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reason")
async def reason_endpoint(request: ReasonRequest):
    """推理接口"""
    try:
        reasoner = LLMFactory.create_reasoner_service()
       
        return StreamingResponse(
            reasoner.generate_stream(request.messages),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_endpoint(request: ChatMessage):
    """带搜索功能的聊天接口"""
    try:
        search_service = SearchService()
        return StreamingResponse(
            search_service.generate_stream(request.messages[0]["content"]),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"} 



app.mount("/", StaticFiles(directory="static/dist", html=True), name="static")