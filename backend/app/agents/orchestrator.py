import os
import json
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process, LLM
from app.models.config import MaterialConfig
from app.services.agents import MaTultimateAgents
from app.agents.pedagogy.factory import PedagogyAgentFactory
from app.core.format_selector import FormatSelector

ORCHESTRATOR_PROMPT = """
Du er hovedorkestratoren for MaTultimate. Analyser forespørselen og lag en komplett produksjonsplan.

INPUT:
- klassetrinn: {klassetrinn}
- emne: {emne}  
- kompetansemål: {kompetansemaal}
- differensiering: {differensiering}

BESTEM FØLGENDE:

## 1. ALDERSNIVÅ OG PEDAGOGISK TILNÆRMING
Klassifiser og beskriv tilnærming (BARNESKOLE, MELLOMTRINN, UNGDOMSSKOLE, VGS GRUNN, VGS AVANSERT).

## 2. FIGURANALYSE
Vurder hvert element: INGEN_FIGUR, ENKEL_FIGUR (Typst), KOMPLEKS_FIGUR (LaTeX/TikZ).

## 3. FORMATVALG
TYPST, LATEX eller HYBRID.

## 4. DIFFERENSIERINGSPLAN
Spesifiser fokus, støtte og tallområde for nivå 1, 2 og 3.

OUTPUT JSON:
{{
  "aldersnivå": "barneskole|mellomtrinn|ungdomsskole|vgs_grunn|vgs_avansert",
  "pedagogisk_profil": {{
    "språknivå": "...",
    "tallområde": "...",
    "abstraksjonsnivå": "..."
  }},
  "figurbehov": [
    {{"oppgave": 1, "type": "ingen|enkel|kompleks", "beskrivelse": "..."}}
  ],
  "format": "typst|latex|hybrid",
  "format_begrunnelse": "...",
  "differensiering": {{
    "nivå_1": {{"fokus": "...", "støtte": "...", "tallområde": "..."}},
    "nivå_2": {{"fokus": "...", "støtte": "...", "tallområde": "..."}},
    "nivå_3": {{"fokus": "...", "støtte": "...", "tallområde": "..."}}
  }},
  "agenter_som_trengs": ["pedagog", "matematiker", "figur", "løsning", "redaktør"]
}}
"""

class IntelligentOrchestrator:
    def __init__(self):
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("LLM_API_KEY")
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.1
        )
        self.agents_factory = MaTultimateAgents()
        self.pedagogy_factory = PedagogyAgentFactory(self.llm)
        self.format_selector = FormatSelector()

    def plan_production(self, config: MaterialConfig) -> Dict[str, Any]:
        """
        Kjører en planleggings-task for å generere den strukturerte produksjonsplanen.
        """
        planner_agent = Agent(
            role="Produksjonsplanlegger",
            goal="Lag en nøyaktig produksjonsplan for matematikkmateriell.",
            backstory="Du er arkitekten bak MaTultimate-systemet.",
            llm=self.llm,
            allow_delegation=False
        )

        plan_task = Task(
            description=ORCHESTRATOR_PROMPT.format(
                klassetrinn=config.klassetrinn,
                emne=config.emne,
                kompetansemaal=config.kompetansemaal,
                differensiering=config.differentiation.value
            ),
            expected_output="En JSON-formatert produksjonsplan.",
            agent=planner_agent
        )

        crew = Crew(agents=[planner_agent], tasks=[plan_task], verbose=True)
        result = crew.kickoff()
        
        raw_output = result.raw if hasattr(result, 'raw') else str(result)
        try:
            clean_json = raw_output.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Feil ved parsing av plan: {e}")
            return {
                "aldersnivå": "ungdomsskole",
                "format": "typst",
                "agenter_som_trengs": ["pedagog", "matematiker", "redaktør"],
                "figurbehov": []
            }

    def create_dynamic_crew(self, config: MaterialConfig) -> Crew:
        """
        Bygger en Crew dynamisk basert på den intelligente produksjonsplanen.
        """
        # 1. Lag produksjonsplan
        plan = self.plan_production(config)
        
        # 2. Velg format intelligent (overstyrer planen hvis nødvendig)
        format_decision = self.format_selector.analyze(plan)
        
        # 3. Hent spesialisert pedagog
        pedagogue = self.pedagogy_factory.get_agent(plan["aldersnivå"])
        
        # 4. Hent andre agenter
        mathematician = self.agents_factory.mathematician(config)
        editor = self.agents_factory.editor(config)
        
        agents = [pedagogue, mathematician, editor]
        tasks = []

        # 1. Planleggingstaske (Pedagog)
        plan_task = Task(
            description=(
                f"Lag en detaljert pedagogisk plan for {config.emne} basert på produksjonsplanen: {json.dumps(plan)}. "
                f"Format: {format_decision.format}. "
                f"Mål: {config.kompetansemaal}."
            ),
            expected_output="En detaljert disposisjon for innholdet.",
            agent=pedagogue
        )
        tasks.append(plan_task)

        # 2. Innholdsproduksjon (Matematiker)
        write_task = Task(
            description=(
                f"Skriv det matematiske innholdet i {format_decision.format} format. "
                "Følg den pedagogiske planen og bruk de spesifiserte tallområdene."
            ),
            expected_output="Ferdig matematisk innhold.",
            agent=mathematician,
            context=[plan_task]
        )
        tasks.append(write_task)

        # 3. Figur-generering (hvis nødvendig)
        needs_figures = any(f["type"] == "kompleks" for f in plan.get("figurbehov", []))
        if needs_figures:
            illustrator = self.agents_factory.figur_factory.get_agent()
            agents.append(illustrator)
            figure_task = Task(
                description="Generer TikZ/LaTeX-kode for alle komplekse figurer flagget i produksjonsplanen.",
                expected_output="TikZ-kode for figurer.",
                agent=illustrator,
                context=[plan_task]
            )
            tasks.append(figure_task)

        # 4. Kvalitetssikring (Redaktør)
        review_task = Task(
            description="Kvalitetssikre alt innhold og figurer. Rett opp feil autonomt.",
            expected_output="Et feilfritt sluttdokument.",
            agent=editor,
            context=[write_task] + ([tasks[-1]] if needs_figures else [])
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
