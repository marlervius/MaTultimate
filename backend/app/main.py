from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.tools.storage import init_db
import uvicorn

app = FastAPI(title="MaTultimate API - VGS Edition")

# CORS - tillat spesifikke frontend-domener
import os
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "https://matultimate.streamlit.app",
    "https://*.streamlit.app",
    "http://localhost:8501",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialiser database ved oppstart
@app.on_event("startup")
async def startup_event():
    init_db()

# Inkluder ruter
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "MaTultimate API is running", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
