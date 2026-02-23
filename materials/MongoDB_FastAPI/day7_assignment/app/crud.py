from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException
from app.database import books_col, transactions_col

# For BusinessLogic

def is_overdue(transaction) -> bool:
    return (
        transaction.get('status') == 'checked_out' and
        transaction.get('due_date') and
        transaction['due_date'] < datetime.now()
    )


def calculate_fine(due_date) -> float:
    now = datetime.now()
    if now > due_date:
        days_late = (now - due_date).days
        return max(0, days_late * 10)
    return 0.0

# Static DB crud
def create_book(payload: dict) -> dict:
    existing = books_col.find_one({"isbn": payload["isbn"]})
    if existing:
        raise HTTPException(status_code=400, detail="ISBN already exists")

    book_data = {
        **payload,
        "available_copies": payload["total_copies"],
        "current_status": "available",
        "last_transaction_id": None
    }

    result = books_col.insert_one(book_data)
    created_book = books_col.find_one({"_id": result.inserted_id})

    created_book["_id"] = str(created_book["_id"])

    return created_book

def list_books(status: str = None, author: str = None) -> list:
    query = {}

    if status:
        query["current_status"] = status

    if author:
        query["author"] = {"$regex": author, "$options": "i"}  # 大文字小文字を区別しない

    books = []
    for doc in books_col.find(query):
        doc["_id"] = str(doc["_id"])
        books.append(doc)

    return books

def get_book(book_id: str) -> dict:
    book = books_col.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book["_id"] = str(book["_id"])

    return book

def update_book(book_id: str, payload: dict) -> dict:
    updated_book = books_col.find_one_and_update(
        {"_id": ObjectId(book_id)},
        {"$set": payload},
        return_document=True
    )

    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")

    updated_book["_id"] = str(updated_book["_id"])
    return updated_book

# Transaction logic

def checkout_book(book_id: str, req: dict) -> dict:
    book = books_col.find_one({
        "_id": ObjectId(book_id),
        "available_copies": {"$gt": 0}
    })

    if not book:
        raise HTTPException(status_code=400, detail="Book not available for checkout")

    now = datetime.now()
    due_date = now + timedelta(days=req["due_days"])

    transaction_data = {
        "book_id": ObjectId(book_id),
        "borrower_name": req["borrower_name"],
        "borrower_id": req["borrower_id"],
        "checkout_date": now,
        "due_date": due_date,
        "return_date": None,
        "status": "checked_out",
        "fine_amount": 0.0
    }

    tx_result = transactions_col.insert_one(transaction_data)
    new_tx_id = tx_result.inserted_id

    books_col.update_one(
        {"_id": ObjectId(book_id)},
        {
            "$inc": {"available_copies": -1},
            "$set": {
                "current_status": "checked_out",
                "last_transaction_id": new_tx_id
            }
        }
    )

    transaction = transactions_col.find_one({"_id": new_tx_id})
    transaction["_id"] = str(transaction["_id"])
    transaction["book_id"] = str(transaction["book_id"])

    return transaction


def return_book(book_id: str, req: dict) -> dict:
    transaction = transactions_col.find_one(
        {
            "book_id": ObjectId(book_id),
            "borrower_id": req["borrower_id"],
            "status": "checked_out"
        },
        sort=[("checkout_date", -1)]
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="No active checkout found")

    now = datetime.now()
    fine_amount = calculate_fine(transaction["due_date"])

    transactions_col.update_one(
        {"_id": transaction["_id"]},
        {
            "$set": {
                "status": "returned",
                "return_date": now,
                "fine_amount": fine_amount
            }
        }
    )

    books_col.update_one(
        {"_id": ObjectId(book_id)},
        {
            "$inc": {"available_copies": 1},
            "$set": {"current_status": "available"}
        }
    )

    updated_tx = transactions_col.find_one({"_id": transaction["_id"]})
    updated_tx["_id"] = str(updated_tx["_id"])
    updated_tx["book_id"] = str(updated_tx["book_id"])

    return updated_tx


def list_transactions(book_id: str = None, status: str = None, borrower_id: str = None) -> list:
    query = {}

    if book_id:
        query["book_id"] = ObjectId(book_id)

    if status:
        query["status"] = status

    if borrower_id:
        query["borrower_id"] = borrower_id

    transactions = []
    for tx in transactions_col.find(query).sort("checkout_date", -1):
        tx["_id"] = str(tx["_id"])
        tx["book_id"] = str(tx["book_id"])
        transactions.append(tx)

    return transactions


def list_overdue_transactions() -> list:
    now = datetime.now()

    overdue = list(transactions_col.find({
        "status": "checked_out",
        "due_date": {"$lt": now}
    }).sort("due_date"))

    result = []
    for tx in overdue:
        book = books_col.find_one({"_id": tx["book_id"]})
        tx["_id"] = str(tx["_id"])
        tx["book_id"] = str(tx["book_id"])
        if book:
            tx["book_title"] = book["title"]
        result.append(tx)

    return result