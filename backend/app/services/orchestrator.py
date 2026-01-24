import os
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from crewai import Crew, Process, Task
from app.models.config import MaterialConfig, GenerationResponse
from app.services.agents import MaTultimateAgents
from app.core.sanitizers import strip_markdown_fences
from app.core.compiler import compile_latex_to_pdf, compile_typst_to_pdf

from app.models.config import MaterialConfig, GenerationResponse
from app.agents.orchestrator import IntelligentOrchestrator
from app.core.compiler import compile_latex_to_pdf, compile_typst_to_pdf
from app.core.sanitizers import strip_markdown_fences
import time
from datetime import datetime

class MaTultimateOrchestrator:
    def __init__(self):
        self.brain = IntelligentOrchestrator()

    def generate_material(self, config: MaterialConfig) -> GenerationResponse:
        start_time = time.time()
        try:
            # Bruk den intelligente hjernen til å bygge crewet
            crew = self.brain.create_dynamic_crew(config)
            result = crew.kickoff()
            
            # Prosesser resultater (forenklet for nå, bør utvides for hybrid pipeline)
            worksheet_raw = ""
            answer_key_raw = ""
            
            # Finn utdata fra oppgavene
            for task in crew.tasks:
                if "Kvalitetssikre" in task.description:
                    worksheet_raw = task.output.raw if hasattr(task.output, 'raw') else str(task.output)
                elif "Fasit" in task.description or "løsninger" in task.description:
                    answer_key_raw = task.output.raw if hasattr(task.output, 'raw') else str(task.output)

            if not worksheet_raw:
                worksheet_raw = result.raw if hasattr(result, 'raw') else str(result)

            worksheet_clean = strip_markdown_fences(worksheet_raw)
            answer_key_clean = strip_markdown_fences(answer_key_raw) if answer_key_raw else ""
            
            # Kompilering
            worksheet_pdf = None
            answer_key_pdf = None
            
            if config.document_format.value == "latex":
                worksheet_pdf, err = compile_latex_to_pdf(worksheet_clean)
                if config.include_answer_key and answer_key_clean:
                    answer_key_pdf, _ = compile_latex_to_pdf(answer_key_clean)
            else:
                worksheet_pdf, err = compile_typst_to_pdf(worksheet_clean)
                if config.include_answer_key and answer_key_clean:
                    answer_key_pdf, _ = compile_typst_to_pdf(answer_key_clean)
            
            return GenerationResponse(
                success=True,
                worksheet_pdf=worksheet_pdf,
                answer_key_pdf=answer_key_pdf,
                source_code=worksheet_clean,
                answer_key_source=answer_key_clean,
                metadata={"engine": "intelligent_orchestrator_v1"},
                compilation_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return GenerationResponse(success=False, error_message=str(e))
