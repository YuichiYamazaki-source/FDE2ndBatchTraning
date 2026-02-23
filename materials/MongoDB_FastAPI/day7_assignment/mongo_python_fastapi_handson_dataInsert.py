# seed_data.py - Run this once to populate initial data

from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client.library_db
books_col = db.books
transactions_col = db.transactions

# Clear existing data (for testing)
books_col.delete_many({})
transactions_col.delete_many({})

# Seed 4 books
books_data = [
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "isbn": "1593279280",
        "total_copies": 5,
        "available_copies": 3,  # One copy checked out via tx2
        "current_status": "checked_out",
        "last_transaction_id": None
    },
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "0132350882",
        "total_copies": 3,
        "available_copies": 0,
        "current_status": "checked_out",
        "last_transaction_id": None  # Overdue tx1
    },
    {
        "title": "Hands-On Machine Learning",
        "author": "Aurélien Géron",
        "isbn": "1492032646",
        "total_copies": 4,
        "available_copies": 4,
        "current_status": "available",
        "last_transaction_id": None
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "David Thomas",
        "isbn": "020161622X",
        "total_copies": 2,
        "available_copies": 0,  # In maintenance
        "current_status": "maintenance",
        "last_transaction_id": None
    }
]

books = []
for book in books_data:
    result = books_col.insert_one(book)
    books.append({"_id": str(result.inserted_id), **book})

print("Inserted books:", [b["_id"] for b in books])

# Seed 2 transactions
now = datetime.utcnow()
tx1_id = transactions_col.insert_one({
    "book_id": ObjectId(books[1]["_id"]),  # Clean Code - overdue
    "borrower_name": "Alice Johnson",
    "borrower_id": "STU001",
    "checkout_date": now - timedelta(days=2),
    "due_date": now - timedelta(days=1),  # Overdue!
    "return_date": None,
    "status": "checked_out",
    "fine_amount": 0.0
}).inserted_id

tx2_id = transactions_col.insert_one({
    "book_id": ObjectId(books[0]["_id"]),  # Python Crash Course
    "borrower_name": "Bob Smith",
    "borrower_id": "STU002",
    "checkout_date": now - timedelta(hours=12),
    "due_date": now + timedelta(days=7),
    "return_date": None,
    "status": "checked_out",
    "fine_amount": 0.0
}).inserted_id

# Update books with actual last_transaction_id (simulates your CRUD logic)
books_col.update_one({"_id": ObjectId(books[1]["_id"])}, {"$set": {"last_transaction_id": tx1_id}})
books_col.update_one({"_id": ObjectId(books[0]["_id"])}, {"$set": {"last_transaction_id": tx2_id}})

print("Sample data ready! Test endpoints now.")

# Verification queries (mirrors your API filters)
print("\nSample available books:")
for b in books_col.find({"available_copies": {"$gt": 0}}):
    print(f"- {b['title']} (avail: {b['available_copies']}, status: {b['current_status']})")

print("\nOverdue transactions:")
for t in transactions_col.find({"status": "checked_out", "due_date": {"$lt": now}}):
    print(f"- Book: {books_col.find_one({'_id': t['book_id']})['title']}, Borrower: {t['borrower_name']}")

print("\nAll books summary:")
for b in books_col.find({}).sort("title"):
    print(f"- {b['title']}: {b['available_copies']}/{b['total_copies']} available")

client.close()
