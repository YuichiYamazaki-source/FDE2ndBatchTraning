from fastapi import APIRouter, HTTPException

from models.schemas import ProductDetail
from services.product_service import get_product_detail

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str):
    product = get_product_detail(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
