from fastapi import FastAPI
from .routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Library Management System')

app.include_router(router)

@app.get("/")
def root():
    return {"Welcom to Our Inventory Management System!"}