from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import engine, Base
from routes import auth, tender

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NividaAI Backend", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tender.router, prefix="/api/tender", tags=["Tender Management"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "NividaAI Backend is healthy"}

@app.get("/")
def read_root():
    return {"message": "Welcome to NividaAI API"}
