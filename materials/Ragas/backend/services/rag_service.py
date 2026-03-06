import chromadb
from openai import AsyncOpenAI

from core.config import settings
from models.schemas import ProductSummary


def _get_chroma_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
    )


def _row_to_product_summary(metadata: dict) -> ProductSummary:
    return ProductSummary(
        product_id=metadata.get("product_id", ""),
        product_name=metadata.get("product_name"),
        description=metadata.get("description"),
        main_image=metadata.get("main_image"),
        final_price=_safe_float(metadata.get("final_price")),
        rating=_safe_float(metadata.get("rating")),
        review_count=_safe_int(metadata.get("review_count")),
        brand=metadata.get("brand"),
        category_name=metadata.get("category_name"),
        root_category_name=metadata.get("root_category_name"),
        available_for_delivery=_safe_bool(metadata.get("available_for_delivery")),
        available_for_pickup=_safe_bool(metadata.get("available_for_pickup")),
    )


def _safe_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> int | None:
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _safe_bool(value) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


async def search_products(query: str, limit: int) -> list[ProductSummary]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    embedding_response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    query_vector = embedding_response.data[0].embedding

    chroma = _get_chroma_client()
    collection = chroma.get_collection(settings.chroma_collection_name)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=limit,
        include=["metadatas"],
    )

    metadatas = results.get("metadatas", [[]])[0]
    return [_row_to_product_summary(m) for m in metadatas]


def get_product_by_id(product_id: str) -> dict | None:
    chroma = _get_chroma_client()
    collection = chroma.get_collection(settings.chroma_collection_name)

    results = collection.get(
        ids=[product_id],
        include=["metadatas"],
    )

    metadatas = results.get("metadatas", [])
    return metadatas[0] if metadatas else None
