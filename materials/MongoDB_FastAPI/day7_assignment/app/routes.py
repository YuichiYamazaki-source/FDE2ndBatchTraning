from fastapi import APIRouter, Query
from typing import Optional
from app.models import BookCreate, BookUpdate, CheckoutRequest, ReturnRequest
from app import crud

router = APIRouter(prefix="/library", tags=["library"])

# Book routes
@router.post("/books/")
async def create_book(payload: BookCreate):
    return crud.create_book(payload.model_dump())


@router.get("/books/")
async def list_books(
    status: Optional[str] = Query(None),
    author: Optional[str] = Query(None)
):
    return crud.list_books(status=status, author=author)


@router.get("/books/{book_id}")
async def get_book(book_id: str):
    return crud.get_book(book_id)


@router.put("/books/{book_id}")
async def update_book(book_id: str, payload: BookUpdate):
    return crud.update_book(book_id, payload.model_dump(exclude_unset=True))


# Transaction routes
@router.post("/transactions/checkout/{book_id}")
async def checkout(book_id: str, req: CheckoutRequest):
    return crud.checkout_book(book_id, req.model_dump())

@router.post("/transactions/return/{book_id}")
async def return_book(book_id: str, req: ReturnRequest):
    return crud.return_book(book_id, req.model_dump())

@router.get("/transactions/")
async def list_transactions(
    book_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    borrower_id: Optional[str] = Query(None)
):
    return crud.list_transactions(book_id=book_id, status=status, borrower_id=borrower_id)


@router.get("/transactions/overdue")
async def list_overdue():
    return crud.list_overdue_transactions()
