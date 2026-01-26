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
        # Kjør crewet
        crew = orchestrator.create_dynamic_crew(config)
        result = crew.kickoff()
        
        # Hent utdata fra siste task (Redaktøren)
        final_code = result.raw if hasattr(result, 'raw') else str(result)
        
        # Forsøk å kompilere til PDF
        from app.core.compiler import DocumentCompiler
        compiler = DocumentCompiler()
        
        worksheet_pdf = None
        if config.document_format.value == "typst":
            # For nå, kompiler uten figurer (hybrid kommer i neste steg)
            # Vi må konvertere fra async til sync for FastAPI endepunktet hvis det ikke er async
            import asyncio
            # Siden vi er i en async def, kan vi bruke await
            res = await compiler.compile_hybrid(final_code, [])
            if res.success:
                worksheet_pdf = res.pdf_base64
        
        return GenerationResponse(
            success=True,
            worksheet_pdf=worksheet_pdf,
            source_code=final_code,
            metadata={"klassetrinn": request.klassetrinn, "emne": request.emne}
        )
        
    except Exception as e:
        logger.error(f"Generering feilet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generering feilet: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "v2.0-vgs"}
