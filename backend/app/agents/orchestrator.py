import os
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process, LLM
from app.models.config import MaterialConfig, GenerationResponse
from app.services.agents import MaTultimateAgents
from datetime import datetime

class IntelligentOrchestrator:
    """
    Hjernen i systemet. Analyserer forespørsler og tar autonome beslutninger
    om hvilke agenter som trengs og hvordan arbeidsflyten skal se ut.
    """
    def __init__(self):
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("LLM_API_KEY")
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.1 # Lav temperatur for konsistente beslutninger
        )
        self.agents_factory = MaTultimateAgents()

    def analyze_request(self, config: MaterialConfig) -> Dict[str, Any]:
        """
        Analyserer MaterialConfig for å bestemme kompleksitet og behov.
        """
        klassetrinn = getattr(config, 'klassetrinn', '8')
        is_vgs = any(v in str(klassetrinn).lower() for v in ["vg", "r1", "r2", "s1", "s2", "1t", "1p"])
        
        needs_figures = config.include_visuals or is_vgs
        needs_differentiation = config.differentiation == "three_levels"
        
        return {
            "is_vgs": is_vgs,
            "needs_figures": needs_figures,
            "needs_differentiation": needs_differentiation,
            "complexity_score": 3 if is_vgs else (2 if needs_differentiation else 1)
        }

    def create_dynamic_crew(self, config: MaterialConfig) -> Crew:
        """
        Bygger en Crew dynamisk basert på analysen.
        """
        analysis = self.analyze_request(config)
        
        # Hent agenter
        pedagogue = self.agents_factory.pedagogue(config)
        mathematician = self.agents_factory.mathematician(config)
        editor = self.agents_factory.editor(config)
        
        agents = [pedagogue, mathematician, editor]
        tasks = []

        # 1. Planleggingstaske
        plan_task = Task(
            description=(
                f"Analyser behovet for {config.emne} på trinn {config.klassetrinn}. "
                f"Lag en autonom plan. {'Inkluder VGS-spesifikk metodikk.' if analysis['is_vgs'] else ''} "
                f"{'Flagg behov for figurer med [FIGUR: type].' if analysis['needs_figures'] else ''}"
            ),
            expected_output="En strategisk plan for innholdsproduksjon.",
            agent=pedagogue
        )
        tasks.append(plan_task)

        # 2. Innholdsproduksjon
        write_task = Task(
            description=(
                f"Produser det matematiske innholdet i {config.document_format.value} format. "
                "Ta selvstendige valg om oppgavedesign basert på planen."
            ),
            expected_output="Ferdig matematisk innhold.",
            agent=mathematician,
            context=[plan_task]
        )
        tasks.append(write_task)

        # 3. Figur-generering (hvis nødvendig)
        if analysis['needs_figures']:
            illustrator = self.agents_factory.figur_factory.get_agent()
            agents.append(illustrator)
            figure_task = Task(
                description="Generer TikZ/LaTeX-kode for alle figurer flagget i planen.",
                expected_output="TikZ-kode for figurer.",
                agent=illustrator,
                context=[plan_task]
            )
            tasks.append(figure_task)

        # 4. Kvalitetssikring
        review_task = Task(
            description="Kvalitetssikre alt innhold og figurer. Rett opp feil autonomt.",
            expected_output="Et feilfritt sluttdokument.",
            agent=editor,
            context=[write_task] + ([tasks[-1]] if analysis['needs_figures'] else [])
        )
        tasks.append(review_task)

        # 5. Fasit (hvis ønsket)
        if config.include_answer_key:
            solution_writer = self.agents_factory.solution_writer(config)
            agents.append(solution_writer)
            solution_task = Task(
                description="Lag en pedagogisk fasit basert på det ferdige innholdet.",
                expected_output="Komplett fasit.",
                agent=solution_writer,
                context=[review_task]
            )
            tasks.append(solution_task)

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
