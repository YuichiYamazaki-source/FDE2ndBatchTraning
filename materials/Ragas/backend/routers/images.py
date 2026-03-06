import httpx
from fastapi import APIRouter, Query
from fastapi.responses import Response

router = APIRouter(prefix="/api", tags=["images"])

_client = httpx.AsyncClient(follow_redirects=True, timeout=10.0)


@router.get("/image-proxy")
async def image_proxy(url: str = Query(..., description="Image URL to proxy")):
    """Proxy external product images to avoid CDN referrer/CORS blocks."""
    if not url.startswith("https://i5.walmartimages.com/"):
        return Response(status_code=400, content=b"Only Walmart image URLs allowed")

    resp = await _client.get(url)
    return Response(
        content=resp.content,
        media_type=resp.headers.get("content-type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},
    )
