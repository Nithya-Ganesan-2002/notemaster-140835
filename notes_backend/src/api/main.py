from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.api.db import Base, engine

openapi_tags = [
    {"name": "auth", "description": "User registration, login, and profile endpoints."},
    {"name": "notes", "description": "Create, update, delete, and list notes."}
]

app = FastAPI(
    title="Notes Backend API",
    description="REST API (FastAPI) backend for user management & notes CRUD.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"message": "Healthy"}
