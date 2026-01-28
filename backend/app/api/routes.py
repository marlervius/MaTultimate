from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import MaterialRequest, GenerationResponse
from app.agents.orchestrator import IntelligentOrchestrator
from app.models.config import MaterialConfig
from app.tools.storage import save_to_history, get_history
import logging
import asyncio
import traceback
from typing import List

router = APIRouter()
logger = logging.getLogger("API")

@router.post("/generate")
async def generate_math_material(request: MaterialRequest, background_tasks: BackgroundTasks):
    """
    Starter generering i bakgrunnen for å unngå timeout.
    """
    logger.info(f"Mottatt forespørsel: {request.emne} ({request.klassetrinn})")
    
    def run_generation_sync():
        """Synkron funksjon som kjører i bakgrunnen."""
        try:
            logger.info(f"Bakgrunnsjobb starter for: {request.emne}")
            
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
            
            logger.info("Crew opprettet, starter kickoff...")
            result = crew.kickoff()
            logger.info("Crew kickoff ferdig!")
            
            final_code = result.raw if hasattr(result, 'raw') else str(result)
            
            # Rens koden for vanlige AI-feil
            from app.core.sanitizer import sanitize_typst_code
            if config.document_format.value == "typst":
                final_code = sanitize_typst_code(final_code)
            else:
                # For LaTeX, bare fjern markdown fences
                import re
                final_code = re.sub(r'```(?:typst|latex)?\n?', '', final_code)
                final_code = final_code.replace('```', '').strip()
            
            logger.info(f"Kode generert og renset ({len(final_code)} tegn), starter kompilering...")
            
            # Kompiler til PDF
            from app.core.compiler import DocumentCompiler, TypstTemplates
            compiler = DocumentCompiler()
            
            if config.document_format.value == "typst":
                # Fjern AI-generert preamble hvis den finnes, vi bruker vår egen
                lines = final_code.split('\n')
                content_lines = []
                skip_preamble = True
                for line in lines:
                    # Hopp over AI-genererte #set linjer i starten
                    if skip_preamble and line.strip().startswith('#set'):
                        continue
                    skip_preamble = False
                    content_lines.append(line)
                
                content = '\n'.join(content_lines).strip()
                
                # Legg til vår preamble
                preamble = TypstTemplates.worksheet_header(
                    title=config.emne,
                    grade=config.klassetrinn,
                    topic=config.emne
                )
                final_code = preamble + "\n" + content

            worksheet_pdf = None
            if config.document_format.value == "typst":
                # Kjør async kompilering synkront
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    res = loop.run_until_complete(compiler.compile_hybrid(final_code, []))
                    if res.success:
                        worksheet_pdf = res.pdf_base64
                        logger.info("PDF kompilert!")
                    else:
                        logger.warning(f"PDF-kompilering feilet: {res.log}")
                finally:
                    loop.close()
            
            save_to_history(config, worksheet_pdf if worksheet_pdf else "", None, final_code)
            logger.info(f"Bakgrunnsjobb FERDIG for: {request.emne}")
            
        except Exception as e:
            logger.error(f"Bakgrunnsgenerering feilet: {str(e)}")
            logger.error(traceback.format_exc())
            # Lagre feilet forsøk med feilmelding
            try:
                save_to_history(
                    MaterialConfig(
                        klassetrinn=request.klassetrinn,
                        emne=f"[FEILET] {request.emne}",
                        kompetansemaal=request.kompetansemaal
                    ),
                    "",
                    None,
                    f"% Generering feilet: {str(e)}"
                )
            except:
                pass

    background_tasks.add_task(run_generation_sync)
    
    return {
        "success": True, 
        "message": "Generering startet i bakgrunnen. Sjekk Oppgavebanken om 1-2 minutter.",
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
