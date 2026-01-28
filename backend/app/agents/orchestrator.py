import os
import logging
from crewai import Agent, Task, Crew, Process, LLM
from app.models.config import MaterialConfig

# Konfigurer logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

class IntelligentOrchestrator:
    """
    Forenklet orchestrator som genererer innhold direkte uten kompleks planlegging.
    """
    def __init__(self):
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("LLM_API_KEY")
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.3
        )

    def _get_aldersnivaa(self, klassetrinn: str) -> str:
        """Enkel logikk for å bestemme aldersnivå."""
        trinn = klassetrinn.lower()
        if trinn in ["1", "2", "3", "4"]:
            return "barneskole_smaa"
        elif trinn in ["5", "6", "7"]:
            return "mellomtrinn"
        elif trinn in ["8", "9", "10"]:
            return "ungdomsskole"
        else:  # VGS kurs
            return "vgs"

    def create_dynamic_crew(self, config: MaterialConfig) -> Crew:
        """
        Bygger et forenklet Crew med kun to agenter for pålitelig kjøring.
        """
        aldersnivaa = self._get_aldersnivaa(config.klassetrinn)
        logger.info(f"Starter generering: {config.emne} ({config.klassetrinn}) - Aldersnivå: {aldersnivaa}")
        
        # Direkte prompt basert på aldersnivå
        if aldersnivaa == "vgs":
            spraak_instruksjoner = "Bruk formelt matematisk språk med korrekt terminologi. Inkluder derivasjon, integrasjon eller andre VGS-konsepter der relevant."
        elif aldersnivaa == "ungdomsskole":
            spraak_instruksjoner = "Bruk matematisk presist språk med variabler. Inkluder bokstavregning og enkle funksjoner."
        elif aldersnivaa == "mellomtrinn":
            spraak_instruksjoner = "Introduser fagtermer gradvis. Bruk større tall, enkel brøk og desimaltall."
        else:
            spraak_instruksjoner = "Bruk enkelt språk med korte setninger. Hold deg til små, hele tall (1-100)."

        # === ENKEL TO-AGENT TILNÆRMING ===
        
        # Agent 1: Pedagog som lager oppgaver
        pedagog = Agent(
            role="Matematikklærer",
            goal=f"Lag differensierte matematikkoppgaver om {config.emne} for {config.klassetrinn}.",
            backstory=(
                f"Du er en erfaren matematikklærer i Norge som følger LK20. "
                f"{spraak_instruksjoner}\n\n"
                f"Kompetansemål: {config.kompetansemaal}"
            ),
            llm=self.llm,
            allow_delegation=False,
            max_iter=2
        )

        # Agent 2: Skribent som formaterer til Typst/LaTeX
        skribent = Agent(
            role="Dokumentskriver",
            goal=f"Konverter oppgavene til ren {config.document_format.value}-kode.",
            backstory=(
                f"Du er ekspert på å skrive {config.document_format.value}-dokumenter. "
                "Du returnerer ALLTID kun rå kode uten markdown fences (```). "
                "Koden må kunne kompileres direkte.\n\n"
                "TYPST-REGLER (VIKTIG!):\n"
                "- Overskrifter: #heading(level: 1)[Tekst]\n"
                "- Matematikk inline: $x^2 + 2x + 1$\n"
                "- Matematikk utstilt: $ x^2 + 2x + 1 $ (med mellomrom)\n"
                "- Brøk: $frac(a, b)$ IKKE \\frac{a}{b}\n"
                "- Potens: $x^2$ eller $x^(2n)$\n"
                "- Sideskift: #pagebreak()\n"
                "- Fet tekst: *tekst* eller #strong[tekst]\n"
                "- Kursiv: _tekst_ eller #emph[tekst]\n"
                "- IKKE bruk LaTeX-kommandoer som \\frac, \\sqrt\n"
                "- IKKE definer egne variabler med #let med mindre nødvendig"
            ),
            llm=self.llm,
            allow_delegation=False,
            max_iter=2
        )

        # Task 1: Lag oppgaver
        diff_instruksjon = ""
        if config.differentiation.value == "three_levels":
            diff_instruksjon = (
                "Lag TRE nivåer:\n"
                "- Nivå 1: Enklest, med hint og støtte\n"
                "- Nivå 2: Middels, standard pensum\n"
                "- Nivå 3: Utfordring, krever dypere forståelse\n"
                "5-6 oppgaver per nivå."
            )
        else:
            diff_instruksjon = "Lag 8 varierte oppgaver med stigende vanskelighetsgrad."

        task1 = Task(
            description=(
                f"Lag matematikkoppgaver om {config.emne} for {config.klassetrinn}.\n\n"
                f"{diff_instruksjon}\n\n"
                "Output: En strukturert liste med oppgaver."
            ),
            expected_output="Liste med matematikkoppgaver.",
            agent=pedagog
        )

        # Task 2: Skriv dokument
        task2 = Task(
            description=(
                f"Konverter oppgavene til et komplett {config.document_format.value}-dokument.\n\n"
                "VIKTIG:\n"
                "- Returner KUN rå kode, ingen forklaringer\n"
                "- INGEN markdown fences (```)\n"
                "- Dokumentet må kompilere direkte"
            ),
            expected_output=f"Ren {config.document_format.value}-kode.",
            agent=skribent,
            context=[task1]
        )

        return Crew(
            agents=[pedagog, skribent],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=True
        )
