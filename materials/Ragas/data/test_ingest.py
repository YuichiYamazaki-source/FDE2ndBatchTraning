"""Unit tests for data/ingest.py helper functions."""

import math
import sys
import os

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(__file__))
from ingest import build_embed_text, row_to_metadata


# --- build_embed_text -------------------------------------------------------

def _row(**kwargs) -> pd.Series:
    return pd.Series(kwargs)


def test_build_embed_text_all_fields():
    row = _row(
        product_name="Organic Face Cream",
        description="Moisturizing cream",
        specifications="50ml, SPF 30",
        ingredients="Aloe Vera, Shea Butter",
        customer_reviews="Great product!",
        category_name="Skincare",
    )
    text = build_embed_text(row)
    assert "product_name: Organic Face Cream" in text
    assert "description: Moisturizing cream" in text
    assert "specifications: 50ml, SPF 30" in text
    assert "ingredients: Aloe Vera, Shea Butter" in text
    assert "reviews: Great product!" in text
    assert "category: Skincare" in text


def test_build_embed_text_skips_nan():
    row = _row(
        product_name="Shampoo",
        description=float("nan"),
        specifications=None,
        ingredients="nan",
        customer_reviews="Good",
        category_name="Hair Care",
    )
    text = build_embed_text(row)
    assert "product_name: Shampoo" in text
    assert "description" not in text
    assert "specifications" not in text
    assert "ingredients" not in text
    assert "reviews: Good" in text


def test_build_embed_text_empty_row():
    row = _row()
    text = build_embed_text(row)
    assert text == ""


# --- row_to_metadata --------------------------------------------------------

def test_row_to_metadata_basic():
    row = _row(
        product_id=12345,
        product_name="Test Product",
        final_price=9.99,
        rating=4.5,
        review_count=100,
        available_for_delivery=True,
        available_for_pickup=False,
        currency="USD",
        description="A test product",
        main_image="http://example.com/img.jpg",
        brand="TestBrand",
        category_name="Electronics",
        root_category_name="Home",
        unit_price=9.99,
        colors=float("nan"),
        seller=None,
        specifications=float("nan"),
        ingredients=None,
        customer_reviews="Nice",
        other_attributes=float("nan"),
    )
    meta = row_to_metadata(row)

    assert meta["product_id"] == "12345"
    assert meta["product_name"] == "Test Product"
    assert meta["final_price"] == pytest.approx(9.99)
    assert meta["rating"] == pytest.approx(4.5)
    assert meta["review_count"] == 100
    assert meta["available_for_delivery"] is True
    assert meta["available_for_pickup"] is False
    # None fields should be None (filtered out before upsert)
    assert meta["colors"] is None
    assert meta["seller"] is None
    assert meta["specifications"] is None


def test_row_to_metadata_product_id_as_string():
    row = _row(product_id=99, product_name="X", available_for_delivery=False, available_for_pickup=False)
    meta = row_to_metadata(row)
    assert isinstance(meta["product_id"], str)
    assert meta["product_id"] == "99"
