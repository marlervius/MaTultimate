from fastapi import FastAPI, HTTPException
from app.models.config import MaterialConfig, GenerationResponse
from app.services.orchestrator import MaTultimateOrchestrator
import uvicorn

app = FastAPI(title="MaTultimate API")

@app.get("/")
async def root():
    return {"message": "MaTultimate API is running"}

@app.post("/generate", response_model=GenerationResponse)
async def generate_material(config: MaterialConfig):
    try:
        orchestrator = MaTultimateOrchestrator()
        result = orchestrator.generate_material(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
