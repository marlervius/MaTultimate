import os
import json
import logging
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process, LLM
from app.models.config import MaterialConfig
from app.prompts.orchestrator import ORCHESTRATOR_PROMPT

# Konfigurer logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

class OrchestratorAgent:
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
