from models.schemas import ProductDetail
from services.rag_service import get_product_by_id, _safe_float, _safe_int, _safe_bool


def get_product_detail(product_id: str) -> ProductDetail | None:
    metadata = get_product_by_id(product_id)
    if metadata is None:
        return None

    return ProductDetail(
        product_id=metadata.get("product_id", product_id),
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
        specifications=metadata.get("specifications"),
        ingredients=metadata.get("ingredients"),
        colors=metadata.get("colors"),
        customer_reviews=metadata.get("customer_reviews"),
        unit_price=_safe_float(metadata.get("unit_price")),
        currency=metadata.get("currency"),
        seller=metadata.get("seller"),
        other_attributes=metadata.get("other_attributes"),
    )
