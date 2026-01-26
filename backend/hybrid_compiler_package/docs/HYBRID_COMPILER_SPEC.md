# Hybrid Compiler Spesifikasjon

## Kontekst

`compiler.py` har allerede grunnstrukturen. Nå må vi sikre at:
1. `compile_latex_figure_to_png()` faktisk fungerer
2. `compile_hybrid()` orkestrerer hele flyten korrekt
3. Feilhåndtering er robust

## Krav til compile_latex_figure_to_png()

### Input
```python
tikz_code: str  # REN TikZ (uten \documentclass)
dpi: int = 300
timeout: int = 30
```

### Prosess
```
1. Wrap TikZ i standalone dokument:
   \documentclass[tikz,border=5pt]{standalone}
   \usepackage{pgfplots}
   \pgfplotsset{compat=1.18}
   \begin{document}
   {tikz_code}
   \end{document}

2. Skriv til temp/figure.tex

3. Kjør: pdflatex -interaction=nonstopmode figure.tex

4. Konverter: pdftoppm -png -r {dpi} -singlefile figure.pdf figure
   (Eller fallback: convert -density {dpi} figure.pdf figure.png)

5. Les figure.png og returner bytes
```

### Output
```python
FigureResult(
    success: bool,
    png_bytes: Optional[bytes],
    png_base64: Optional[str],
    log: str
)
```

## Krav til compile_hybrid()

### Input
```python
typst_code: str  # Typst med #image("figurer/fig_X.png") referanser
figures: list[dict]  # [{"id": "fig_0", "latex": "TikZ-kode"}, ...]
```

### Prosess
```
1. Opprett session_dir/figurer/

2. For hver figur i figures:
   a. Kall compile_latex_figure_to_png(figur["latex"])
   b. Lagre til session_dir/figurer/{figur["id"]}.png
   c. Hvis feil: legg til warning, fortsett

3. Oppdater Typst-kode:
   - Erstatt #image("figurer/ med #image("{session_dir}/figurer/

4. Kompiler Typst til PDF

5. Returner PDF + warnings
```

### Kritisk: Bildereferanser

Typst bruker relative stier. Vi må enten:

**Alternativ A**: Kopier PNG til samme mappe som .typ filen
```python
# I session_dir:
# - document.typ
# - figurer/
#   - fig_0.png
#   - fig_1.png
```

**Alternativ B**: Bruk absolutte stier i Typst
```python
typst_code = typst_code.replace(
    '#image("figurer/',
    f'#image("{session_dir}/figurer/'
)
```

Alternativ A er renere og mer portabelt.

## Forbedringer i _wrap_tikz_standalone()

```python
def _wrap_tikz_standalone(self, tikz_code: str) -> str:
    """Wrap TikZ i standalone dokument med alle nødvendige pakker."""
    return r"""\documentclass[tikz,border=5pt]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{tikz}
\usetikzlibrary{calc,positioning,arrows.meta}

\begin{document}
""" + tikz_code + r"""
\end{document}
"""
```

## Robust feilhåndtering

```python
async def compile_latex_figure_to_png(self, tikz_code, dpi=300, timeout=30):
    try:
        # ... kompilering ...
    except asyncio.TimeoutError:
        return FigureResult(success=False, log="Timeout")
    except FileNotFoundError as e:
        return FigureResult(success=False, log=f"Mangler verktøy: {e}")
    except Exception as e:
        return FigureResult(success=False, log=f"Ukjent feil: {e}")
```

## Test at pdflatex og pdftoppm finnes

```python
def check_dependencies(self) -> dict:
    """Sjekk at verktøyene finnes."""
    results = {}
    
    for tool, cmd in [
        ('typst', ['typst', '--version']),
        ('pdflatex', ['pdflatex', '--version']),
        ('pdftoppm', ['pdftoppm', '-v']),  # Skriver til stderr
    ]:
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=5)
            results[tool] = {
                'installed': True,
                'version': (proc.stdout or proc.stderr).decode().split('\n')[0]
            }
        except Exception as e:
            results[tool] = {'installed': False, 'error': str(e)}
    
    return results
```

## Eksempel på forventet flyt

```python
# Bruker ber om differensierte derivasjonsoppgaver med grafer

# 1. VGSAgent genererer oppgaver
oppgavesett = vgs_agent.generer_oppgavesett(config)

# 2. Identifiser oppgaver som trenger figurer
figur_oppgaver = [o for o in alle_oppgaver if o.figur_trengs]

# 3. FigurAgent genererer TikZ
figures = []
for i, o in enumerate(figur_oppgaver):
    request = FigurRequest(
        figur_type=FigurType.FUNKSJONSPLOT_TANGENT,
        funksjon=o.funksjon,
        tangent_x=o.tangent_punkt,
    )
    tikz = figur_agent.generer(request)
    figures.append({"id": f"fig_{i}", "latex": tikz})

# 4. Generer Typst med figur-referanser
typst_code = vgs_agent.til_typst_med_figurer(oppgavesett, figures)

# 5. Kompiler hybrid
result = await compiler.compile_hybrid(typst_code, figures)

# 6. Returner PDF
return result.pdf_bytes
```

## Filstruktur under kompilering

```
/tmp/matultimate/compile_abc123/
├── document.typ          # Hovedfil
├── figurer/
│   ├── fig_0.png        # Kompilert fra TikZ
│   ├── fig_1.png
│   └── fig_2.png
├── figure_temp/          # Midlertidig for LaTeX
│   ├── figure.tex
│   ├── figure.pdf
│   └── figure.png
└── document.pdf          # Endelig output
```
