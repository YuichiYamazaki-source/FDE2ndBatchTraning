from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, images, products, search

app = FastAPI(
    title="E-Commerce Product Discovery API",
    description="GenAI-powered product search and assistant",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(products.router)
app.include_router(chat.router)
app.include_router(images.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
