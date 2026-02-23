from fastapi import FastAPI 
from .router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Simple Authentication System')

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
    )

@app.get("/")
def root():
    return "Welcom to Our Simple Authentication System!"