from fastapi import APIRouter

from models.schemas import SearchRequest, SearchResponse
from services.rag_service import search_products

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    results = await search_products(request.query, request.limit)
    return SearchResponse(results=results, total=len(results))
