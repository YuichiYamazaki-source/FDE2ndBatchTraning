"""
One-time script: load walmart-products.xlsx into ChromaDB.

Usage (run from project root with Docker services up):
    python data/ingest.py

Requires .env with:
    OPENAI_API_KEY=...
    CHROMA_HOST=localhost   (default)
    CHROMA_PORT=8001        (host-side mapped port)
"""

import math
import os
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --- Config ---------------------------------------------------------------

XLSX_PATH = os.path.join(os.path.dirname(__file__), "..", "Project", "walmart-products.xlsx")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "products")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # OpenAI embeddings API batch limit

# --- Helpers --------------------------------------------------------------

def build_embed_text(row: pd.Series) -> str:
    """Build embedding text with field labels (Problem Statement Section 9).

    Fields: product_name, description, specifications, ingredients,
            customer_reviews, category_name

    Field labels are prepended so the embedding model understands field
    boundaries. This keeps implementation simple (single vector per product)
    while making future field-level chunking straightforward — each labeled
    segment can be extracted and embedded independently if needed.
    """
    fields = [
        ("product_name", row.get("product_name")),
        ("description", row.get("description")),
        ("specifications", row.get("specifications")),
        ("ingredients", row.get("ingredients")),
        ("reviews", row.get("customer_reviews")),
        ("category", row.get("category_name")),
    ]
    parts = [
        f"{label}: {val}"
        for label, val in fields
        if val and str(val) != "nan"
    ]
    return " ".join(parts).strip()


def row_to_metadata(row: pd.Series) -> dict:
    """Convert a DataFrame row to a ChromaDB metadata dict (str/int/float/bool only)."""
    def safe(val, cast=str):
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        try:
            return cast(val)
        except (ValueError, TypeError):
            return None

    return {
        "product_id":             str(int(row["product_id"])),
        "product_name":           safe(row.get("product_name")),
        "description":            safe(row.get("description")),
        "main_image":             safe(row.get("main_image")),
        "final_price":            safe(row.get("final_price"), float),
        "unit_price":             safe(row.get("unit_price"), float),
        "currency":               safe(row.get("currency")),
        "rating":                 safe(row.get("rating"), float),
        "review_count":           safe(row.get("review_count"), int),
        "brand":                  safe(row.get("brand")),
        "category_name":          safe(row.get("category_name")),
        "root_category_name":     safe(row.get("root_category_name")),
        "available_for_delivery": bool(row.get("available_for_delivery")),
        "available_for_pickup":   bool(row.get("available_for_pickup")),
        "specifications":         safe(row.get("specifications")),
        "ingredients":            safe(row.get("ingredients")),
        "colors":                 safe(row.get("colors")),
        "customer_reviews":       safe(row.get("customer_reviews")),
        "seller":                 safe(row.get("seller")),
        "other_attributes":       safe(row.get("other_attributes")),
    }


# --- Main -----------------------------------------------------------------

def main() -> None:
    import chromadb
    from openai import OpenAI

    print(f"Loading {XLSX_PATH} ...")
    df = pd.read_excel(XLSX_PATH)
    print(f"  {len(df)} rows loaded.")

    # Drop rows without a usable product_id
    df = df.dropna(subset=["product_id"])
    df["product_id"] = df["product_id"].astype(int)
    print(f"  {len(df)} rows after dropping missing product_id.")

    # Connect to ChromaDB
    print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT} ...")
    chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"  Collection '{COLLECTION_NAME}' ready.")

    # Build texts and metadata
    texts = [build_embed_text(row) for _, row in df.iterrows()]
    ids = [str(int(row["product_id"])) for _, row in df.iterrows()]
    metadatas = [row_to_metadata(row) for _, row in df.iterrows()]

    # Embed and upsert in batches
    openai_client = OpenAI()
    total = len(texts)
    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch_texts = texts[start:end]
        batch_ids = ids[start:end]
        batch_meta = metadatas[start:end]

        print(f"  Embedding rows {start + 1}–{end} / {total} ...")
        response = openai_client.embeddings.create(model=EMBED_MODEL, input=batch_texts)
        embeddings = [item.embedding for item in response.data]

        # Remove None values from metadata (ChromaDB rejects None)
        cleaned_meta = [
            {k: v for k, v in m.items() if v is not None}
            for m in batch_meta
        ]

        collection.upsert(
            ids=batch_ids,
            embeddings=embeddings,
            metadatas=cleaned_meta,
        )

    count = collection.count()
    print(f"\nDone. {count} documents in '{COLLECTION_NAME}' collection.")


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)
    main()
