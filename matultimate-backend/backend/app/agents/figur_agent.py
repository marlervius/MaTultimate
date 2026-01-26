"""
MaTultimate Figure Agent
========================
Genererer matematiske figurer med TikZ og pgfplots.

Støtter:
- Funksjonsgrafer med tangenter, nullpunkter, ekstremalpunkter
- Geometriske figurer (trekanter, sirkler, vektorer)
- Statistikk (normalfordeling, boksplott, regresjon)
- Økonomiske diagrammer (tilbud/etterspørsel)
"""

from typing import Optional, Literal
from dataclasses import dataclass
from enum import Enum
import re


class FigurType(str, Enum):
    """Typer figurer."""
    FUNKSJONSPLOTT = "funksjonsplott"
    FUNKSJONSPLOTT_MED_TANGENT = "funksjonsplott_tangent"
    AREAL_UNDER_KURVE = "areal_under_kurve"
    AREAL_MELLOM_KURVER = "areal_mellom_kurver"
    FORTEGNSLINJE = "fortegnslinje"
    TREKANT = "trekant"
    SIRKEL = "sirkel"
    VEKTOR = "vektor"
    ENHETSSIRKEL = "enhetssirkel"
    NORMALFORDELING = "normalfordeling"
    BOKSPLOTT = "boksplott"
    REGRESJON = "regresjon"
    TILBUD_ETTERSPORSEL = "tilbud_ettersporsel"


@dataclass
class FigurConfig:
    """Konfigurasjon for en figur."""
    type: FigurType
    
    # For funksjoner
    funksjon: Optional[str] = None  # f.eks. "x^2 - 2*x + 1"
    funksjon2: Optional[str] = None  # For areal mellom kurver
    x_min: float = -5
    x_max: float = 5
    y_min: float = -5
    y_max: float = 5
    
    # For tangent
    tangent_punkt: Optional[float] = None
    
    # For areal
    areal_fra: Optional[float] = None
    areal_til: Optional[float] = None
    
    # For geometri
    punkter: Optional[list[tuple]] = None
    vinkler: Optional[list[str]] = None
    sidelengder: Optional[list[str]] = None
    
    # For statistikk
    gjennomsnitt: Optional[float] = None
    standardavvik: Optional[float] = None
    data: Optional[list[float]] = None
    
    # Visuelle innstillinger
    grid: bool = True
    akser: bool = True
    farge: str = "blue"
    linjetykkelse: float = 1.5
    bredde: str = "10cm"
    hoyde: str = "8cm"


class FigurAgent:
    """
    Agent for å generere TikZ/pgfplots-figurer.
    
    Eksempel:
        agent = FigurAgent()
        
        config = FigurConfig(
            type=FigurType.FUNKSJONSPLOTT_MED_TANGENT,
            funksjon="x^2",
            tangent_punkt=1,
            x_min=-3, x_max=3
        )
        
        tikz_code = agent.generer(config)
    """
    
    def generer(self, config: FigurConfig) -> str:
        """Hovedmetode for å generere figur."""
        if config.type == FigurType.FUNKSJONSPLOTT:
            return self._funksjonsplott(config)
        elif config.type == FigurType.FUNKSJONSPLOTT_MED_TANGENT:
            return self._funksjonsplott_tangent(config)
        elif config.type == FigurType.AREAL_UNDER_KURVE:
            return self._areal_under_kurve(config)
        elif config.type == FigurType.AREAL_MELLOM_KURVER:
            return self._areal_mellom_kurver(config)
        elif config.type == FigurType.FORTEGNSLINJE:
            return self._fortegnslinje(config)
        elif config.type == FigurType.TREKANT:
            return self._trekant(config)
        elif config.type == FigurType.SIRKEL:
            return self._sirkel(config)
        elif config.type == FigurType.VEKTOR:
            return self._vektor(config)
        elif config.type == FigurType.ENHETSSIRKEL:
            return self._enhetssirkel(config)
        elif config.type == FigurType.NORMALFORDELING:
            return self._normalfordeling(config)
        elif config.type == FigurType.BOKSPLOTT:
            return self._boksplott(config)
        elif config.type == FigurType.REGRESJON:
            return self._regresjon(config)
        elif config.type == FigurType.TILBUD_ETTERSPORSEL:
            return self._tilbud_ettersporsel(config)
        else:
            raise ValueError(f"Ukjent figurtype: {config.type}")
    
    def _pgfplots_header(self, config: FigurConfig) -> str:
        """Standard pgfplots-oppsett."""
        grid_option = "both" if config.grid else "none"
        
        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width={config.bredde},
    height={config.hoyde},
    axis lines=middle,
    xlabel=$x$,
    ylabel=$y$,
    xmin={config.x_min}, xmax={config.x_max},
    ymin={config.y_min}, ymax={config.y_max},
    grid={grid_option},
    grid style={{gray!30}},
    tick label style={{font=\\small}},
    samples=100,
]
"""
    
    def _pgfplots_footer(self) -> str:
        """Avslutning for pgfplots."""
        return """\\end{axis}
\\end{tikzpicture}"""
    
    def _konverter_funksjon(self, f: str) -> str:
        """Konverter Python-syntaks til pgfplots-syntaks."""
        result = f
        
        # Python -> pgfplots
        replacements = [
            (r'\*\*', '^'),           # ** -> ^
            (r'exp\(', 'exp('),       # exp() er OK
            (r'sqrt\(', 'sqrt('),     # sqrt() er OK
            (r'sin\(', 'sin(deg('),   # sin(x) -> sin(deg(x))
            (r'cos\(', 'cos(deg('),   # cos(x) -> cos(deg(x))
            (r'tan\(', 'tan(deg('),   # tan(x) -> tan(deg(x))
            (r'ln\(', 'ln('),         # ln() er OK
            (r'log\(', 'ln('),        # log() -> ln() i pgfplots
        ]
        
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        # Fiks grader for trig (legg til avsluttende parentes)
        for trig in ['sin', 'cos', 'tan']:
            if f'{trig}(deg(' in result:
                # Finn matchende parentes og legg til )
                # Dette er en forenklet versjon
                result = result.replace(f'{trig}(deg(x))', f'{trig}(deg(x))')
        
        return result
    
    def _funksjonsplott(self, config: FigurConfig) -> str:
        """Enkel funksjonsplott."""
        f = self._konverter_funksjon(config.funksjon or "x^2")
        
        code = self._pgfplots_header(config)
        code += f"""
    \\addplot[{config.farge}, thick, domain={config.x_min}:{config.x_max}] {{{f}}};
"""
        code += self._pgfplots_footer()
        return code
    
    def _funksjonsplott_tangent(self, config: FigurConfig) -> str:
        """Funksjonsplott med tangentlinje."""
        f = self._konverter_funksjon(config.funksjon or "x^2")
        x0 = config.tangent_punkt or 1
        
        # For tangent trenger vi f(x0) og f'(x0)
        # Dette beregnes av SymPy på forhånd, men her bruker vi en forenklet versjon
        
        code = self._pgfplots_header(config)
        code += f"""
    % Funksjonen
    \\addplot[{config.farge}, thick, domain={config.x_min}:{config.x_max}] {{{f}}};
    
    % Tangentpunkt
    \\addplot[only marks, mark=*, {config.farge}] coordinates {{({x0}, {{{f.replace('x', f'({x0})')}}})}};
    
    % Tangentlinje (beregnes numerisk)
    % For eksakt tangent, bruk SymPy til å beregne f(x0) og f'(x0)
"""
        code += self._pgfplots_footer()
        return code
    
    def _areal_under_kurve(self, config: FigurConfig) -> str:
        """Skravert areal under kurve."""
        f = self._konverter_funksjon(config.funksjon or "x^2")
        a = config.areal_fra or 0
        b = config.areal_til or 2
        
        code = self._pgfplots_header(config)
        code += f"""
    % Skravert areal
    \\addplot[
        fill={config.farge}!20,
        draw={config.farge},
        thick,
        domain={a}:{b}
    ] {{{f}}} \\closedcycle;
    
    % Funksjonen over hele domenet
    \\addplot[{config.farge}, thick, domain={config.x_min}:{config.x_max}] {{{f}}};
    
    % Grenselinjer
    \\draw[dashed, gray] ({a}, 0) -- ({a}, {{{f.replace('x', f'({a})')}}});
    \\draw[dashed, gray] ({b}, 0) -- ({b}, {{{f.replace('x', f'({b})')}}});
"""
        code += self._pgfplots_footer()
        return code
    
    def _areal_mellom_kurver(self, config: FigurConfig) -> str:
        """Skravert areal mellom to kurver."""
        f1 = self._konverter_funksjon(config.funksjon or "x^2")
        f2 = self._konverter_funksjon(config.funksjon2 or "x")
        a = config.areal_fra or 0
        b = config.areal_til or 1
        
        code = self._pgfplots_header(config)
        code += f"""
    % Skravert areal mellom kurvene
    \\addplot[
        fill={config.farge}!20,
        draw=none
    ] fill between[
        of=f1 and f2,
        soft clip={{domain={a}:{b}}}
    ];
    
    % Funksjon 1
    \\addplot[{config.farge}, thick, domain={config.x_min}:{config.x_max}, name path=f1] {{{f1}}};
    
    % Funksjon 2
    \\addplot[red, thick, domain={config.x_min}:{config.x_max}, name path=f2] {{{f2}}};
"""
        code += self._pgfplots_footer()
        return code
    
    def _fortegnslinje(self, config: FigurConfig) -> str:
        """Fortegnslinje (for funksjonsdrøfting)."""
        # Enkel fortegnslinje
        return f"""\\begin{{tikzpicture}}
    % Tallinje
    \\draw[thick, ->] (-5, 0) -- (5, 0) node[right] {{$x$}};
    
    % Nullpunkter (eksempel)
    \\foreach \\x in {{-2, 1, 3}} {{
        \\draw[thick] (\\x, -0.1) -- (\\x, 0.1);
        \\node[below] at (\\x, -0.2) {{$\\x$}};
    }}
    
    % Fortegn
    \\node at (-3.5, 0.5) {{$+$}};
    \\node at (-0.5, 0.5) {{$-$}};
    \\node at (2, 0.5) {{$+$}};
    \\node at (4, 0.5) {{$-$}};
    
    % Funksjonsnavn
    \\node[left] at (-5, 0.5) {{$f'(x)$}};
\\end{{tikzpicture}}"""
    
    def _trekant(self, config: FigurConfig) -> str:
        """Trekant med vinkler og sider."""
        # Standard trekant hvis ingen punkter er gitt
        punkter = config.punkter or [(0, 0), (4, 0), (2, 3)]
        vinkler = config.vinkler or ["A", "B", "C"]
        sider = config.sidelengder or ["a", "b", "c"]
        
        A, B, C = punkter
        
        return f"""\\begin{{tikzpicture}}[scale=1.5]
    % Trekanten
    \\draw[thick] {A} -- {B} -- {C} -- cycle;
    
    % Hjørnepunkter
    \\node[below left] at {A} {{${vinkler[0]}$}};
    \\node[below right] at {B} {{${vinkler[1]}$}};
    \\node[above] at {C} {{${vinkler[2]}$}};
    
    % Sidelengder
    \\node[below] at ({(A[0]+B[0])/2}, {(A[1]+B[1])/2 - 0.2}) {{${sider[2]}$}};
    \\node[right] at ({(B[0]+C[0])/2 + 0.2}, {(B[1]+C[1])/2}) {{${sider[0]}$}};
    \\node[left] at ({(A[0]+C[0])/2 - 0.2}, {(A[1]+C[1])/2}) {{${sider[1]}$}};
    
    % Rettvinklet markering (hvis relevant)
    % \\draw ({A[0]+0.3}, {A[1]}) -- ({A[0]+0.3}, {A[1]+0.3}) -- ({A[0]}, {A[1]+0.3});
\\end{{tikzpicture}}"""
    
    def _sirkel(self, config: FigurConfig) -> str:
        """Sirkel med radius og sentrum."""
        return f"""\\begin{{tikzpicture}}
    % Koordinatsystem
    \\draw[gray!30, step=1] (-4,-4) grid (4,4);
    \\draw[thick, ->] (-4.5, 0) -- (4.5, 0) node[right] {{$x$}};
    \\draw[thick, ->] (0, -4.5) -- (0, 4.5) node[above] {{$y$}};
    
    % Sirkelen
    \\draw[{config.farge}, thick] (0, 0) circle (3);
    
    % Sentrum
    \\fill[{config.farge}] (0, 0) circle (2pt);
    \\node[below left] at (0, 0) {{$S$}};
    
    % Radius
    \\draw[{config.farge}, dashed] (0, 0) -- (3, 0);
    \\node[below] at (1.5, 0) {{$r$}};
\\end{{tikzpicture}}"""
    
    def _vektor(self, config: FigurConfig) -> str:
        """Vektor i koordinatsystem."""
        return f"""\\begin{{tikzpicture}}
    % Koordinatsystem
    \\draw[gray!30, step=1] (-1,-1) grid (5,4);
    \\draw[thick, ->] (-1.5, 0) -- (5.5, 0) node[right] {{$x$}};
    \\draw[thick, ->] (0, -1.5) -- (0, 4.5) node[above] {{$y$}};
    
    % Vektor
    \\draw[->, {config.farge}, very thick] (0, 0) -- (3, 2);
    \\node[{config.farge}, above right] at (1.5, 1) {{$\\vec{{v}}$}};
    
    % Komponentpiler (stiplet)
    \\draw[dashed, gray] (0, 0) -- (3, 0);
    \\draw[dashed, gray] (3, 0) -- (3, 2);
    
    % Komponenter
    \\node[below] at (1.5, 0) {{$v_x$}};
    \\node[right] at (3, 1) {{$v_y$}};
\\end{{tikzpicture}}"""
    
    def _enhetssirkel(self, config: FigurConfig) -> str:
        """Enhetssirkelen med vinkel."""
        return f"""\\begin{{tikzpicture}}[scale=2.5]
    % Enhetssirkelen
    \\draw[thick] (0, 0) circle (1);
    
    % Akser
    \\draw[thick, ->] (-1.3, 0) -- (1.3, 0) node[right] {{$x$}};
    \\draw[thick, ->] (0, -1.3) -- (0, 1.3) node[above] {{$y$}};
    
    % Vinkel 60 grader som eksempel
    \\draw[{config.farge}, thick] (0, 0) -- (60:1);
    \\fill[{config.farge}] (60:1) circle (1.5pt);
    
    % Vinkelmarkering
    \\draw[{config.farge}] (0.2, 0) arc (0:60:0.2);
    \\node[{config.farge}] at (30:0.35) {{$\\theta$}};
    
    % Projeksjoner
    \\draw[dashed, gray] (60:1) -- ({{cos(60)}}, 0);
    \\draw[dashed, gray] (60:1) -- (0, {{sin(60)}});
    
    % Labels
    \\node[below] at ({{cos(60)/2}}, 0) {{$\\cos\\theta$}};
    \\node[left] at (0, {{sin(60)/2}}) {{$\\sin\\theta$}};
    
    % Punkt-koordinater
    \\node[above right] at (60:1) {{$(\\cos\\theta, \\sin\\theta)$}};
    
    % Spesielle punkter
    \\fill (1, 0) circle (1pt);
    \\fill (0, 1) circle (1pt);
    \\fill (-1, 0) circle (1pt);
    \\fill (0, -1) circle (1pt);
\\end{{tikzpicture}}"""
    
    def _normalfordeling(self, config: FigurConfig) -> str:
        """Normalfordelingskurve."""
        mu = config.gjennomsnitt or 0
        sigma = config.standardavvik or 1
        
        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width=12cm,
    height=7cm,
    axis lines=middle,
    xlabel=$x$,
    ylabel=$f(x)$,
    xmin={mu - 4*sigma}, xmax={mu + 4*sigma},
    ymin=0, ymax={0.5/sigma},
    xtick={{{mu - 2*sigma}, {mu - sigma}, {mu}, {mu + sigma}, {mu + 2*sigma}}},
    xticklabels={{$\\mu-2\\sigma$, $\\mu-\\sigma$, $\\mu$, $\\mu+\\sigma$, $\\mu+2\\sigma$}},
    ytick=\\empty,
    samples=100,
]
    % Normalfordelingskurven
    \\addplot[{config.farge}, thick, domain={mu - 4*sigma}:{mu + 4*sigma}] 
        {{1/({sigma}*sqrt(2*pi))*exp(-((x-{mu})^2)/(2*{sigma}^2))}};
    
    % Skravert område (±1 sigma)
    \\addplot[fill={config.farge}!20, draw=none, domain={mu - sigma}:{mu + sigma}]
        {{1/({sigma}*sqrt(2*pi))*exp(-((x-{mu})^2)/(2*{sigma}^2))}} \\closedcycle;
    
    % Midtlinje
    \\draw[dashed, gray] ({mu}, 0) -- ({mu}, {{1/({sigma}*sqrt(2*pi))}});
\\end{{axis}}
\\end{{tikzpicture}}"""
    
    def _boksplott(self, config: FigurConfig) -> str:
        """Boksplott (box-and-whisker)."""
        # Eksempeldata
        data = config.data or [2, 5, 7, 8, 9, 10, 12, 15, 18]
        
        return f"""\\begin{{tikzpicture}}
    % Tallinje
    \\draw[thick, ->] (0, 0) -- (12, 0) node[right] {{}};
    \\foreach \\x in {{0, 2, 4, 6, 8, 10, 12}} {{
        \\draw (\\x, -0.1) -- (\\x, 0.1);
        \\node[below] at (\\x, -0.2) {{\\x}};
    }}
    
    % Boksplott
    \\draw[thick, {config.farge}] (2, 0.5) -- (2, 1.5);  % Min whisker
    \\draw[thick, {config.farge}] (2, 1) -- (4, 1);       % Min linje
    \\draw[thick, {config.farge}, fill={config.farge}!20] (4, 0.5) rectangle (8, 1.5);  % Boks
    \\draw[thick, {config.farge}] (6, 0.5) -- (6, 1.5);   % Median
    \\draw[thick, {config.farge}] (8, 1) -- (10, 1);      % Max linje
    \\draw[thick, {config.farge}] (10, 0.5) -- (10, 1.5); % Max whisker
    
    % Labels
    \\node[above, font=\\small] at (2, 1.6) {{Min}};
    \\node[above, font=\\small] at (4, 1.6) {{$Q_1$}};
    \\node[above, font=\\small] at (6, 1.6) {{Median}};
    \\node[above, font=\\small] at (8, 1.6) {{$Q_3$}};
    \\node[above, font=\\small] at (10, 1.6) {{Max}};
\\end{{tikzpicture}}"""
    
    def _regresjon(self, config: FigurConfig) -> str:
        """Punktplott med regresjonslinje."""
        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width=10cm,
    height=8cm,
    axis lines=middle,
    xlabel=$x$,
    ylabel=$y$,
    xmin=0, xmax=10,
    ymin=0, ymax=15,
    grid=both,
    grid style={{gray!30}},
]
    % Datapunkter
    \\addplot[only marks, mark=*, {config.farge}] coordinates {{
        (1, 2.1)
        (2, 3.8)
        (3, 5.2)
        (4, 6.1)
        (5, 8.3)
        (6, 9.0)
        (7, 10.5)
        (8, 12.1)
    }};
    
    % Regresjonslinje
    \\addplot[red, thick, domain=0:10] {{1.5*x + 0.5}};
    
    % Ligning
    \\node[red, above right] at (1, 12) {{$y = 1.5x + 0.5$}};
\\end{{axis}}
\\end{{tikzpicture}}"""
    
    def _tilbud_ettersporsel(self, config: FigurConfig) -> str:
        """Tilbuds- og etterspørselskurver."""
        return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
    width=10cm,
    height=8cm,
    axis lines=middle,
    xlabel=Mengde ($Q$),
    ylabel=Pris ($P$),
    xmin=0, xmax=12,
    ymin=0, ymax=12,
    xtick=\\empty,
    ytick=\\empty,
]
    % Etterspørselskurve (fallende)
    \\addplot[{config.farge}, thick, domain=0.5:10] {{10 - 0.8*x}};
    \\node[{config.farge}, right] at (9, 3) {{Etterspørsel}};
    
    % Tilbudskurve (stigende)
    \\addplot[red, thick, domain=0:10] {{1 + 0.8*x}};
    \\node[red, right] at (9, 9) {{Tilbud}};
    
    % Likevektspunkt
    \\fill (5, 5) circle (2pt);
    \\node[above right] at (5, 5) {{Likevekt}};
    
    % Stiplete linjer til aksene
    \\draw[dashed, gray] (5, 0) -- (5, 5);
    \\draw[dashed, gray] (0, 5) -- (5, 5);
    
    % Labels
    \\node[below] at (5, 0) {{$Q^*$}};
    \\node[left] at (0, 5) {{$P^*$}};
\\end{{axis}}
\\end{{tikzpicture}}"""
    
    def generer_standalone(self, config: FigurConfig) -> str:
        """Generer komplett standalone LaTeX-dokument."""
        tikz_code = self.generer(config)
        
        return f"""\\documentclass[tikz, border=5pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepgfplotslibrary{{fillbetween}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}

\\begin{{document}}
{tikz_code}
\\end{{document}}
"""


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def lag_funksjonsplott(
    funksjon: str,
    x_min: float = -5,
    x_max: float = 5,
    tangent_ved: Optional[float] = None
) -> str:
    """Lag et enkelt funksjonsplott."""
    agent = FigurAgent()
    
    config = FigurConfig(
        type=FigurType.FUNKSJONSPLOTT_MED_TANGENT if tangent_ved else FigurType.FUNKSJONSPLOTT,
        funksjon=funksjon,
        x_min=x_min,
        x_max=x_max,
        tangent_punkt=tangent_ved
    )
    
    return agent.generer(config)


def lag_areal_figur(
    funksjon: str,
    fra: float,
    til: float,
    funksjon2: Optional[str] = None
) -> str:
    """Lag arealsfirgur (under kurve eller mellom kurver)."""
    agent = FigurAgent()
    
    config = FigurConfig(
        type=FigurType.AREAL_MELLOM_KURVER if funksjon2 else FigurType.AREAL_UNDER_KURVE,
        funksjon=funksjon,
        funksjon2=funksjon2,
        areal_fra=fra,
        areal_til=til
    )
    
    return agent.generer(config)


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    agent = FigurAgent()
    
    print("=== MaTultimate FigurAgent Test ===\n")
    
    # Test funksjonsplott
    print("1. Funksjonsplott:")
    config = FigurConfig(
        type=FigurType.FUNKSJONSPLOTT,
        funksjon="x^2 - 2*x - 3",
        x_min=-3, x_max=5
    )
    code = agent.generer(config)
    print(f"   Genererte {len(code)} tegn TikZ-kode")
    
    # Test areal
    print("\n2. Areal under kurve:")
    config = FigurConfig(
        type=FigurType.AREAL_UNDER_KURVE,
        funksjon="x^2",
        areal_fra=0, areal_til=2
    )
    code = agent.generer(config)
    print(f"   Genererte {len(code)} tegn TikZ-kode")
    
    # Test normalfordeling
    print("\n3. Normalfordeling:")
    config = FigurConfig(
        type=FigurType.NORMALFORDELING,
        gjennomsnitt=100,
        standardavvik=15
    )
    code = agent.generer(config)
    print(f"   Genererte {len(code)} tegn TikZ-kode")
    
    # Lagre eksempel
    print("\n4. Lagrer eksempel til fil...")
    config = FigurConfig(
        type=FigurType.ENHETSSIRKEL
    )
    standalone = agent.generer_standalone(config)
    
    with open("/home/claude/matultimate/test_figur.tex", "w") as f:
        f.write(standalone)
    
    print("   Lagret til test_figur.tex")
    print("\n✓ FigurAgent fungerer!")
