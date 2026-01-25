from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from app.core.math_engine import MathEngine
from crewai import Agent, LLM
import os

class FigurType(str, Enum):
    FUNKSJONSPLOT = "funksjonsplot"           # f(x) med valgfri tangent
    FUNKSJONSPLOT_TANGENT = "tangent"         # f(x) med tangent i punkt
    AREAL_UNDER_KURVE = "areal_under"         # Skravert areal
    AREAL_MELLOM_KURVER = "areal_mellom"      # To funksjoner, skravert mellom
    NORMALFORDELING = "normalfordeling"        # Gaussisk kurve med skravering
    ENHETSSIRKEL = "enhetssirkel"             # Med vinkler og verdier
    TREKANT = "trekant"                       # Med vinkler/sider merket
    VEKTOR_2D = "vektor_2d"                   # Vektorer i plan

@dataclass
class FigurRequest:
    figur_type: FigurType
    
    # For funksjonsplot
    funksjon: Optional[str] = None           # "x**2 - 2*x"
    x_range: Tuple[float, float] = (-5, 5)
    y_range: Optional[Tuple[float, float]] = None
    
    # For tangent
    tangent_x: Optional[float] = None        # x-verdi for tangentpunkt
    
    # For areal
    nedre_grense: Optional[float] = None
    ovre_grense: Optional[float] = None
    funksjon_2: Optional[str] = None         # For areal mellom kurver
    
    # For normalfordeling
    mu: float = 0
    sigma: float = 1
    skraver_fra: Optional[float] = None
    skraver_til: Optional[float] = None
    
    # Styling
    farge: str = "blue"
    bredde_cm: float = 10
    hoyde_cm: float = 7

class FigurAgent:
    """
    Agent som genererer LaTeX/TikZ-kode for matematiske figurer.
    Bruker MathEngine for nøyaktige beregninger.
    """
    
    TEMPLATES = {
        FigurType.FUNKSJONSPLOT_TANGENT: r"""
\begin{tikzpicture}
\begin{axis}[
    width={bredde}cm, height={hoyde}cm,
    axis lines=middle,
    xlabel=$x$, ylabel=$y$,
    xmin={xmin}, xmax={xmax},
    ymin={ymin}, ymax={ymax},
    grid=major,
    samples=100,
]
% Hovedfunksjon
\addplot[{farge}, thick, domain={xmin}:{xmax}] {{{funksjon}}};

% Tangent
\addplot[red, thick, domain={t_xmin}:{t_xmax}] {{{tangent_ligning}}};
\node[circle, fill=red, inner sep=2pt] at (axis cs:{tangent_x},{tangent_y}) {{}};
\end{axis}
\end{tikzpicture}
""",
        FigurType.AREAL_UNDER_KURVE: r"""
\begin{tikzpicture}
\begin{axis}[
    width={bredde}cm, height={hoyde}cm,
    axis lines=middle,
    xlabel=$x$, ylabel=$y$,
    xmin={xmin}, xmax={xmax},
]
\addplot[{farge}, thick, domain={xmin}:{xmax}] {{{funksjon}}};
\addplot[fill={farge}, fill opacity=0.3, domain={a}:{b}, samples=100] {{{funksjon}}} \closedcycle;
\end{axis}
\end{tikzpicture}
""",
        FigurType.NORMALFORDELING: r"""
\begin{tikzpicture}
\begin{axis}[
    width={bredde}cm, height={hoyde}cm,
    axis lines=left,
    xlabel=$x$,
    ylabel=$f(x)$,
    ymin=0,
    domain={xmin}:{xmax},
]
% Kurve
\addplot[blue, thick, samples=100] {{1/({sigma}*sqrt(2*pi))*exp(-((x-{mu})^2)/(2*{sigma}^2))}};

% Skravert område
\addplot[fill=blue!30, domain={skraver_fra}:{skraver_til}, samples=100] 
    {{1/({sigma}*sqrt(2*pi))*exp(-((x-{mu})^2)/(2*{sigma}^2))}} \closedcycle;
\end{axis}
\end{tikzpicture}
"""
    }

    def __init__(self, llm: Optional[LLM] = None):
        self.math_engine = MathEngine()
        self.llm = llm

    def generer(self, request: FigurRequest) -> str:
        """Genererer komplett TikZ-kode basert på forespørselen."""
        if request.figur_type == FigurType.FUNKSJONSPLOT_TANGENT:
            return self._generer_tangent_plot(request)
        elif request.figur_type == FigurType.AREAL_UNDER_KURVE:
            return self._generer_areal_plot(request)
        elif request.figur_type == FigurType.NORMALFORDELING:
            return self._generer_normalfordeling(request)
        else:
            # Fallback til LLM hvis typen ikke har en hardkodet template ennå
            return self._generer_med_llm(request)

    def _generer_tangent_plot(self, request: FigurRequest) -> str:
        if not request.funksjon or request.tangent_x is None:
            raise ValueError("Funksjon og tangent_x må være satt for tangent-plot.")
        
        tangent_ligning, y0, stigning = self.math_engine.beregn_tangent(request.funksjon, request.tangent_x)
        
        # TikZ-vennlig syntaks
        tikz_funksjon = self.math_engine.sympy_til_tikz(request.funksjon)
        tikz_tangent = self.math_engine.sympy_til_tikz(tangent_ligning)
        
        # Bestem y-range hvis ikke satt
        ymin = request.y_range[0] if request.y_range else -5
        ymax = request.y_range[1] if request.y_range else 10

        return self.TEMPLATES[FigurType.FUNKSJONSPLOT_TANGENT].format(
            bredde=request.bredde_cm,
            hoyde=request.hoyde_cm,
            xmin=request.x_range[0],
            xmax=request.x_range[1],
            ymin=ymin,
            ymax=ymax,
            farge=request.farge,
            funksjon=tikz_funksjon,
            tangent_ligning=tikz_tangent,
            tangent_x=request.tangent_x,
            tangent_y=y0,
            t_xmin=max(request.x_range[0], request.tangent_x - 2),
            t_xmax=min(request.x_range[1], request.tangent_x + 2)
        )

    def _generer_areal_plot(self, request: FigurRequest) -> str:
        tikz_funksjon = self.math_engine.sympy_til_tikz(request.funksjon)
        return self.TEMPLATES[FigurType.AREAL_UNDER_KURVE].format(
            bredde=request.bredde_cm,
            hoyde=request.hoyde_cm,
            xmin=request.x_range[0],
            xmax=request.x_range[1],
            farge=request.farge,
            funksjon=tikz_funksjon,
            a=request.nedre_grense if request.nedre_grense is not None else 0,
            b=request.ovre_grense if request.ovre_grense is not None else 2
        )

    def _generer_normalfordeling(self, request: FigurRequest) -> str:
        return self.TEMPLATES[FigurType.NORMALFORDELING].format(
            bredde=request.bredde_cm,
            hoyde=request.hoyde_cm,
            mu=request.mu,
            sigma=request.sigma,
            xmin=request.mu - 4*request.sigma,
            xmax=request.mu + 4*request.sigma,
            skraver_fra=request.skraver_fra if request.skraver_fra is not None else request.mu - request.sigma,
            skraver_til=request.skraver_til if request.skraver_til is not None else request.mu + request.sigma
        )

    def _generer_med_llm(self, request: FigurRequest) -> str:
        """Bruker CrewAI-agent for mer komplekse figurer som ikke har templates."""
        if not self.llm:
            return "% LLM ikke tilgjengelig for figur-generering"
            
        agent = Agent(
            role="TikZ-ekspert",
            goal="Generer TikZ-kode for en matematisk figur.",
            backstory="Du er en ekspert på LaTeX og TikZ, spesielt for VGS-matematikk.",
            llm=self.llm,
            allow_delegation=False
        )
        # Implementasjon av task her ved behov
        return "% LLM fallback ikke fullt implementert ennå"

    def get_agent(self) -> Agent:
        """Returnerer CrewAI-agenten for integrasjon i workflows."""
        return Agent(
            role="Teknisk Illustratør",
            goal="Generer nøyaktig TikZ/LaTeX-kode for matematiske figurer.",
            backstory="Du bruker templates og MathEngine for å sikre 100% korrekt matematikk i figurer.",
            llm=self.llm,
            allow_delegation=False
        )
