from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import MaterialRequest, GenerationResponse
from app.agents.orchestrator import IntelligentOrchestrator
from app.models.config import MaterialConfig
import logging

router = APIRouter()
logger = logging.getLogger("API")

@router.post("/generate", response_model=GenerationResponse)
async def generate_math_material(request: MaterialRequest):
    """
    Hovedendepunkt for å generere matematikk-materiell.
    Starter den intelligente orkestratoren og returnerer PDF-data.
    """
    logger.info(f"Mottok forespørsel: {request.emne} for {request.klassetrinn}")
    
    try:
        # Konverter til MaterialConfig (som agenter forventer)
        config = MaterialConfig(
            klassetrinn=request.klassetrinn,
            emne=request.emne,
            kompetansemaal=request.kompetansemaal,
            differentiation=request.differentiation,
            include_answer_key=request.include_answer_key,
            document_format=request.document_format
        )
        
        orchestrator = IntelligentOrchestrator()
        # Merk: Vi må sikre at generate_material returnerer GenerationResponse i henhold til skjema
        result = orchestrator.create_dynamic_crew(config).kickoff()
        
        # Her må vi legge til logikk for å trekke ut PDF fra resultatet
        # (Dette vil bli utvidet når HybridCompiler er ferdig)
        
        return GenerationResponse(
            success=True,
            source_code=str(result),
            metadata={"klassetrinn": request.klassetrinn, "emne": request.emne}
        )
        
    except Exception as e:
        logger.error(f"Generering feilet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generering feilet: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "v2.0-vgs"}
