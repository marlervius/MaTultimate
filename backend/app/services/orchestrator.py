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

class MaTultimateOrchestrator:
    """
    Orchestrator for MaTultimate that combines CrewAI and LangGraph concepts.
    """
    def __init__(self):
        self.agents_factory = MaTultimateAgents()

    def generate_material(self, config: MaterialConfig) -> GenerationResponse:
        """
        Generates math material based on the provided configuration.
        """
        start_time = time.time()
        worksheet_raw = ""
        try:
            # 1. Initialize agents
            pedagogue = self.agents_factory.pedagogue(config)
            mathematician = self.agents_factory.mathematician(config)
            editor = self.agents_factory.editor(config)
            solution_writer = self.agents_factory.solution_writer(config)

            # 2. Define tasks
            plan_task = Task(
                description=(
                    f"Planlegg innholdet for et matematikkmateriell om {config.emne} for {config.klassetrinn}. "
                    f"Antall oppgaver: {config.antall_oppgaver}. "
                    f"Differensiering: {config.differentiation.value}. "
                    f"Kompetansemål: {config.kompetansemaal}."
                ),
                expected_output="En detaljert disposisjon for innholdet.",
                agent=pedagogue
            )

            write_task = Task(
                description=(
                    f"Skriv det matematiske innholdet i {config.document_format.value} format. "
                    "Følg disposisjonen fra pedagogen nøye. "
                    "Sørg for korrekt matematisk notasjon og pedagogiske forklaringer."
                ),
                expected_output=f"Komplett matematisk innhold i {config.document_format.value}.",
                agent=mathematician,
                context=[plan_task]
            )

            review_task = Task(
                description=(
                    "Gå gjennom det genererte innholdet. Sjekk for matematiske feil, "
                    "pedagogisk flyt og korrekt formatering. Rett opp eventuelle feil."
                ),
                expected_output=f"Ferdigstilt og kvalitetssikret {config.document_format.value} innhold.",
                agent=editor,
                context=[write_task]
            )

            tasks = [plan_task, write_task, review_task]

            # Add solution task if requested
            solution_task = None
            if config.include_answer_key:
                solution_task = Task(
                    description=(
                        "Lag en komplett fasit for oppgavene generert i forrige steg. "
                        "Hver oppgave skal ha steg-for-steg utregning og forklaring. "
                        "Inkluder tittel, trinn og 'Kun for lærerbruk' i headingen."
                    ),
                    expected_output=f"Komplett fasit i {config.document_format.value} format.",
                    agent=solution_writer,
                    context=[write_task]
                )
                tasks.append(solution_task)

            # 3. Run the crew
            crew = Crew(
                agents=[pedagogue, mathematician, editor, solution_writer] if config.include_answer_key else [pedagogue, mathematician, editor],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )

            result = crew.kickoff()
            
            # 4. Process and sanitize result
            answer_key_raw = ""
            
            # Find outputs from specific tasks
            for task in tasks:
                if task.agent == editor:
                    worksheet_raw = task.output.raw if hasattr(task.output, 'raw') else str(task.output)
                elif task.agent == solution_writer:
                    answer_key_raw = task.output.raw if hasattr(task.output, 'raw') else str(task.output)

            # If worksheet_raw is still empty, fallback to result.raw if not answer_key
            if not worksheet_raw and not config.include_answer_key:
                worksheet_raw = result.raw if hasattr(result, 'raw') else str(result)

            worksheet_clean = strip_markdown_fences(worksheet_raw)
            answer_key_clean = strip_markdown_fences(answer_key_raw) if answer_key_raw else ""
            
            # 5. Compile to PDF
            worksheet_pdf = None
            answer_key_pdf = None
            
            if config.document_format == "latex":
                worksheet_pdf, err = compile_latex_to_pdf(worksheet_clean)
                if err: raise Exception(f"Worksheet compilation error: {err}")
                if config.include_answer_key and answer_key_clean:
                    answer_key_pdf, err = compile_latex_to_pdf(answer_key_clean)
                    if err: raise Exception(f"Answer key compilation error: {err}")
            elif config.document_format == "typst":
                worksheet_pdf, err = compile_typst_to_pdf(worksheet_clean)
                if err: raise Exception(f"Worksheet compilation error: {err}")
                if config.include_answer_key and answer_key_clean:
                    answer_key_pdf, err = compile_typst_to_pdf(answer_key_clean)
                    if err: raise Exception(f"Answer key compilation error: {err}")
            
            compilation_time = int((time.time() - start_time) * 1000)
                
            return GenerationResponse(
                success=True,
                worksheet_pdf=worksheet_pdf,
                answer_key_pdf=answer_key_pdf,
                source_code=worksheet_clean,
                answer_key_source=answer_key_clean,
                metadata={
                    "klassetrinn": config.klassetrinn,
                    "emne": config.emne,
                    "levels": 3 if config.differentiation == "three_levels" else 1
                },
                compilation_time_ms=compilation_time
            )

        except Exception as e:
            return GenerationResponse(
                success=False,
                error_message=str(e),
                raw_ai_output=worksheet_raw if worksheet_raw else None
            )
