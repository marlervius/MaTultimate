"""
MaTultimate VGS Agent
=====================
Spesialisert agent for VGS-matematikk (1T, R1, R2, S1, S2).

Denne agenten:
- Forstår LK20-kompetansemål
- Genererer pedagogisk tilpassede oppgaver
- Bruker SymPy for matematisk verifisering
- Produserer Typst/LaTeX-kode av høy kvalitet
"""

from typing import Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
import json

from ..core.math_engine import MathEngine, VGSMathGenerator, ProblemVariant, StepByStepSolution
from ..core.compiler import TypstTemplates


class VGSKurs(str, Enum):
    """VGS matematikkurs."""
    T1 = "1t"
    P1 = "1p"
    P2 = "2p"
    R1 = "r1"
    S1 = "s1"
    R2 = "r2"
    S2 = "s2"


class Emne(str, Enum):
    """Hovedemner i VGS-matematikk."""
    ALGEBRA = "algebra"
    FUNKSJONER = "funksjoner"
    DERIVASJON = "derivasjon"
    INTEGRASJON = "integrasjon"
    VEKTORER = "vektorer"
    SANNSYNLIGHET = "sannsynlighet"
    STATISTIKK = "statistikk"
    GEOMETRI = "geometri"
    OKONOMI = "økonomi"


@dataclass
class OppgaveConfig:
    """Konfigurasjon for oppgavegenerering."""
    kurs: VGSKurs
    emne: Emne
    kompetansemaal: Optional[str] = None
    antall_oppgaver: int = 6
    differensiering: bool = True
    inkluder_fasit: bool = True
    inkluder_figurer: bool = True
    sprak: str = "nb"  # Norsk bokmål


@dataclass
class Oppgave:
    """En enkelt oppgave."""
    nummer: str  # "1a", "1b", "2", etc.
    tekst: str  # Oppgaveteksten
    latex_problem: str  # Matematisk uttrykk i LaTeX
    latex_svar: str  # Svaret i LaTeX
    steg_for_steg: Optional[list[dict]] = None
    hint: Optional[str] = None
    figur_trengs: bool = False
    figur_beskrivelse: Optional[str] = None
    vanskelighetsgrad: float = 0.5  # 0.0 - 1.0


@dataclass
class Oppgavesett:
    """Et komplett oppgavesett med tre nivåer."""
    tittel: str
    kurs: str
    emne: str
    kompetansemaal: str
    
    nivaa_1: list[Oppgave] = field(default_factory=list)
    nivaa_2: list[Oppgave] = field(default_factory=list)
    nivaa_3: list[Oppgave] = field(default_factory=list)
    
    fasit: Optional[dict] = None
    
    # Metadata
    figurer_trengs: list[dict] = field(default_factory=list)
    format_anbefaling: str = "typst"


class VGSAgent:
    """
    Hovedagent for VGS-matematikk.
    
    Eksempel:
        agent = VGSAgent()
        oppgavesett = agent.generer_oppgavesett(
            kurs=VGSKurs.R1,
            emne=Emne.DERIVASJON,
            antall=6
        )
    """
    
    def __init__(self):
        self.math_engine = MathEngine()
        self.math_generator = VGSMathGenerator()
        
        # Emne-spesifikke konfigurasjoner
        self.emne_config = {
            Emne.DERIVASJON: {
                'nivaa_1_kategorier': ['polynomial_easy'],
                'nivaa_2_kategorier': ['chain_rule', 'product_rule'],
                'nivaa_3_kategorier': ['combined', 'quotient_rule'],
                'figur_sannsynlighet': 0.3,  # 30% sjanse for figur
                'typiske_figurer': ['funksjonsplot_med_tangent', 'fortegnslinje'],
            },
            Emne.INTEGRASJON: {
                'nivaa_1_kategorier': ['polynomial'],
                'nivaa_2_kategorier': ['exponential', 'trigonometric'],
                'nivaa_3_kategorier': ['substitution'],
                'figur_sannsynlighet': 0.5,
                'typiske_figurer': ['areal_under_kurve', 'areal_mellom_kurver'],
            },
            Emne.FUNKSJONER: {
                'nivaa_1_kategorier': ['polynomial_easy'],
                'nivaa_2_kategorier': ['polynomial_medium'],
                'nivaa_3_kategorier': ['combined'],
                'figur_sannsynlighet': 0.7,
                'typiske_figurer': ['funksjonsplot', 'nullpunkter_graf', 'ekstremalpunkt_graf'],
            },
        }
    
    def generer_oppgavesett(
        self,
        config: OppgaveConfig
    ) -> Oppgavesett:
        """
        Generer et komplett oppgavesett basert på konfigurasjon.
        
        Dette er hovedmetoden som orkestrerer hele genereringsprosessen.
        """
        # Hent emne-konfigurasjon
        emne_cfg = self.emne_config.get(config.emne, {})
        
        # Initialiser oppgavesett
        oppgavesett = Oppgavesett(
            tittel=self._generer_tittel(config),
            kurs=config.kurs.value.upper(),
            emne=config.emne.value.capitalize(),
            kompetansemaal=config.kompetansemaal or self._hent_standard_kompetansemaal(config)
        )
        
        if config.differensiering:
            # Generer tre nivåer
            oppgavesett.nivaa_1 = self._generer_nivaa(
                config, 1, 
                config.antall_oppgaver // 3 + 1
            )
            oppgavesett.nivaa_2 = self._generer_nivaa(
                config, 2,
                config.antall_oppgaver // 3 + 1
            )
            oppgavesett.nivaa_3 = self._generer_nivaa(
                config, 3,
                config.antall_oppgaver // 3
            )
        else:
            # Bare middels nivå
            oppgavesett.nivaa_2 = self._generer_nivaa(
                config, 2,
                config.antall_oppgaver
            )
        
        # Generer fasit
        if config.inkluder_fasit:
            oppgavesett.fasit = self._generer_fasit(oppgavesett)
        
        # Bestem format
        oppgavesett.format_anbefaling = self._bestem_format(oppgavesett)
        
        return oppgavesett
    
    def _generer_tittel(self, config: OppgaveConfig) -> str:
        """Generer en passende tittel for oppgavesettet."""
        emne_titler = {
            Emne.DERIVASJON: "Derivasjon",
            Emne.INTEGRASJON: "Integrasjon",
            Emne.FUNKSJONER: "Funksjoner",
            Emne.VEKTORER: "Vektorer",
            Emne.SANNSYNLIGHET: "Sannsynlighetsregning",
            Emne.STATISTIKK: "Statistikk",
            Emne.ALGEBRA: "Algebra",
            Emne.GEOMETRI: "Geometri",
            Emne.OKONOMI: "Økonomi",
        }
        return f"Arbeidsark: {emne_titler.get(config.emne, config.emne.value)}"
    
    def _hent_standard_kompetansemaal(self, config: OppgaveConfig) -> str:
        """Hent standard kompetansemål for kurset og emnet."""
        # Forenklet mapping - i produksjon ville dette komme fra curriculum.py
        maal_mapping = {
            (VGSKurs.R1, Emne.DERIVASJON): (
                "utlede derivasjonsreglene for polynomfunksjoner, bruke dem til å "
                "drøfte polynomfunksjoner og begrunne fremgangsmåter"
            ),
            (VGSKurs.R1, Emne.INTEGRASJON): (
                "gjøre rede for definisjonen av bestemt integral og bruke "
                "integrasjon til å beregne areal"
            ),
            (VGSKurs.R2, Emne.DERIVASJON): (
                "derivere sammensatte funksjoner ved hjelp av kjerneregelen, "
                "produktregelen og brøkregelen"
            ),
            (VGSKurs.R2, Emne.INTEGRASJON): (
                "beregne integraler ved hjelp av integrasjonsregler, "
                "delvis integrasjon og substitusjon"
            ),
        }
        return maal_mapping.get(
            (config.kurs, config.emne),
            f"Kompetansemål for {config.emne.value} i {config.kurs.value}"
        )
    
    def _generer_nivaa(
        self,
        config: OppgaveConfig,
        nivaa: int,
        antall: int
    ) -> list[Oppgave]:
        """Generer oppgaver for ett differensieringsnivå."""
        oppgaver = []
        
        # Map nivå til vanskelighetsgrad
        difficulty_map = {1: 0.2, 2: 0.5, 3: 0.8}
        difficulty = difficulty_map.get(nivaa, 0.5)
        
        if config.emne == Emne.DERIVASJON:
            oppgaver = self._generer_derivasjonsoppgaver(nivaa, antall, difficulty)
        elif config.emne == Emne.INTEGRASJON:
            oppgaver = self._generer_integrasjonsoppgaver(nivaa, antall, difficulty)
        elif config.emne == Emne.FUNKSJONER:
            oppgaver = self._generer_funksjonsoppgaver(nivaa, antall, difficulty)
        else:
            # Fallback - generiske oppgaver
            oppgaver = self._generer_generiske_oppgaver(nivaa, antall, difficulty)
        
        return oppgaver
    
    def _generer_derivasjonsoppgaver(
        self,
        nivaa: int,
        antall: int,
        difficulty: float
    ) -> list[Oppgave]:
        """Generer derivasjonsoppgaver med SymPy-verifisering."""
        oppgaver = []
        
        # Velg maler basert på nivå
        if nivaa == 1:
            # Enkle polynomer, potensregelen
            templates = [
                "{a}*x**{n}",
                "{a}*x**2 + {b}*x + {c}",
                "{a}*x**3",
            ]
            intro_tekst = "Deriver funksjonen. Bruk potensregelen."
            hints = [
                "Husk: $(x^n)' = n \\cdot x^{n-1}$",
                "Deriver ledd for ledd",
            ]
        elif nivaa == 2:
            # Produktregel, kjerneregel
            templates = [
                "x**{n} * exp(x)",
                "sin({a}*x)",
                "exp({a}*x)",
                "ln({a}*x + {b})",
                "({a}*x + {b})**{n}",
            ]
            intro_tekst = "Deriver funksjonen."
            hints = []
        else:
            # Kombinerte, krevende
            templates = [
                "x**{n} * sin(x)",
                "exp(x) / x**{n}",
                "ln(x**2 + {a})",
                "sin(x) * cos(x)",
                "({a}*x**2 + {b})**{n}",
            ]
            intro_tekst = "Deriver funksjonen. Vis tydelig hvilke regler du bruker."
            hints = []
        
        # Generer varianter med SymPy
        import random
        random.shuffle(templates)
        
        for i, template in enumerate(templates[:antall]):
            try:
                variants = self.math_engine.generate_derivative_variants(
                    template, 
                    num_variants=1, 
                    difficulty=difficulty
                )
                
                if variants:
                    v = variants[0]
                    
                    # SymPy har allerede verifisert at svaret er korrekt 
                    # under generering (den bruker diff() direkte), 
                    # så vi stoler på resultatet
                    oppgave = Oppgave(
                        nummer=f"{i+1}",
                        tekst=intro_tekst if i == 0 else "Deriver:",
                        latex_problem=f"f(x) = {v.problem_latex}",
                        latex_svar=f"f'(x) = {v.answer_latex}",
                        hint=random.choice(hints) if hints and nivaa == 1 else None,
                        vanskelighetsgrad=difficulty,
                        figur_trengs=(nivaa == 3 and random.random() < 0.3),
                        figur_beskrivelse="Graf av f(x) med tangentlinje" if nivaa == 3 else None
                    )
                    oppgaver.append(oppgave)
                        
            except Exception as e:
                # Logg feil, men fortsett
                print(f"Advarsel: Kunne ikke generere oppgave fra mal '{template}': {e}")
                continue
        
        # Legg til tekstoppgave på nivå 2 og 3
        if nivaa >= 2 and len(oppgaver) > 0:
            tekstoppgave = self._lag_derivasjons_tekstoppgave(nivaa)
            if tekstoppgave:
                oppgaver.append(tekstoppgave)
        
        return oppgaver
    
    def _lag_derivasjons_tekstoppgave(self, nivaa: int) -> Optional[Oppgave]:
        """Lag en tekstoppgave (anvendelse) for derivasjon."""
        if nivaa == 2:
            return Oppgave(
                nummer="T",
                tekst=(
                    "En ball kastes opp i lufta. Høyden $h$ (i meter) etter $t$ sekunder "
                    "er gitt ved $h(t) = 20t - 5t^2$.\n\n"
                    "a) Finn farten $v(t) = h'(t)$.\n"
                    "b) Når er farten lik null? Hva betyr dette?"
                ),
                latex_problem="h(t) = 20t - 5t^2",
                latex_svar="v(t) = 20 - 10t, \\quad t = 2",
                vanskelighetsgrad=0.5
            )
        elif nivaa == 3:
            return Oppgave(
                nummer="T",
                tekst=(
                    "En bedrift har inntektsfunksjonen $I(x) = 100x - x^2$ og "
                    "kostnadsfunksjonen $K(x) = 20 + 10x$, der $x$ er antall enheter.\n\n"
                    "a) Finn overskuddsfunksjonen $O(x) = I(x) - K(x)$.\n"
                    "b) For hvilken $x$-verdi er overskuddet størst?\n"
                    "c) Hva er det maksimale overskuddet?"
                ),
                latex_problem="I(x) = 100x - x^2, \\quad K(x) = 20 + 10x",
                latex_svar="O(x) = -x^2 + 90x - 20, \\quad x = 45, \\quad O(45) = 2005",
                vanskelighetsgrad=0.8
            )
        return None
    
    def _generer_integrasjonsoppgaver(
        self,
        nivaa: int,
        antall: int,
        difficulty: float
    ) -> list[Oppgave]:
        """Generer integrasjonsoppgaver."""
        oppgaver = []
        
        if nivaa == 1:
            templates = [
                "{a}*x**{n}",
                "{a}*x**2 + {b}*x",
                "{a}",
            ]
            intro_tekst = "Finn det ubestemte integralet."
        elif nivaa == 2:
            templates = [
                "{a}*exp({b}*x)",
                "{a}*sin({b}*x)",
                "{a}*cos({b}*x)",
            ]
            intro_tekst = "Integrer funksjonen."
        else:
            templates = [
                "x * exp(x**2)",
                "sin(x) * cos(x)",
                "x / (x**2 + {a})",
            ]
            intro_tekst = "Bruk substitusjon eller andre teknikker for å finne integralet."
        
        import random
        random.shuffle(templates)
        
        for i, template in enumerate(templates[:antall]):
            try:
                variants = self.math_generator.engine.generate_integral_variants(
                    template,
                    num_variants=1,
                    difficulty=difficulty
                )
                
                if variants:
                    v = variants[0]
                    oppgave = Oppgave(
                        nummer=f"{i+1}",
                        tekst=intro_tekst if i == 0 else "Integrer:",
                        latex_problem=f"\\int {v.problem_latex} \\, dx",
                        latex_svar=v.answer_latex,
                        vanskelighetsgrad=difficulty,
                        figur_trengs=(nivaa == 3 and i == 0),
                        figur_beskrivelse="Areal under kurven" if nivaa == 3 and i == 0 else None
                    )
                    oppgaver.append(oppgave)
                    
            except Exception as e:
                print(f"Advarsel: Kunne ikke generere integrasjonsoppgave: {e}")
                continue
        
        return oppgaver
    
    def _generer_funksjonsoppgaver(
        self,
        nivaa: int,
        antall: int,
        difficulty: float
    ) -> list[Oppgave]:
        """Generer oppgaver om funksjonsdrøfting."""
        oppgaver = []
        
        # Funksjonsdrøfting krever ofte figurer
        if nivaa == 1:
            funcs = ["x**2 - 4*x + 3", "x**2 - 9", "-x**2 + 6*x - 5"]
        elif nivaa == 2:
            funcs = ["x**3 - 3*x", "x**3 - 6*x**2 + 9*x", "x**4 - 2*x**2"]
        else:
            funcs = ["x**3 - 3*x**2 + 2", "x * exp(-x)", "(x**2 - 1) / x"]
        
        import random
        random.shuffle(funcs)
        
        for i, func in enumerate(funcs[:antall]):
            try:
                # Bruk math_engine for analyse
                extrema = self.math_engine.find_extrema(func)
                
                if nivaa == 1:
                    tekst = f"Gitt funksjonen $f(x) = {self.math_engine.to_latex(self.math_engine.parse_expression(func))}$.\n\na) Finn nullpunktene.\nb) Bestem fortegnene til $f(x)$."
                elif nivaa == 2:
                    tekst = f"Drøft funksjonen $f(x) = {self.math_engine.to_latex(self.math_engine.parse_expression(func))}$.\n\nFinn nullpunkter, ekstremalpunkter og skisser grafen."
                else:
                    tekst = f"Gjør en fullstendig drøfting av $f(x) = {self.math_engine.to_latex(self.math_engine.parse_expression(func))}$.\n\nInkluder vendepunkter og asymptotisk oppførsel."
                
                oppgave = Oppgave(
                    nummer=f"{i+1}",
                    tekst=tekst,
                    latex_problem=f"f(x) = {self.math_engine.to_latex(self.math_engine.parse_expression(func))}",
                    latex_svar=f"f'(x) = {extrema['f_prime']}, \\text{{ kritiske punkter: }} {', '.join(extrema['critical_points'])}",
                    vanskelighetsgrad=difficulty,
                    figur_trengs=True,
                    figur_beskrivelse=f"Graf av f(x) = {func}"
                )
                oppgaver.append(oppgave)
                
            except Exception as e:
                print(f"Advarsel: Kunne ikke generere funksjonsoppgave: {e}")
                continue
        
        return oppgaver
    
    def _generer_generiske_oppgaver(
        self,
        nivaa: int,
        antall: int,
        difficulty: float
    ) -> list[Oppgave]:
        """Fallback for emner som ikke har spesifikk generator."""
        return [
            Oppgave(
                nummer=f"{i+1}",
                tekst=f"Oppgave {i+1} for nivå {nivaa}",
                latex_problem="",
                latex_svar="",
                vanskelighetsgrad=difficulty
            )
            for i in range(antall)
        ]
    
    def _generer_fasit(self, oppgavesett: Oppgavesett) -> dict:
        """Generer fasit med steg-for-steg løsninger."""
        fasit = {
            'nivaa_1': [],
            'nivaa_2': [],
            'nivaa_3': [],
        }
        
        for nivaa_navn, oppgaver in [
            ('nivaa_1', oppgavesett.nivaa_1),
            ('nivaa_2', oppgavesett.nivaa_2),
            ('nivaa_3', oppgavesett.nivaa_3),
        ]:
            for oppgave in oppgaver:
                fasit_entry = {
                    'nummer': oppgave.nummer,
                    'svar': oppgave.latex_svar,
                }
                
                # Prøv å generere steg-for-steg
                if 'f(x) =' in oppgave.latex_problem and "f'(x)" in oppgave.latex_svar:
                    try:
                        # Ekstraher funksjonen
                        func_str = oppgave.latex_problem.replace('f(x) = ', '').strip()
                        # Fjern LaTeX-formatering for SymPy
                        func_clean = func_str.replace('\\cdot', '*').replace('^', '**')
                        
                        solution = self.math_engine.derivative_step_by_step(func_clean)
                        
                        fasit_entry['steg'] = [
                            {
                                'beskrivelse': step.description,
                                'uttrykk': step.expression,
                                'regel': step.rule_applied
                            }
                            for step in solution.steps
                        ]
                    except Exception:
                        pass
                
                fasit[nivaa_navn].append(fasit_entry)
        
        return fasit
    
    def _bestem_format(self, oppgavesett: Oppgavesett) -> str:
        """Bestem om Typst, LaTeX eller hybrid er best."""
        # Tell hvor mange oppgaver som trenger figurer
        total_oppgaver = (
            len(oppgavesett.nivaa_1) + 
            len(oppgavesett.nivaa_2) + 
            len(oppgavesett.nivaa_3)
        )
        
        figur_oppgaver = sum(
            1 for o in (oppgavesett.nivaa_1 + oppgavesett.nivaa_2 + oppgavesett.nivaa_3)
            if o.figur_trengs
        )
        
        if total_oppgaver == 0:
            return "typst"
        
        figur_andel = figur_oppgaver / total_oppgaver
        
        if figur_andel > 0.5:
            return "latex"  # Mange figurer, bruk LaTeX gjennomgående
        elif figur_andel > 0.1:
            return "hybrid"  # Noen figurer, hybrid-tilnærming
        else:
            return "typst"  # Få/ingen figurer, Typst er raskest
    
    def til_typst(self, oppgavesett: Oppgavesett) -> str:
        """Konverter oppgavesett til Typst-kode."""
        parts = []
        
        # Header
        parts.append(TypstTemplates.worksheet_header(
            title=oppgavesett.tittel,
            grade=oppgavesett.kurs,
            topic=oppgavesett.emne
        ))
        
        # Kompetansemål
        parts.append(f"""
#text(style: "italic")[
  *Kompetansemål:* {oppgavesett.kompetansemaal}
]

#v(1em)
""")
        
        # Nivå 1
        if oppgavesett.nivaa_1:
            parts.append(TypstTemplates.level_divider(
                1, 
                "Disse oppgavene hjelper deg å forstå det grunnleggende."
            ))
            parts.append(self._oppgaver_til_typst(oppgavesett.nivaa_1))
        
        # Nivå 2
        if oppgavesett.nivaa_2:
            parts.append(TypstTemplates.level_divider(
                2,
                "Standardoppgaver som tester din forståelse."
            ))
            parts.append(self._oppgaver_til_typst(oppgavesett.nivaa_2))
        
        # Nivå 3
        if oppgavesett.nivaa_3:
            parts.append(TypstTemplates.level_divider(
                3,
                "Utfordrende oppgaver som krever kombinasjon av flere teknikker."
            ))
            parts.append(self._oppgaver_til_typst(oppgavesett.nivaa_3))
        
        return ''.join(parts)
    
    def _oppgaver_til_typst(self, oppgaver: list[Oppgave]) -> str:
        """Konverter en liste med oppgaver til Typst."""
        lines = []
        
        for oppgave in oppgaver:
            # Oppgavetekst
            lines.append(f"*Oppgave {oppgave.nummer}*")
            lines.append("")
            lines.append(oppgave.tekst)
            lines.append("")
            
            # Matematisk uttrykk
            if oppgave.latex_problem:
                # Konverter LaTeX til Typst math
                typst_math = self._latex_til_typst_math(oppgave.latex_problem)
                lines.append(f"$ {typst_math} $")
                lines.append("")
            
            # Hint (kun nivå 1)
            if oppgave.hint:
                lines.append(f"#hint[{oppgave.hint}]")
                lines.append("")
            
            lines.append("#v(1em)")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _latex_til_typst_math(self, latex: str) -> str:
        """Konverter LaTeX math til Typst math."""
        # Enkel konvertering - kan utvides
        result = latex
        
        # Vanlige konverteringer
        replacements = [
            (r'\frac{', 'frac('),
            (r'}{', ', '),
            (r'\cdot', 'dot'),
            (r'\sqrt{', 'sqrt('),
            (r'\sin', 'sin'),
            (r'\cos', 'cos'),
            (r'\tan', 'tan'),
            (r'\ln', 'ln'),
            (r'\exp', 'exp'),
            (r'\pi', 'pi'),
            (r'\infty', 'oo'),
            (r'\\', ''),  # Fjern backslash-escapes
        ]
        
        for old, new in replacements:
            result = result.replace(old, new)
        
        # Fikse lukkeparenteser fra \frac
        # Dette er en forenklet versjon - mer robust parsing trengs for komplekse uttrykk
        
        return result
    
    def fasit_til_typst(self, oppgavesett: Oppgavesett) -> str:
        """Generer Typst-kode for fasit."""
        if not oppgavesett.fasit:
            return ""
        
        parts = []
        
        # Header
        parts.append(TypstTemplates.answer_key_header(
            title=oppgavesett.tittel,
            grade=oppgavesett.kurs,
            topic=oppgavesett.emne
        ))
        
        # Nivåer
        for nivaa, navn in [(1, 'nivaa_1'), (2, 'nivaa_2'), (3, 'nivaa_3')]:
            fasit_liste = oppgavesett.fasit.get(navn, [])
            if not fasit_liste:
                continue
            
            parts.append(f"\n== Nivå {nivaa}\n")
            
            for entry in fasit_liste:
                parts.append(f"*Oppgave {entry['nummer']}:*")
                parts.append("")
                
                # Svar
                svar_typst = self._latex_til_typst_math(entry['svar'])
                parts.append(f"$ {svar_typst} $")
                parts.append("")
                
                # Steg hvis tilgjengelig
                if 'steg' in entry:
                    for steg in entry['steg']:
                        parts.append(f"- {steg['beskrivelse']}")
                        if steg.get('regel'):
                            parts.append(f"  _({steg['regel']})_")
                    parts.append("")
                
                parts.append("#v(0.5em)")
        
        return '\n'.join(parts)


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    agent = VGSAgent()
    
    print("=== MaTultimate VGS Agent Test ===\n")
    
    # Test derivasjon
    config = OppgaveConfig(
        kurs=VGSKurs.R1,
        emne=Emne.DERIVASJON,
        antall_oppgaver=6,
        differensiering=True
    )
    
    print(f"Genererer oppgavesett for {config.kurs.value} - {config.emne.value}...")
    oppgavesett = agent.generer_oppgavesett(config)
    
    print(f"\nTittel: {oppgavesett.tittel}")
    print(f"Nivå 1: {len(oppgavesett.nivaa_1)} oppgaver")
    print(f"Nivå 2: {len(oppgavesett.nivaa_2)} oppgaver")
    print(f"Nivå 3: {len(oppgavesett.nivaa_3)} oppgaver")
    print(f"Format-anbefaling: {oppgavesett.format_anbefaling}")
    
    print("\n--- Eksempel på oppgaver ---")
    for nivaa_navn, oppgaver in [("Nivå 1", oppgavesett.nivaa_1), ("Nivå 2", oppgavesett.nivaa_2)]:
        print(f"\n{nivaa_navn}:")
        for o in oppgaver[:2]:
            print(f"  {o.nummer}: {o.latex_problem}")
            print(f"      Svar: {o.latex_svar}")
    
    print("\n--- Typst-output (første 50 linjer) ---")
    typst_code = agent.til_typst(oppgavesett)
    for line in typst_code.split('\n')[:50]:
        print(line)
    
    print("\n=== Ferdig ===")
