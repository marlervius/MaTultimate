"""
FigurAgent - Forventet Output Eksempler
=======================================
Denne filen viser EKSAKT hva FigurAgent skal produsere.
Bruk dette som referanse under implementasjon.
"""

# =============================================================================
# EKSEMPEL 1: Enkel funksjonsplot
# =============================================================================
# Input: funksjon="x**2", x_range=(-3, 3)

EXPECTED_FUNKSJONSPLOT = r"""
\begin{tikzpicture}
\begin{axis}[
    width=10cm,
    height=7cm,
    axis lines=middle,
    xlabel={$x$},
    ylabel={$y$},
    xmin=-3, xmax=3,
    ymin=-1, ymax=10,
    grid=major,
    samples=100,
]
\addplot[blue, thick, domain=-3:3] {x^2};
\end{axis}
\end{tikzpicture}
""".strip()


# =============================================================================
# EKSEMPEL 2: Funksjonsplot med tangent
# =============================================================================
# Input: funksjon="x**2 - 2*x", tangent_x=3, x_range=(-1, 5)
# 
# Beregninger:
#   f(x) = x² - 2x
#   f(3) = 9 - 6 = 3
#   f'(x) = 2x - 2  
#   f'(3) = 4
#   Tangent: y - 3 = 4(x - 3)  =>  y = 4x - 9

EXPECTED_TANGENT = r"""
\begin{tikzpicture}
\begin{axis}[
    width=10cm,
    height=7cm,
    axis lines=middle,
    xlabel={$x$},
    ylabel={$y$},
    xmin=-1, xmax=5,
    ymin=-2, ymax=10,
    grid=major,
    samples=100,
    legend pos=north west,
]
% Hovedfunksjon
\addplot[blue, thick, domain=-1:5] {x^2 - 2*x};
\addlegendentry{$f(x) = x^2 - 2x$}

% Tangentlinje
\addplot[red, thick, dashed, domain=1:5] {4*x - 9};
\addlegendentry{Tangent i $x=3$}

% Tangentpunkt
\node[circle, fill=red, inner sep=2pt] at (axis cs:3,3) {};
\end{axis}
\end{tikzpicture}
""".strip()


# =============================================================================
# EKSEMPEL 3: Areal under kurve
# =============================================================================
# Input: funksjon="x**2", nedre_grense=0, ovre_grense=2

EXPECTED_AREAL = r"""
\begin{tikzpicture}
\begin{axis}[
    width=10cm,
    height=7cm,
    axis lines=middle,
    xlabel={$x$},
    ylabel={$y$},
    xmin=-1, xmax=3,
    ymin=-0.5, ymax=5,
    grid=major,
    samples=100,
]
% Skravert område
\addplot[fill=blue!30, draw=none, domain=0:2] {x^2} \closedcycle;

% Funksjonskurve
\addplot[blue, thick, domain=-1:3] {x^2};

% Grenselinjer (valgfritt)
\draw[dashed, gray] (axis cs:0,0) -- (axis cs:0,0);
\draw[dashed, gray] (axis cs:2,0) -- (axis cs:2,4);
\end{axis}
\end{tikzpicture}
""".strip()


# =============================================================================
# EKSEMPEL 4: Normalfordeling
# =============================================================================
# Input: mu=0, sigma=1, skraver_fra=-1, skraver_til=1

EXPECTED_NORMALFORDELING = r"""
\begin{tikzpicture}
\begin{axis}[
    width=10cm,
    height=6cm,
    axis lines=left,
    xlabel={$x$},
    ylabel={$f(x)$},
    xmin=-4, xmax=4,
    ymin=0, ymax=0.5,
    samples=100,
    ytick={0, 0.1, 0.2, 0.3, 0.4},
]
% Skravert område (P(-1 < X < 1) ≈ 0.68)
\addplot[fill=blue!30, draw=none, domain=-1:1] 
    {1/(1*sqrt(2*pi))*exp(-((x-0)^2)/(2*1^2))} \closedcycle;

% Normalfordelingskurve
\addplot[blue, thick, domain=-4:4] 
    {1/(1*sqrt(2*pi))*exp(-((x-0)^2)/(2*1^2))};

% Markeringer
\node at (axis cs:0,0.45) {$\mu = 0$};
\end{axis}
\end{tikzpicture}
""".strip()


# =============================================================================
# EKSEMPEL 5: Enhetssirkel
# =============================================================================
# Input: vinkler=[30, 45, 60] (grader)

EXPECTED_ENHETSSIRKEL = r"""
\begin{tikzpicture}[scale=2.5]
% Koordinatsystem
\draw[->] (-1.3,0) -- (1.3,0) node[right] {$x$};
\draw[->] (0,-1.3) -- (0,1.3) node[above] {$y$};

% Enhetssirkel
\draw[thick] (0,0) circle (1);

% Vinkel 30°
\draw[blue, thick] (0,0) -- (30:1);
\filldraw[blue] (30:1) circle (1pt) node[above right] {$(\frac{\sqrt{3}}{2}, \frac{1}{2})$};
\draw[blue] (0.3,0) arc (0:30:0.3) node[midway, right] {$30°$};

% Vinkel 45°
\draw[red, thick] (0,0) -- (45:1);
\filldraw[red] (45:1) circle (1pt) node[above right] {$(\frac{\sqrt{2}}{2}, \frac{\sqrt{2}}{2})$};

% Vinkel 60°
\draw[green!60!black, thick] (0,0) -- (60:1);
\filldraw[green!60!black] (60:1) circle (1pt) node[above] {$(\frac{1}{2}, \frac{\sqrt{3}}{2})$};

% Aksemerking
\node[below] at (1,0) {$1$};
\node[left] at (0,1) {$1$};
\end{tikzpicture}
""".strip()


# =============================================================================
# SYMPY -> TIKZ KONVERTERINGER
# =============================================================================

SYMPY_TO_TIKZ_EXAMPLES = {
    # SymPy syntaks -> pgfplots syntaks
    "x**2": "x^2",
    "x**3 + 2*x**2 - x": "x^3 + 2*x^2 - x",
    "3*x**2 - 2*x + 1": "3*x^2 - 2*x + 1",
    "exp(x)": "exp(x)",           # pgfplots forstår exp
    "exp(-x**2)": "exp(-x^2)",
    "sin(x)": "sin(x)",           # pgfplots forstår sin
    "cos(2*x)": "cos(2*x)",
    "ln(x)": "ln(x)",             # pgfplots forstår ln
    "log(x, 10)": "log10(x)",     # 10-logaritme
    "sqrt(x)": "sqrt(x)",         # pgfplots forstår sqrt
    "sqrt(x**2 + 1)": "sqrt(x^2 + 1)",
    "1/(x**2 + 1)": "1/(x^2 + 1)",
    "x/(x**2 - 1)": "x/(x^2 - 1)",
}


# =============================================================================
# PRINT EKSEMPLER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FigurAgent - Forventet Output")
    print("=" * 60)
    
    examples = [
        ("Enkel funksjonsplot", EXPECTED_FUNKSJONSPLOT),
        ("Funksjonsplot med tangent", EXPECTED_TANGENT),
        ("Areal under kurve", EXPECTED_AREAL),
        ("Normalfordeling", EXPECTED_NORMALFORDELING),
        ("Enhetssirkel", EXPECTED_ENHETSSIRKEL),
    ]
    
    for name, tikz in examples:
        print(f"\n{'=' * 60}")
        print(f"EKSEMPEL: {name}")
        print("=" * 60)
        print(tikz)
    
    print(f"\n{'=' * 60}")
    print("SymPy -> TikZ konverteringer")
    print("=" * 60)
    for sympy_expr, tikz_expr in SYMPY_TO_TIKZ_EXAMPLES.items():
        print(f"  {sympy_expr:25} -> {tikz_expr}")
