from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from app.models.schemas import JurnalRequest
from app.services.ai_agent import ResearchAgent
from app.api.auth import get_api_key
from typing import Optional

router = APIRouter()

@router.get("/", tags=["Health"])
async def root():
    """Cek status API layer."""
    return {"status": "Siap", "mode": "Backend V2 (Streaming & BYOK)"}

@router.post("/riset-lengkap", 
             tags=["Research"], 
             summary="Jalankan Pipeline Riset Sequential (Streaming)")
async def sequential_research(
    data: JurnalRequest, 
    api_key: str = Depends(get_api_key),
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    Endpoint utama (Streaming):
    - **BYOK Support:** Jika header `X-Gemini-API-Key` ada, akan digunakan untuk Gemini API (Public).
    - **Streaming Response:** Menggunakan SSE style untuk real-time updates.
    """
    try:
        # Pake instance agent baru per request buat handle dynamic key
        dynamic_agent = ResearchAgent(gemini_api_key=x_gemini_api_key)
        
        return StreamingResponse(
            dynamic_agent.stream_sequential_research(data.topik, data.target_pembaca),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
