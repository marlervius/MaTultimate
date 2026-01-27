from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import MaterialRequest, GenerationResponse
from app.agents.orchestrator import IntelligentOrchestrator
from app.models.config import MaterialConfig
from app.tools.storage import save_to_history, get_history
import logging
from typing import List

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
        from app.core.compiler import DocumentCompiler, TypstTemplates
        compiler = DocumentCompiler()
        
        # Legg til preamble hvis det mangler (agenter glemmer det ofte)
        if config.document_format.value == "typst" and not final_code.strip().startswith("#set"):
            preamble = TypstTemplates.worksheet_header(
                title=config.emne,
                grade=config.klassetrinn,
                topic=config.emne
            )
            final_code = preamble + "\n" + final_code

        worksheet_pdf = None
        if config.document_format.value == "typst":
            import asyncio
            # TODO: Trekk ut figurer fra koden hvis de finnes
            res = await compiler.compile_hybrid(final_code, [])
            if res.success:
                worksheet_pdf = res.pdf_base64
            else:
                logger.error(f"Kompilering feilet: {res.log}")
        
        # Lagre til historikk (Gjør dette asynkront eller etterpå)
        try:
            save_to_history(config, worksheet_pdf if worksheet_pdf else "", None, final_code)
        except Exception as e:
            logger.error(f"Kunne ikke lagre til historikk: {e}")
        
        return GenerationResponse(
            success=True,
            worksheet_pdf=worksheet_pdf,
            source_code=final_code,
            metadata={"klassetrinn": request.klassetrinn, "emne": request.emne}
        )
        
    except Exception as e:
        logger.error(f"Generering feilet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generering feilet: {str(e)}")

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
