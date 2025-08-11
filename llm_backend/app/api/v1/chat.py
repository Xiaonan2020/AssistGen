from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.deepseek_service import DeepseekService
from app.models.chat import ChatRequest

router = APIRouter()
llm_service = DeepseekService()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        return StreamingResponse(
            llm_service.generate_stream(request.messages),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 