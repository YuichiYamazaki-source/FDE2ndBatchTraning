from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str = Field(..., min_length=13, max_length=13)
    total_copies: int = Field(..., gt=0)

class BookCreate(BookBase):
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('ISBN must contain only digits')
        if len(v) != 13:
            raise ValueError('ISBN must be exactly 13 digits')
        return v

class BookResponse(BookBase):
    id: str = Field(..., alias="_id")
    available_copies: int
    current_status: Literal["available", "checked_out", "maintenance"]

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    total_copies: Optional[int] = Field(None, gt=0)


class CheckoutRequest(BaseModel):
    borrower_name: str = Field(..., min_length=1)
    borrower_id: str = Field(..., min_length=1)
    due_days: int = Field(..., ge=1, le=30)

class ReturnRequest(BaseModel):
    borrower_id: str = Field(..., min_length=1)

