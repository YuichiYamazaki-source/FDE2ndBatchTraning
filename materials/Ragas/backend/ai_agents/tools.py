import chromadb
from agents import function_tool
from openai import AsyncOpenAI

from core.config import settings


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _chroma() -> chromadb.HttpClient:
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def _collection():
    return _chroma().get_collection(settings.chroma_collection_name)


async def _embed(query: str) -> list[float]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    embedding = await client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    return embedding.data[0].embedding


def _format_products(metadatas: list[dict], max_items: int = 5) -> str:
    lines = []
    for m in metadatas[:max_items]:
        name = m.get("product_name", "Unknown")
        price = m.get("final_price")
        rating = m.get("rating")
        pid = m.get("product_id", "")
        line = f"- [{pid}] {name}"
        if price is not None:
            line += f"  ${price:.2f}"
        if rating is not None:
            line += f"  ⭐{rating}"
        lines.append(line)
    return "\n".join(lines) if lines else "No products found."


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@function_tool
async def search_products(query: str, limit: int = 5) -> str:
    """Search for products using natural language.

    Args:
        query: Natural language search query (e.g. "organic skincare under $30").
        limit: Maximum number of results to return (1-15).
    """
    limit = max(1, min(15, limit))
    vector = await _embed(query)

    results = _collection().query(
        query_embeddings=[vector],
        n_results=limit,
        include=["metadatas"],
    )
    metadatas = results.get("metadatas", [[]])[0]
    return _format_products(metadatas, limit)


@function_tool
def get_product(product_id: str) -> str:
    """Retrieve full details for a specific product by its ID.

    Args:
        product_id: The unique product identifier.
    """
    results = _collection().get(ids=[product_id], include=["metadatas"])
    metadatas = results.get("metadatas", [])
    if not metadatas:
        return f"Product {product_id} not found."

    m = metadatas[0]
    fields = [
        ("Product ID", product_id),
        ("Name", m.get("product_name")),
        ("Price", f"${m['final_price']:.2f}" if m.get("final_price") else None),
        ("Rating", m.get("rating")),
        ("Reviews", m.get("review_count")),
        ("Brand", m.get("brand")),
        ("Category", m.get("category_name")),
        ("Delivery", m.get("available_for_delivery")),
        ("Pickup", m.get("available_for_pickup")),
        ("Description", m.get("description")),
        ("Specifications", m.get("specifications")),
        ("Ingredients", m.get("ingredients")),
    ]
    lines = [f"{k}: {v}" for k, v in fields if v is not None]
    return "\n".join(lines)


@function_tool
def analyze_reviews(product_id: str) -> str:
    """Retrieve and return customer reviews for a product so you can analyze them.

    Returns the raw reviews text. Summarize positives, negatives, and overall
    quality in your response.

    Args:
        product_id: The unique product identifier.
    """
    results = _collection().get(ids=[product_id], include=["metadatas"])
    metadatas = results.get("metadatas", [])
    if not metadatas:
        return f"Product {product_id} not found."

    m = metadatas[0]
    reviews = m.get("customer_reviews")
    rating = m.get("rating")
    review_count = m.get("review_count")

    if not reviews:
        return f"No customer reviews available for product {product_id}."

    return (
        f"Product: {m.get('product_name', product_id)}\n"
        f"Rating: {rating} ({review_count} reviews)\n\n"
        f"Customer Reviews:\n{reviews}"
    )


@function_tool
def recommend_alternatives(category_name: str, min_rating: float = 4.0, limit: int = 5) -> str:
    """Find alternative products in the same category with a minimum rating.

    Use this when a product has poor reviews and you want to suggest better options.

    Args:
        category_name: Product category to search within.
        min_rating: Minimum acceptable rating (default 4.0).
        limit: Number of alternatives to return (1-10).
    """
    limit = max(1, min(10, limit))
    try:
        results = _collection().get(
            where={
                "$and": [
                    {"category_name": {"$eq": category_name}},
                    {"rating": {"$gte": min_rating}},
                ]
            },
            include=["metadatas"],
            limit=limit,
        )
        metadatas = results.get("metadatas", [])
    except Exception:
        metadatas = []

    if not metadatas:
        return f"No alternatives found in '{category_name}' with rating ≥ {min_rating}."

    return f"Top alternatives in '{category_name}' (rating ≥ {min_rating}):\n" + _format_products(metadatas, limit)
