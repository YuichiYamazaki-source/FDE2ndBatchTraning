"""
Backend API tests (Phase 1).

External dependencies (ChromaDB, OpenAI) are mocked so tests run without
Docker or real API keys.
"""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Add backend/ to path so imports resolve (routers, services, models, core)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Stub out heavy dependencies before any backend module is imported
sys.modules.setdefault("chromadb", MagicMock())
sys.modules.setdefault("openai", MagicMock())

# Stub the openai-agents SDK (imported as "agents" by the SDK package)
_agents_mock = MagicMock()
sys.modules.setdefault("agents", _agents_mock)

# Patch settings before importing main (pydantic-settings reads env at import time)
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")

from main import app  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

MOCK_PRODUCT = {
    "product_id": "123",
    "product_name": "Organic Face Cream",
    "description": "Moisturizing cream",
    "main_image": "http://example.com/img.jpg",
    "final_price": 19.99,
    "rating": 4.5,
    "review_count": 100,
    "brand": "NatureBrand",
    "category_name": "Skincare",
    "root_category_name": "Beauty",
    "available_for_delivery": True,
    "available_for_pickup": False,
}


@patch("routers.search.search_products")
def test_search_returns_results(mock_search):
    from models.schemas import ProductSummary
    mock_search.return_value = [ProductSummary(**MOCK_PRODUCT)]

    response = client.post("/api/search", json={"query": "organic skincare", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["product_name"] == "Organic Face Cream"


@patch("routers.search.search_products")
def test_search_empty_results(mock_search):
    mock_search.return_value = []

    response = client.post("/api/search", json={"query": "nonexistent product", "limit": 5})
    assert response.status_code == 200
    assert response.json() == {"results": [], "total": 0}


def test_search_limit_validation():
    # limit > 15 should fail validation
    response = client.post("/api/search", json={"query": "shoes", "limit": 20})
    assert response.status_code == 422

    # limit < 1 should fail validation
    response = client.post("/api/search", json={"query": "shoes", "limit": 0})
    assert response.status_code == 422


def test_search_missing_query():
    response = client.post("/api/search", json={"limit": 5})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

MOCK_PRODUCT_DETAIL = {
    **MOCK_PRODUCT,
    "specifications": "50ml",
    "ingredients": "Aloe Vera",
    "colors": None,
    "customer_reviews": "Great product!",
    "unit_price": 19.99,
    "currency": "USD",
    "seller": "NatureStore",
    "other_attributes": None,
}


@patch("routers.products.get_product_detail")
def test_get_product_found(mock_get):
    from models.schemas import ProductDetail
    mock_get.return_value = ProductDetail(**MOCK_PRODUCT_DETAIL)

    response = client.get("/api/products/123")
    assert response.status_code == 200
    assert response.json()["product_name"] == "Organic Face Cream"
    assert response.json()["ingredients"] == "Aloe Vera"


@patch("routers.products.get_product_detail")
def test_get_product_not_found(mock_get):
    mock_get.return_value = None

    response = client.get("/api/products/999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Chat (Phase 3 — Orchestrator Agent)
# ---------------------------------------------------------------------------

@patch("routers.chat.run_orchestrator", new_callable=AsyncMock)
def test_chat_orchestrator(mock_orch):
    mock_orch.return_value = "This product has great reviews."

    response = client.post("/api/chat", json={"message": "Is this product good?", "product_id": "123"})
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "This product has great reviews."
    assert data["agent_used"] == "orchestrator"


@patch("routers.chat.run_orchestrator", new_callable=AsyncMock)
def test_chat_without_product_id(mock_orch):
    mock_orch.return_value = "I can help with product questions."

    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json()["agent_used"] == "orchestrator"
