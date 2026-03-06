"""
Unit tests for Agent tools and orchestrator (Phase 3).

ChromaDB and OpenAI are mocked — no Docker or real API keys needed.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

sys.modules.setdefault("chromadb", MagicMock())
sys.modules.setdefault("openai", MagicMock())
sys.modules.setdefault("agents", MagicMock())

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")


# ---------------------------------------------------------------------------
# tools — _format_products
# ---------------------------------------------------------------------------

def test_format_products_basic():
    from ai_agents.tools import _format_products
    metadatas = [
        {"product_id": "1", "product_name": "Cream", "final_price": 9.99, "rating": 4.5},
        {"product_id": "2", "product_name": "Shampoo", "final_price": 5.00, "rating": 4.0},
    ]
    result = _format_products(metadatas)
    assert "[1] Cream" in result
    assert "$9.99" in result
    assert "⭐4.5" in result
    assert "[2] Shampoo" in result


def test_format_products_empty():
    from ai_agents.tools import _format_products
    assert _format_products([]) == "No products found."


def test_format_products_respects_limit():
    from ai_agents.tools import _format_products
    metadatas = [{"product_id": str(i), "product_name": f"P{i}"} for i in range(10)]
    result = _format_products(metadatas, max_items=3)
    assert result.count("- [") == 3


# ---------------------------------------------------------------------------
# orchestrator — run_orchestrator
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_orchestrator_injects_product_id():
    """run_orchestrator should prepend product_id context to the input."""
    with patch("ai_agents.orchestrator.Runner") as mock_runner:
        mock_result = MagicMock()
        mock_result.final_output = "This product is great."
        mock_runner.run = AsyncMock(return_value=mock_result)

        from ai_agents.orchestrator import run_orchestrator
        response = await run_orchestrator("Is this good?", product_id="123")

        assert response == "This product is great."
        call_input = mock_runner.run.call_args.kwargs.get("input", mock_runner.run.call_args.args[1] if len(mock_runner.run.call_args.args) > 1 else "")
        assert "product_id=123" in call_input


@pytest.mark.asyncio
async def test_run_orchestrator_no_product_id():
    with patch("ai_agents.orchestrator.Runner") as mock_runner:
        mock_result = MagicMock()
        mock_result.final_output = "Here are some products."
        mock_runner.run = AsyncMock(return_value=mock_result)

        from ai_agents.orchestrator import run_orchestrator
        response = await run_orchestrator("Show me shampoos")

        assert response == "Here are some products."
        call_input = mock_runner.run.call_args.kwargs.get("input", mock_runner.run.call_args.args[1] if len(mock_runner.run.call_args.args) > 1 else "")
        assert call_input == "Show me shampoos"


# ---------------------------------------------------------------------------
# chat endpoint — agent_used is now "orchestrator"
# ---------------------------------------------------------------------------

def test_chat_endpoint_uses_orchestrator():
    """Chat endpoint should report agent_used='orchestrator' (not 'stub')."""
    from main import app
    from fastapi.testclient import TestClient
    test_client = TestClient(app)

    with patch("routers.chat.run_orchestrator", new_callable=AsyncMock) as mock_orch:
        mock_orch.return_value = "Great product!"
        response = test_client.post("/api/chat", json={"message": "Is this good?", "product_id": "123"})
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Great product!"
        assert data["agent_used"] == "orchestrator"
