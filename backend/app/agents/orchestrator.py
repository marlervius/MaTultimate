import os
import logging
import json
from crewai import Agent, Task, Crew, Process, LLM
from app.models.config import MaterialConfig
from typing import List, Dict, Any

# Konfigurer logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

# Emner som typisk trenger grafer/figurer
EMNER_MED_FIGURBEHOV = [
    "lineær", "funksjon", "graf", "koordinat", "derivasjon", "integral",
    "areal", "geometri", "trekant", "sirkel", "vektor", "trigonometri",
    "statistikk", "normalfordeling", "regresjon", "vekst", "eksponential",
    "logaritme", "polynom", "andregrads", "parabel"
]

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
    
    def _needs_figures(self, emne: str, klassetrinn: str) -> bool:
        """Sjekker om emnet typisk trenger figurer."""
        emne_lower = emne.lower()
        # Sjekk om noen nøkkelord matcher
        for keyword in EMNER_MED_FIGURBEHOV:
            if keyword in emne_lower:
                return True
        # VGS-emner trenger ofte figurer
        if klassetrinn.lower() in ["r1", "r2", "s1", "s2", "1t"]:
            return True
        return False
    
    def _generate_figure_specs(self, emne: str, klassetrinn: str) -> List[Dict[str, Any]]:
        """Genererer spesifikasjoner for figurer basert på emne."""
        figures = []
        emne_lower = emne.lower()
        
        # Lineære funksjoner
        if "lineær" in emne_lower or "funksjon" in emne_lower:
            figures.append({
                "id": "fig_linear",
                "type": "funksjonsplot",
                "description": "Koordinatsystem med lineær funksjon",
                "functions": ["2*x + 1", "-x + 3"],
                "x_range": [-4, 4],
                "y_range": [-3, 7],
                "show_grid": True,
                "labels": ["f(x) = 2x + 1", "g(x) = -x + 3"]
            })
        
        # Andregrads / Parabel
        if "andregr" in emne_lower or "parabel" in emne_lower or "kvadrat" in emne_lower:
            figures.append({
                "id": "fig_parabola",
                "type": "funksjonsplot",
                "description": "Parabel med toppunkt markert",
                "functions": ["x**2 - 4*x + 3"],
                "x_range": [-1, 5],
                "y_range": [-2, 6],
                "show_grid": True,
                "mark_roots": True
            })
        
        # Derivasjon / Tangent
        if "derivasjon" in emne_lower or "tangent" in emne_lower:
            figures.append({
                "id": "fig_tangent",
                "type": "tangent",
                "description": "Funksjon med tangentlinje",
                "function": "x**2",
                "tangent_x": 1,
                "x_range": [-2, 3],
                "y_range": [-1, 5]
            })
        
        # Areal / Integral
        if "areal" in emne_lower or "integral" in emne_lower:
            figures.append({
                "id": "fig_area",
                "type": "areal_under",
                "description": "Skravert areal under kurve",
                "function": "x**2",
                "a": 0,
                "b": 2,
                "x_range": [-1, 3],
                "y_range": [-0.5, 5]
            })
        
        # Statistikk / Normalfordeling
        if "normal" in emne_lower or "statistikk" in emne_lower:
            figures.append({
                "id": "fig_normal",
                "type": "normalfordeling",
                "description": "Normalfordelingskurve",
                "mu": 0,
                "sigma": 1,
                "shade_from": -1,
                "shade_to": 1
            })
        
        return figures

    def generate_figures(self, config: MaterialConfig) -> List[Dict[str, str]]:
        """
        Genererer TikZ-kode for figurer basert på emnet.
        Returnerer liste med {"id": "...", "latex": "tikz-kode"}.
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        if not self._needs_figures(config.emne, config.klassetrinn):
            logger.info("Ingen figurer trengs for dette emnet")
            return []
        
        figure_specs = self._generate_figure_specs(config.emne, config.klassetrinn)
        if not figure_specs:
            return []
        
        logger.info(f"Genererer {len(figure_specs)} figurer...")
        figur_agent = FigurAgent(llm=self.llm)
        figures = []
        
        for spec in figure_specs:
            try:
                fig_type = spec.get("type", "funksjonsplot")
                
                if fig_type == "funksjonsplot":
                    request = FigurRequest(
                        figur_type=FigurType.FUNKSJONSPLOT,
                        funksjon=spec.get("functions", ["x"])[0] if spec.get("functions") else "x",
                        x_range=tuple(spec.get("x_range", [-5, 5])),
                        y_range=tuple(spec.get("y_range", [-5, 5])) if spec.get("y_range") else None
                    )
                elif fig_type == "tangent":
                    request = FigurRequest(
                        figur_type=FigurType.FUNKSJONSPLOT_TANGENT,
                        funksjon=spec.get("function", "x**2"),
                        tangent_x=spec.get("tangent_x", 1),
                        x_range=tuple(spec.get("x_range", [-5, 5])),
                        y_range=tuple(spec.get("y_range", [-5, 5])) if spec.get("y_range") else None
                    )
                elif fig_type == "areal_under":
                    request = FigurRequest(
                        figur_type=FigurType.AREAL_UNDER_KURVE,
                        funksjon=spec.get("function", "x**2"),
                        nedre_grense=spec.get("a", 0),
                        ovre_grense=spec.get("b", 2),
                        x_range=tuple(spec.get("x_range", [-5, 5])),
                        y_range=tuple(spec.get("y_range", [-5, 5])) if spec.get("y_range") else None
                    )
                elif fig_type == "normalfordeling":
                    request = FigurRequest(
                        figur_type=FigurType.NORMALFORDELING,
                        mu=spec.get("mu", 0),
                        sigma=spec.get("sigma", 1),
                        skraver_fra=spec.get("shade_from"),
                        skraver_til=spec.get("shade_to")
                    )
                else:
                    continue
                
                tikz_code = figur_agent.generer(request)
                figures.append({
                    "id": spec["id"],
                    "latex": tikz_code,
                    "description": spec.get("description", "")
                })
                logger.info(f"Figur {spec['id']} generert")
                
            except Exception as e:
                logger.warning(f"Kunne ikke generere figur {spec.get('id')}: {e}")
        
        return figures

    def create_dynamic_crew(self, config: MaterialConfig) -> Crew:
        """
        Bygger et forenklet Crew med kun to agenter for pålitelig kjøring.
        """
        aldersnivaa = self._get_aldersnivaa(config.klassetrinn)
        is_hybrid = config.document_format.value == "hybrid"
        logger.info(f"Starter generering: {config.emne} ({config.klassetrinn}) - Aldersnivå: {aldersnivaa} - Hybrid: {is_hybrid}")
        
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

        # Figur-instruksjoner for hybrid modus
        figur_instruksjoner = ""
        if is_hybrid and self._needs_figures(config.emne, config.klassetrinn):
            figur_instruksjoner = (
                "\n\nFIGURER (Hybrid-modus aktivert):\n"
                "Legg inn figurer der de er pedagogisk nyttige med denne syntaksen:\n"
                "#align(center)[#image(\"figurer/fig_linear.png\", width: 80%)]\n"
                "#v(0.5em)\n"
                "#text(size: 0.9em, fill: gray)[_Figur: Koordinatsystem med lineære funksjoner_]\n\n"
                "Tilgjengelige figurer:\n"
                "- fig_linear.png - Koordinatsystem med lineære funksjoner\n"
                "- fig_parabola.png - Parabel/andregradsfunksjon\n"
                "- fig_tangent.png - Funksjon med tangentlinje\n"
                "- fig_area.png - Areal under kurve\n"
                "- fig_normal.png - Normalfordelingskurve\n"
                "Plasser figurer på nivå 1 for visuell støtte."
            )

        # Agent 2: Skribent som formaterer til Typst/LaTeX
        skribent = Agent(
            role="Dokumentskriver",
            goal=f"Konverter oppgavene til profesjonell lærebok-stil Typst-kode.",
            backstory=(
                "Du er ekspert på å skrive Typst-dokumenter som ser ut som profesjonelle lærebøker. "
                "Du returnerer ALLTID kun rå kode uten markdown fences (```). "
                "Koden må kunne kompileres direkte.\n\n"
                "BRUK DISSE FERDIGDEFINERTE BOKSENE:\n"
                "- #oppgave_box(\"1a\", [oppgavetekst], nivaa: 1)  // nivaa: 1, 2 eller 3\n"
                "- #eksempel_box(\"Tittel\", [innhold])\n"
                "- #definisjon_box([definisjon])\n"
                "- #hint_box([hint-tekst])\n"
                "- #formel_box([$formel$])\n"
                "- #nivaa_header(1)  // For nivå-overskrift (1, 2 eller 3)\n\n"
                "TYPST MATEMATIKK-SYNTAKS:\n"
                "- Inline: $x^2 + 2x + 1$\n"
                "- Utstilt: $ x^2 + 2x + 1 $\n"
                "- Brøk: $frac(a, b)$\n"
                "- Grenser: $lim_(x -> 0)$\n"
                "- Integral: $integral f(x) dif x$\n"
                "- Multiplikasjon: $a cdot b$\n"
                "- Enheter: $5 \"m\"$ (mellomrom før enhet)\n"
                "- DESIMALTALL: $2.5$ IKKE $2,5$ (punktum, ikke komma!)\n\n"
                "STRUKTUR FOR DIFFERENSIERTE OPPGAVER:\n"
                "#nivaa_header(1)  // Grunnleggende\n"
                "[oppgaver med nivaa: 1]\n"
                "#pagebreak()\n"
                "#nivaa_header(2)  // Middels\n"
                "[oppgaver med nivaa: 2]\n"
                "#pagebreak()\n"
                "#nivaa_header(3)  // Utfordring\n"
                "[oppgaver med nivaa: 3]\n\n"
                "VIKTIG:\n"
                "- IKKE definer egne #let variabler (de er allerede definert)\n"
                "- IKKE bruk LaTeX-kommandoer som \\frac\n"
                "- Bruk #pagebreak() mellom nivåer"
                f"{figur_instruksjoner}"
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
