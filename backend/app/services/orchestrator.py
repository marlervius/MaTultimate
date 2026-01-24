import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from crewai import Crew, Process
from app.models.core import MaterialConfig, MathBlock
from app.services.agents import MaTultimateAgents
from app.core.sanitizers import strip_markdown_fences
from app.core.compiler import compile_latex_to_pdf, compile_typst_to_pdf

class MaTultimateOrchestrator:
    """
    Orchestrator for MaTultimate that combines CrewAI and LangGraph concepts.
    """
    def __init__(self):
        self.agents_factory = MaTultimateAgents()

    def generate_material(self, config: MaterialConfig) -> Dict[str, Any]:
        """
        Generates math material based on the provided configuration.
        """
        # 1. Initialize agents
        pedagogue = self.agents_factory.pedagogue(config)
        mathematician = self.agents_factory.mathematician(config)
        editor = self.agents_factory.editor(config)
        solution_writer = self.agents_factory.solution_writer(config)

        # 2. Define tasks
        from crewai import Task

        plan_task = Task(
            description=(
                f"Planlegg innholdet for et {config.material_type} om {config.topic} for {config.grade}. "
                f"Inkluder: {'teori, ' if config.include_theory else ''}"
                f"{'eksempler, ' if config.include_examples else ''}"
                f"{config.num_exercises} oppgaver. "
                f"Vanskelighetsgrad: {config.difficulty}. "
                f"Differensiering: {config.differentiation}. "
                f"Kompetansemål: {', '.join(config.competency_goals)}."
            ),
            expected_output="En detaljert disposisjon for innholdet.",
            agent=pedagogue
        )

        write_task = Task(
            description=(
                f"Skriv det matematiske innholdet i {config.output_format} format. "
                "Følg disposisjonen fra pedagogen nøye. "
                "Sørg for korrekt matematisk notasjon og pedagogiske forklaringer."
            ),
            expected_output=f"Komplett matematisk innhold i {config.output_format}.",
            agent=mathematician,
            context=[plan_task]
        )

        review_task = Task(
            description=(
                "Gå gjennom det genererte innholdet. Sjekk for matematiske feil, "
                "pedagogisk flyt og korrekt formatering. Rett opp eventuelle feil."
            ),
            expected_output=f"Ferdigstilt og kvalitetssikret {config.output_format} innhold.",
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
                expected_output=f"Komplett fasit i {config.output_format} format.",
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
        # The result of the crew is typically the output of the LAST task
        # If we have a solution task, we need to extract both
        
        worksheet_raw = ""
        answer_key_raw = ""
        
        # CrewAI result.raw is the last task's output
        if config.include_answer_key:
            answer_key_raw = result.raw
            # We need to find the output of the review_task
            # In current CrewAI, we can access task outputs
            for task in tasks:
                if task.agent == editor:
                    worksheet_raw = task.output.raw
        else:
            worksheet_raw = result.raw

        worksheet_clean = strip_markdown_fences(worksheet_raw)
        answer_key_clean = strip_markdown_fences(answer_key_raw) if answer_key_raw else ""
        
        # 5. Compile to PDF
        worksheet_pdf = None
        answer_key_pdf = None
        compilation_error = None
        
        if config.output_format == "latex":
            worksheet_pdf, err = compile_latex_to_pdf(worksheet_clean)
            if err: compilation_error = f"Worksheet: {err}"
            if config.include_answer_key and answer_key_clean:
                answer_key_pdf, err = compile_latex_to_pdf(answer_key_clean)
                if err: compilation_error = (compilation_error or "") + f" | Answer Key: {err}"
        elif config.output_format == "typst":
            worksheet_pdf, err = compile_typst_to_pdf(worksheet_clean)
            if err: compilation_error = f"Worksheet: {err}"
            if config.include_answer_key and answer_key_clean:
                answer_key_pdf, err = compile_typst_to_pdf(answer_key_clean)
                if err: compilation_error = (compilation_error or "") + f" | Answer Key: {err}"
            
        return {
            "content": worksheet_clean,
            "answer_key_content": answer_key_clean,
            "format": config.output_format,
            "pdf_base64": worksheet_pdf,
            "answer_key_pdf_base64": answer_key_pdf,
            "compilation_error": compilation_error,
            "timestamp": datetime.now().isoformat(),
            "config": config.model_dump()
        }
