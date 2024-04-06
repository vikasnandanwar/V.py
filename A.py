from fastapi import FastAPI, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel
from typing import List

# MongoDB Atlas connection string
mongo_uri = "YOUR_MONGODB_ATLAS_CONNECTION_STRING"

# Initialize FastAPI app
app = FastAPI()

# Connect to MongoDB Atlas using motor
client = AsyncIOMotorClient(mongo_uri)
db = client["library"]  # Database name: library
books_collection = db["books"]  # Collection name: books
users_collection = db["users"]  # Collection name: users


class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool = True  # Indicates whether the book is available for borrowing


class User(BaseModel):
    name: str
    email: str


@app.post("/books/", response_model=Book)
async def create_book(book: Book):
    inserted = await books_collection.insert_one(book.dict())
    return {"id": str(inserted.inserted_id), **book.dict()}


@app.get("/books/", response_model=List[Book])
async def get_books():
    books = []
    async for book in books_collection.find():
        books.append({"id": str(book["_id"]), **book})
    return books


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = await books_collection.find_one({"_id": ObjectId(book_id)})
    if book:
        return {"id": str(book["_id"]), **book}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: str, book: Book):
    updated = await books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": book.dict()})
    if updated.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    else:
        return {"id": book_id, **book.dict()}


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str):
    deleted = await books_collection.delete_one({"_id": ObjectId(book_id)})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.post("/users/", response_model=User)
async def create_user(user: User):
    inserted = await users_collection.insert_one(user.dict())
    return {"id": str(inserted.inserted_id), **user.dict()}


@app.get("/users/", response_model=List[User])
async def get_users():
    users = []
    async for user in users_collection.find():
        users.append({"id": str(user["_id"]), **user})
    return users


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return {"id": str(user["_id"]), **user}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
