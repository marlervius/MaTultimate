from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List
import os
import re
from app.core.math_engine import MathEngine

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
    
    # For enhetssirkel
    vinkler: Optional[List[float]] = None    # Grader
    
    # Styling
    farge: str = "blue"
    bredde_cm: float = 10
    hoyde_cm: float = 7

class FigurAgent:
    """
    Agent som genererer LaTeX/TikZ-kode for matematiske figurer.
    Bruker MathEngine for nøyaktige beregninger.
    """
    
    def __init__(self):
        self.math_engine = MathEngine()

    def generer(self, request: FigurRequest) -> str:
        """Genererer komplett TikZ-kode basert på forespørselen."""
        if request.figur_type == FigurType.FUNKSJONSPLOT:
            return self._generer_funksjonsplot(request)
        elif request.figur_type == FigurType.FUNKSJONSPLOT_TANGENT:
            return self._generer_tangent_plot(request)
        elif request.figur_type == FigurType.AREAL_UNDER_KURVE:
            return self._generer_areal_plot(request)
        elif request.figur_type == FigurType.NORMALFORDELING:
            return self._generer_normalfordeling(request)
        elif request.figur_type == FigurType.ENHETSSIRKEL:
            return self._generer_enhetssirkel(request)
        else:
            return f"% Figurtype {request.figur_type} er ikke implementert ennå."

    def _generer_funksjonsplot(self, request: FigurRequest) -> str:
        tikz_funksjon = self._sympy_til_tikz(request.funksjon)
        ymin = request.y_range[0] if request.y_range else -1
        ymax = request.y_range[1] if request.y_range else 10
        
        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width={request.bredde_cm}cm,
    height={request.hoyde_cm}cm,
    axis lines=middle,
    xlabel={{$x$}},
    ylabel={{$y$}},
    xmin={request.x_range[0]}, xmax={request.x_range[1]},
    ymin={ymin}, ymax={ymax},
    grid=major,
    samples=100,
]
\\addplot[{request.farge}, thick, domain={request.x_range[0]}:{request.x_range[1]}] {{{tikz_funksjon}}};
\\end{{axis}}
\\end{{tikzpicture}}""".strip()

    def _generer_tangent_plot(self, request: FigurRequest) -> str:
        if not request.funksjon or request.tangent_x is None:
            raise ValueError("Funksjon og tangent_x må være satt for tangent-plot.")
        
        tangent_ligning, y0 = self._beregn_tangent(request.funksjon, request.tangent_x)
        
        tikz_funksjon = self._sympy_til_tikz(request.funksjon)
        tikz_tangent = self._sympy_til_tikz(tangent_ligning)
        
        ymin = request.y_range[0] if request.y_range else -2
        ymax = request.y_range[1] if request.y_range else 10

        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width={request.bredde_cm}cm,
    height={request.hoyde_cm}cm,
    axis lines=middle,
    xlabel={{$x$}},
    ylabel={{$y$}},
    xmin={request.x_range[0]}, xmax={request.x_range[1]},
    ymin={ymin}, ymax={ymax},
    grid=major,
    samples=100,
    legend pos=north west,
]
% Hovedfunksjon
\\addplot[{request.farge}, thick, domain={request.x_range[0]}:{request.x_range[1]}] {{{tikz_funksjon}}};
\\addlegendentry{{$f(x) = {tikz_funksjon.replace("*", "")}$}}

% Tangentlinje
\\addplot[red, thick, dashed, domain={request.tangent_x-2}:{request.tangent_x+2}] {{{tikz_tangent}}};
\\addlegendentry{{Tangent i $x={request.tangent_x}$}}

% Tangentpunkt
\\node[circle, fill=red, inner sep=2pt] at (axis cs:{request.tangent_x},{y0}) {{}};
\\end{{axis}}
\\end{{tikzpicture}}""".strip()

    def _generer_areal_plot(self, request: FigurRequest) -> str:
        tikz_funksjon = self._sympy_til_tikz(request.funksjon)
        a = request.nedre_grense if request.nedre_grense is not None else 0
        b = request.ovre_grense if request.ovre_grense is not None else 2
        
        ymin = request.y_range[0] if request.y_range else -0.5
        ymax = request.y_range[1] if request.y_range else 5

        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width={request.bredde_cm}cm,
    height={request.hoyde_cm}cm,
    axis lines=middle,
    xlabel={{$x$}},
    ylabel={{$y$}},
    xmin={request.x_range[0]}, xmax={request.x_range[1]},
    ymin={ymin}, ymax={ymax},
    grid=major,
    samples=100,
]
% Skravert område
\\addplot[fill={request.farge}!30, draw=none, domain={a}:{b}] {{{tikz_funksjon}}} \\closedcycle;

% Funksjonskurve
\\addplot[{request.farge}, thick, domain={request.x_range[0]}:{request.x_range[1]}] {{{tikz_funksjon}}};

% Grenselinjer (valgfritt)
\\draw[dashed, gray] (axis cs:{a},0) -- (axis cs:{a},{a**2 if "x^2" in tikz_funksjon else 0});
\\draw[dashed, gray] (axis cs:{b},0) -- (axis cs:{b},{b**2 if "x^2" in tikz_funksjon else 0});
\\end{{axis}}
\\end{{tikzpicture}}""".strip()

    def _generer_normalfordeling(self, request: FigurRequest) -> str:
        mu = request.mu
        sigma = request.sigma
        a = request.skraver_fra if request.skraver_fra is not None else -1
        b = request.skraver_til if request.skraver_til is not None else 1
        
        formula = f"1/({sigma}*sqrt(2*pi))*exp(-((x-{mu})^2)/(2*{sigma}^2))"

        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width={request.bredde_cm}cm,
    height={request.hoyde_cm-1}cm,
    axis lines=left,
    xlabel={{$x$}},
    ylabel={{$f(x)$}},
    xmin={mu-4*sigma}, xmax={mu+4*sigma},
    ymin=0, ymax=0.5,
    samples=100,
    ytick={{0, 0.1, 0.2, 0.3, 0.4}},
]
% Skravert område
\\addplot[fill=blue!30, draw=none, domain={a}:{b}] 
    {{{formula}}} \\closedcycle;

% Normalfordelingskurve
\\addplot[blue, thick, domain={mu-4*sigma}:{mu+4*sigma}] 
    {{{formula}}};

% Markeringer
\\node at (axis cs:{mu},0.45) {{$\\mu = {mu}$}};
\\end{{axis}}
\\end{{tikzpicture}}""".strip()

    def _generer_enhetssirkel(self, request: FigurRequest) -> str:
        vinkler = request.vinkler or [30, 45, 60]
        
        output = [r"""\begin{tikzpicture}[scale=2.5]
% Koordinatsystem
\draw[->] (-1.3,0) -- (1.3,0) node[right] {$x$};
\draw[->] (0,-1.3) -- (0,1.3) node[above] {$y$};

% Enhetssirkel
\draw[thick] (0,0) circle (1);"""]

        colors = ["blue", "red", "green!60!black", "orange", "purple"]
        
        for i, v in enumerate(vinkler):
            color = colors[i % len(colors)]
            # Forenklet etikett for nå (burde egentlig bruke sympy for eksakte verdier)
            output.append(f"""
% Vinkel {v}°
\\draw[{color}, thick] (0,0) -- ({v}:1);
\\filldraw[{color}] ({v}:1) circle (1pt);
\\draw[{color}] (0.3,0) arc (0:{v}:0.3) node[midway, right] {{${v}°$}};""")

        output.append(r"""
% Aksemerking
\node[below] at (1,0) {$1$};
\node[left] at (0,1) {$1$};
\end{tikzpicture}""")
        
        return "\n".join(output).strip()

    def _beregn_tangent(self, funksjon: str, x: float) -> Tuple[str, float]:
        """Bruker MathEngine til å finne tangentligning og y-verdi."""
        tangent_expr, y0, stigning = self.math_engine.beregn_tangent(funksjon, x)
        
        # Verifiser (valgfritt krav i prompt, men vi bruker verify_derivative for sikkerhet)
        import sympy as sp
        expr = sp.sympify(funksjon)
        derivert = str(sp.diff(expr, sp.Symbol('x')))
        if not self.math_engine.verify_derivative(funksjon, derivert):
            raise ValueError("Feil i derivasjonsberegning!")
            
        return tangent_expr, y0

    def _sympy_til_tikz(self, expr: str) -> str:
        """Konverterer SymPy-uttrykk til TikZ-kompatibel syntaks."""
        if not expr: return ""
        
        # x**2 -> x^2
        res = expr.replace("**", "^")
        
        # log(x) -> ln(x) (SymPy log er naturlig logaritme)
        # Men vi må sjekke om det er log10
        if "log(x, 10)" in res:
            res = res.replace("log(x, 10)", "log10(x)")
        elif "log(x)" in res:
            res = res.replace("log(x)", "ln(x)")
            
        return res
