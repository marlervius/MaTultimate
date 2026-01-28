import os
import json
import logging
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process, LLM
from app.models.config import MaterialConfig
from app.prompts.orchestrator import ORCHESTRATOR_PROMPT
from app.agents.pedagogy.vgs import VGSAgent
from app.agents.pedagogy.barneskole import BarneskoleAgent
from app.agents.pedagogy.mellomtrinn import MellomtrinnAgent
from app.agents.pedagogy.ungdomsskole import UngdomsskoleAgent
from app.agents.figur_agent import FigurAgent
from app.agents.redaktor_agent import RedaktorAgent
from app.core.sanitizer import strip_markdown_fences
# Konfigurer logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

class IntelligentOrchestrator:
    """
    Hovedhjernen i systemet. Analyserer forespørsler og lager en komplett produksjonsplan.
    """
    def __init__(self):
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("LLM_API_KEY")
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.1
        )

    def create_plan(self, config: MaterialConfig) -> Dict[str, Any]:
        """
        Genererer en strukturert produksjonsplan basert på input.
        """
        logger.info(f"Starter planlegging for: {config.emne} ({config.klassetrinn})")
        
        planner = Agent(
            role="Hovedorkestrator",
            goal="Analyser forespørselen og lag en komplett produksjonsplan.",
            backstory="Du er den øverste arkitekten for MaTultimate, ansvarlig for å velge riktig pedagogikk og teknologi.",
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
            expected_output="En detaljert produksjonsplan i JSON-format.",
            agent=planner
        )

        crew = Crew(agents=[planner], tasks=[plan_task], verbose=False)
        result = crew.kickoff()
        
        raw_output = result.raw if hasattr(result, 'raw') else str(result)
        try:
            # Rens JSON-output
            clean_json = raw_output.strip().replace("```json", "").replace("```", "").strip()
            plan = json.loads(clean_json)
            
            logger.info(f"Plan generert. Valgt format: {plan.get('format')}. Aldersnivå: {plan.get('aldersnivå')}")
            return plan
        except Exception as e:
            logger.error(f"Feil ved parsing av produksjonsplan: {e}")
            # Robust fallback
            return {
                "aldersnivå": "ungdomsskole",
                "format": "typst",
                "agenter_som_trengs": ["pedagog", "matematiker", "redaktør"],
                "figurbehov": []
            }

    def create_dynamic_crew(self, config: MaterialConfig) -> Crew:
        """
        Bygger et Crew basert på produksjonsplanen.
        """
        from app.core.curriculum import Klassetrinn, get_aldersnivaa, Aldersnivaa
        
        plan = self.create_plan(config)
        
        # Velg pedagog-agent basert på aldersnivå fra plan eller config
        aldersnivaa = plan.get("aldersnivå")
        
        # Fallback til curriculum-logikk hvis plan er uklar
        if not aldersnivaa or aldersnivaa == "ukjent":
            try:
                trinn_enum = Klassetrinn(config.klassetrinn.lower())
                aldersnivaa_enum = get_aldersnivaa(trinn_enum)
                aldersnivaa = aldersnivaa_enum.value
            except:
                aldersnivaa = "ungdomsskole"

        # Instansier riktig pedagog
        if "vgs" in aldersnivaa:
            pedagog_instance = VGSAgent(llm=self.llm)
        elif "barneskole_små" in aldersnivaa:
            pedagog_instance = BarneskoleAgent(llm=self.llm)
        elif "barneskole_store" in aldersnivaa:
            pedagog_instance = MellomtrinnAgent(llm=self.llm)
        else:
            pedagog_instance = UngdomsskoleAgent(llm=self.llm)
            
        pedagog = pedagog_instance.get_agent()

        # Hent andre agenter
        from app.services.agents import MaTultimateAgents
        agent_factory = MaTultimateAgents()
        
        matematiker = agent_factory.mathematician(config)
        # Legg til begrensninger for å hindre frys/looping
        matematiker.max_iter = 3
        matematiker.allow_delegation = False
        
        # Bruk den nye RedaktorAgent
        redaktor_instance = RedaktorAgent(llm=self.llm)
        redaktor = redaktor_instance.get_agent()
        
        figur_agent_instance = FigurAgent(llm=self.llm)
        figur_agent = figur_agent_instance.get_agent()

        agents = [pedagog, matematiker, redaktor, figur_agent]

        task1 = Task(
            description=f"Lag en pedagogisk plan for {config.emne} på nivå {config.klassetrinn}.",
            expected_output="En detaljert pedagogisk plan.",
            agent=pedagog
        )

        task2 = Task(
            description=f"Skriv {config.document_format.value}-kode basert på planen. VIKTIG: Returner KUN rå kode uten markdown fences eller forklaringer.",
            expected_output=f"Kompilerbar {config.document_format.value}-kode.",
            agent=matematiker,
            context=[task1]
        )

        task3 = Task(
            description="Kvalitetssikre koden og fjern markdown fences.",
            expected_output="Ren kode klar for kompilering.",
            agent=redaktor,
            context=[task2]
        )

        tasks = [task1, task2, task3]

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
