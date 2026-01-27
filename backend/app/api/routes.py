from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import MaterialRequest, GenerationResponse
from app.agents.orchestrator import IntelligentOrchestrator
from app.models.config import MaterialConfig
from app.tools.storage import save_to_history, get_history
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger("API")

@router.post("/generate")
async def generate_math_material(request: MaterialRequest, background_tasks: BackgroundTasks):
    """
    Starter generering i bakgrunnen for å unngå timeout.
    """
    logger.info(f"Starter bakgrunnsjobb for: {request.emne}")
    
    async def run_generation():
        try:
            config = MaterialConfig(
                klassetrinn=request.klassetrinn,
                emne=request.emne,
                kompetansemaal=request.kompetansemaal,
                differentiation=request.differentiation,
                include_answer_key=request.include_answer_key,
                document_format=request.document_format
            )
            
            orchestrator = IntelligentOrchestrator()
            crew = orchestrator.create_dynamic_crew(config)
            result = crew.kickoff()
            
            final_code = result.raw if hasattr(result, 'raw') else str(result)
            
            from app.core.compiler import DocumentCompiler, TypstTemplates
            compiler = DocumentCompiler()
            
            if config.document_format.value == "typst" and not final_code.strip().startswith("#set"):
                preamble = TypstTemplates.worksheet_header(
                    title=config.emne,
                    grade=config.klassetrinn,
                    topic=config.emne
                )
                final_code = preamble + "\n" + final_code

            worksheet_pdf = None
            if config.document_format.value == "typst":
                res = await compiler.compile_hybrid(final_code, [])
                if res.success:
                    worksheet_pdf = res.pdf_base64
            
            save_to_history(config, worksheet_pdf if worksheet_pdf else "", None, final_code)
            logger.info(f"Bakgrunnsjobb ferdig for: {request.emne}")
            
        except Exception as e:
            logger.error(f"Bakgrunnsgenerering feilet: {str(e)}")

    background_tasks.add_task(run_generation)
    
    return {
        "success": True, 
        "message": "Generering startet i bakgrunnen. Sjekk Oppgavebanken om et øyeblikk.",
        "status": "processing"
    }

@router.get("/history")
async def fetch_history(limit: int = 10):
    """Henter genereringshistorikken."""
    try:
        return get_history(limit)
    except Exception as e:
        logger.error(f"Kunne ikke hente historikk: {e}")
        return []

@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "v2.0-vgs"}
