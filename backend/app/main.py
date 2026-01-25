from fastapi import FastAPI, HTTPException
from app.api.routes import router as api_router
import uvicorn

app = FastAPI(title="MaTultimate API - VGS Edition")

# Inkluder ruter
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "MaTultimate API is running", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
