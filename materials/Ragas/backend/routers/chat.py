from fastapi import APIRouter

from ai_agents.orchestrator import run_orchestrator
from models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response_text = await run_orchestrator(request.message, request.product_id)
    return ChatResponse(response=response_text, agent_used="orchestrator")
