import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from crewai import Crew, Process
from app.models.core import MaterialConfig, MathBlock
from app.services.agents import MaTultimateAgents
from app.core.sanitizers import strip_markdown_fences

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

        # 2. Define tasks (simplified for now, following MateMaTeX pattern)
        # In a full implementation, these would be more detailed and potentially use LangGraph
        from crewai import Task

        plan_task = Task(
            description=(
                f"Planlegg innholdet for et {config.material_type} om {config.topic} for {config.grade}. "
                f"Inkluder: {'teori, ' if config.include_theory else ''}"
                f"{'eksempler, ' if config.include_examples else ''}"
                f"{config.num_exercises} oppgaver. "
                f"Vanskelighetsgrad: {config.difficulty}. "
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

        # 3. Run the crew
        crew = Crew(
            agents=[pedagogue, mathematician, editor],
            tasks=[plan_task, write_task, review_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        
        # 4. Process result
        raw_content = result.raw if hasattr(result, 'raw') else str(result)
        clean_content = strip_markdown_fences(raw_content)
        
        return {
            "content": clean_content,
            "format": config.output_format,
            "timestamp": datetime.now().isoformat(),
            "config": config.model_dump()
        }
