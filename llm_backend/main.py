from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from app.services.llm_factory import LLMFactory
from app.services.search_service import SearchService

from fastapi.staticfiles import StaticFiles
from datetime import datetime
from pathlib import Path
from app.services.rag_service import RAGService
from app.services.rag_chat_service import RAGChatService
from app.core.logger import get_logger, log_structured
from app.core.middleware import LoggingMiddleware
from app.core.config import settings
from app.api import api_router


# 配置上传目录 - RAG 功能的
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# logger 变量就被初始化为一个日志记录器实例。
# 之后，便可以在当前文件中直接使用 logger.info()、logger.error() 等方法来记录日志，而不需要进行其他操作。
logger = get_logger(service="main")

# 创建 FastAPI 应用实例
app = FastAPI(title="AssistGen REST API")

# 添加日志中间件， 使用 LoggingMiddleware 来统一处理日志记录，从而替代 FastAPI 的原生打印日志。
app.add_middleware(LoggingMiddleware)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中要设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 用户注册、登录路由通过 api_router 路由挂载到 /api 前缀
app.include_router(api_router, prefix="/api")

class ReasonRequest(BaseModel):
    messages: List[Dict[str, str]]

class ChatMessage(BaseModel):
    messages: List[Dict[str, str]]

class RAGChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    index_id: str

@app.post("/chat")
async def chat_endpoint(request: ChatMessage):
    """聊天接口"""
    try:
        logger.info("Processing chat request")
        chat_service = LLMFactory.create_chat_service()
        
        log_structured("chat_request", {
            "message_count": len(request.messages),
            "last_message": request.messages[-1]["content"][:100] + "..."
        })
        
        # 默认情况下， FastAPI使用JSONResponse返回响应。
        # 要返回流式响应，请使用StreamingResponse: 将生成器函数传递给StreamingResponse ，然后将其返回。
        # FastAPI 官方详细文档：https://fastapi.tiangolo.com/advanced/custom-response/#redirectresponse
        return StreamingResponse(
            chat_service.generate_stream(request.messages),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)  # exc_info=True 用于在记录错误时提供详细的错误信息
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reason")
async def reason_endpoint(request: ReasonRequest):
    """推理接口"""
    try:
        logger.info("Processing reasoning request")
        reasoner = LLMFactory.create_reasoner_service()
        
        log_structured("reason_request", {
            "message_count": len(request.messages),
            "last_message": request.messages[-1]["content"][:100] + "..."
        })
        
        return StreamingResponse(
            reasoner.generate_stream(request.messages),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        logger.error(f"Reasoning error: {str(e)}", exc_info=True)  # exc_info=True 用于在记录错误时提供详细的错误信息
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


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并准备 RAG 处理"""
    try:
        logger.info(f"Uploading file: {file.filename}")
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / filename
        
        # 确保上传目录存在
        UPLOAD_DIR.mkdir(exist_ok=True)
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        # 获取文件类型
        file_type = file.content_type
        file_ext = Path(file.filename).suffix.lower()
        
        # 返回文件信息
        file_info = {
            "filename": filename,
            "original_name": file.filename,
            "size": len(content),
            "type": file_type,
            "path": str(file_path).replace('\\', '/'),  # 使用正斜杠
        }
        
        print(f"文件已保存到: {file_path}")  # 添加日志
        

                # 初始化 RAG 服务
        rag_service = RAGService()
        # 初始化 RAG 处理
        rag_result = await rag_service.process_file(file_info)
        
        # 合并结果
        result = {**file_info, **rag_result}
        
        log_structured("file_upload", {
            "filename": file.filename,
            "size": len(content),
            "type": file_type
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return {"error": str(e)}
    
    return f"data: {result}\n\n"

@app.post("/chat-rag")
async def rag_chat_endpoint(request: RAGChatRequest):
    """基于文档的问答接口"""
    try:
        rag_chat_service = RAGChatService()
        
        return StreamingResponse(
            rag_chat_service.generate_stream(
                request.messages,
                request.index_id
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 最后挂载静态文件，并确保使用绝对路径
STATIC_DIR = Path(__file__).parent / "static" / "dist"
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
