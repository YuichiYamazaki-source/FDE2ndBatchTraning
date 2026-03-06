from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=15)


class ProductSummary(BaseModel):
    product_id: str
    product_name: str | None = None
    description: str | None = None
    main_image: str | None = None
    final_price: float | None = None
    rating: float | None = None
    review_count: int | None = None
    brand: str | None = None
    category_name: str | None = None
    root_category_name: str | None = None
    available_for_delivery: bool | None = None
    available_for_pickup: bool | None = None


class ProductDetail(ProductSummary):
    specifications: str | None = None
    ingredients: str | None = None
    colors: str | None = None
    customer_reviews: str | None = None
    unit_price: float | None = None
    currency: str | None = None
    seller: str | None = None
    other_attributes: str | None = None


class SearchResponse(BaseModel):
    results: list[ProductSummary]
    total: int


class ChatRequest(BaseModel):
    message: str
    product_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    agent_used: str = "orchestrator"
