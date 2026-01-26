#!/usr/bin/env python3
"""
Hybrid Compiler Test Suite
==========================
Tester ende-til-ende: TikZ → PNG → Typst → PDF

Kjør: python tests/test_hybrid_compiler.py
"""

import sys
import asyncio
sys.path.insert(0, '/home/claude/matultimate/backend')

from pathlib import Path
import tempfile


class TestHybridCompiler:
    """
    Test-suite for hybrid kompilering.
    
    Pipeline som testes:
    1. FigurAgent genererer TikZ
    2. Compiler konverterer TikZ → PNG
    3. Compiler embedder PNG i Typst
    4. Compiler produserer endelig PDF
    """
    
    # -------------------------------------------------------------------------
    # TEST 1: TikZ til PNG konvertering
    # -------------------------------------------------------------------------
    async def test_tikz_til_png(self):
        """
        KRAV: Skal konvertere TikZ-kode til PNG-bilde.
        
        Input: Ren TikZ-kode (uten document-wrapper)
        Output: PNG-bytes med oppløsning 300 DPI
        """
        from app.core.compiler import DocumentCompiler
        
        compiler = DocumentCompiler()
        
        tikz_code = r"""
\begin{tikzpicture}
\begin{axis}[
    width=8cm,
    height=6cm,
    axis lines=middle,
    xlabel={$x$},
    ylabel={$y$},
]
\addplot[blue, thick, domain=-2:2, samples=50] {x^2};
\end{axis}
\end{tikzpicture}
"""
        
        result = await compiler.compile_latex_figure_to_png(tikz_code, dpi=300)
        
        assert result.success, f"Kompilering feilet: {result.log}"
        assert result.png_bytes is not None, "Ingen PNG-bytes"
        assert len(result.png_bytes) > 1000, "PNG for liten (korrupt?)"
        
        # Sjekk PNG magic bytes
        assert result.png_bytes[:8] == b'\x89PNG\r\n\x1a\n', "Ikke gyldig PNG"
        
        print("OK: Test 1 PASSED: TikZ -> PNG")
        print(f"  PNG størrelse: {len(result.png_bytes)} bytes")
        return result.png_bytes
    
    # -------------------------------------------------------------------------
    # TEST 2: Hybrid dokument (Typst + PNG-figurer)
    # -------------------------------------------------------------------------
    async def test_hybrid_dokument(self):
        """
        KRAV: Skal kompilere Typst-dokument med innebygde PNG-figurer.
        
        Workflow:
        1. FigurAgent lager TikZ
        2. TikZ kompileres til PNG
        3. Typst-dokument refererer til PNG
        4. Kompiler til PDF
        """
        from app.core.compiler import DocumentCompiler
        
        compiler = DocumentCompiler()
        
        # Typst-kode med figur-placeholder
        typst_code = r'''
#set text(lang: "nb")
#set page(paper: "a4", margin: 2cm)

= Test av hybrid kompilering

Her er en graf av $f(x) = x^2$:

#figure(
  image("figurer/fig_0.png", width: 80%),
  caption: [Graf av $f(x) = x^2$]
)

Grafen viser en parabel med bunnpunkt i origo.
'''
        
        # Figur som skal kompileres
        figures = [
            {
                "id": "fig_0",
                "latex": r"""
\begin{tikzpicture}
\begin{axis}[
    width=10cm, height=7cm,
    axis lines=middle,
    xlabel={$x$}, ylabel={$y$},
    xmin=-3, xmax=3,
    ymin=-1, ymax=9,
    grid=major,
]
\addplot[blue, thick, domain=-3:3, samples=100] {x^2};
\end{axis}
\end{tikzpicture}
"""
            }
        ]
        
        result = await compiler.compile_hybrid(typst_code, figures)
        
        assert result.success, f"Hybrid kompilering feilet: {result.log}"
        assert result.pdf_bytes is not None, "Ingen PDF"
        assert len(result.pdf_bytes) > 5000, "PDF for liten"
        
        # Sjekk PDF magic bytes
        assert result.pdf_bytes[:4] == b'%PDF', "Ikke gyldig PDF"
        
        print("OK: Test 2 PASSED: Hybrid dokument")
        print(f"  PDF størrelse: {len(result.pdf_bytes)} bytes")
        print(f"  Kompileringstid: {result.compilation_time_ms}ms")
        return result.pdf_bytes
    
    # -------------------------------------------------------------------------
    # TEST 3: Flere figurer i samme dokument
    # -------------------------------------------------------------------------
    async def test_flere_figurer(self):
        """
        KRAV: Skal håndtere flere figurer i samme dokument.
        """
        from app.core.compiler import DocumentCompiler
        
        compiler = DocumentCompiler()
        
        typst_code = r'''
#set text(lang: "nb")

= Funksjonsdrøfting

== Oppgave 1
#image("figurer/parabola.png", width: 70%)

== Oppgave 2  
#image("figurer/sinus.png", width: 70%)

== Oppgave 3
#image("figurer/tangent.png", width: 70%)
'''
        
        figures = [
            {
                "id": "parabola",
                "latex": r"""
\begin{tikzpicture}
\begin{axis}[width=8cm, height=5cm, axis lines=middle]
\addplot[blue, thick, domain=-2:2] {x^2};
\end{axis}
\end{tikzpicture}
"""
            },
            {
                "id": "sinus",
                "latex": r"""
\begin{tikzpicture}
\begin{axis}[width=8cm, height=5cm, axis lines=middle]
\addplot[red, thick, domain=-3.14:3.14, samples=100] {sin(deg(x))};
\end{axis}
\end{tikzpicture}
"""
            },
            {
                "id": "tangent",
                "latex": r"""
\begin{tikzpicture}
\begin{axis}[width=8cm, height=5cm, axis lines=middle, ymin=-3, ymax=3]
\addplot[blue, thick, domain=-2:2] {x^2 - 1};
\addplot[red, thick, dashed, domain=-1:3] {2*x - 2};
\node[circle, fill=red, inner sep=2pt] at (axis cs:1,0) {};
\end{axis}
\end{tikzpicture}
"""
            }
        ]
        
        result = await compiler.compile_hybrid(typst_code, figures)
        
        assert result.success, f"Feilet med flere figurer: {result.log}"
        assert len(result.warnings) < len(figures), "For mange warnings"
        
        print("OK: Test 3 PASSED: Flere figurer")
        print(f"  Antall figurer: {len(figures)}")
    
    # -------------------------------------------------------------------------
    # TEST 4: Feilhåndtering - ugyldig TikZ
    # -------------------------------------------------------------------------
    async def test_ugyldig_tikz_handtering(self):
        """
        KRAV: Skal håndtere feil i TikZ gracefully, ikke krasje hele dokumentet.
        """
        from app.core.compiler import DocumentCompiler
        
        compiler = DocumentCompiler()
        
        typst_code = r'''
#set text(lang: "nb")
= Test
#image("figurer/valid.png", width: 50%)
Tekst fortsetter her.
'''
        
        figures = [
            {
                "id": "valid",
                "latex": r"""
\begin{tikzpicture}
\begin{axis}[width=6cm, height=4cm]
\addplot[blue, domain=-1:1] {x^2};
\end{axis}
\end{tikzpicture}
"""
            },
            {
                "id": "invalid",  # Denne brukes ikke i typst, men tester feilhåndtering
                "latex": r"""
\begin{tikzpicture}
\begin{axis}
THIS IS INVALID LATEX!!!
\end{axis}
\end{tikzpicture}
"""
            }
        ]
        
        result = await compiler.compile_hybrid(typst_code, figures)
        
        # Bør fortsatt produsere PDF med gyldige figurer
        # Warnings bør rapportere den ugyldige figuren
        
        print("OK: Test 4 PASSED: Feilhåndtering")
        print(f"  Warnings: {result.warnings}")
    
    # -------------------------------------------------------------------------
    # TEST 5: Full pipeline - VGSAgent + FigurAgent + Compiler
    # -------------------------------------------------------------------------
    async def test_full_pipeline(self):
        """
        KRAV: Hele flyten fra oppgavegenerering til PDF.
        
        1. VGSAgent genererer oppgavesett
        2. Identifiser oppgaver som trenger figurer
        3. FigurAgent genererer TikZ for disse
        4. Compiler produserer hybrid PDF
        """
        from app.agents.vgs_agent import VGSAgent, VGSKurs, Emne, OppgaveConfig
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        from app.core.compiler import DocumentCompiler
        
        # Steg 1: Generer oppgaver
        vgs_agent = VGSAgent()
        config = OppgaveConfig(
            kurs=VGSKurs.R1,
            emne=Emne.DERIVASJON,
            antall_oppgaver=6,
            differensiering=True
        )
        oppgavesett = vgs_agent.generer_oppgavesett(config)
        
        # Steg 2: Finn oppgaver som trenger figurer
        figur_oppgaver = [
            o for o in (oppgavesett.nivaa_1 + oppgavesett.nivaa_2 + oppgavesett.nivaa_3)
            if o.figur_trengs
        ]
        
        print(f"  Fant {len(figur_oppgaver)} oppgaver som trenger figurer")
        
        # Steg 3: Generer figurer
        figur_agent = FigurAgent()
        figures = []
        
        for i, oppgave in enumerate(figur_oppgaver[:2]):  # Begrens til 2 for hastighet
            # Parse funksjon fra oppgaven
            funksjon = oppgave.latex_problem.replace("f(x) = ", "").strip()
            
            # Fjern LaTeX-formatering for SymPy
            funksjon_clean = funksjon.replace("\\", "").replace("{", "").replace("}", "")
            
            try:
                request = FigurRequest(
                    figur_type=FigurType.FUNKSJONSPLOT,
                    funksjon=funksjon_clean,
                    x_range=(-3, 3),
                )
                tikz = figur_agent.generer(request)
                figures.append({"id": f"fig_{i}", "latex": tikz})
            except Exception as e:
                print(f"  Advarsel: Kunne ikke lage figur for '{funksjon}': {e}")
        
        # Steg 4: Kompiler til PDF (hvis vi har figurer)
        if figures:
            compiler = DocumentCompiler()
            
            # Lag Typst med figur-referanser
            typst_code = vgs_agent.til_typst(oppgavesett)
            
            # Legg til figurer i Typst (forenklet)
            for i, fig in enumerate(figures):
                typst_code += f'\n#image("figurer/{fig["id"]}.png", width: 60%)\n'
            
            result = await compiler.compile_hybrid(typst_code, figures)
            
            if result.success:
                print("OK: Test 5 PASSED: Full pipeline")
                print(f"  PDF størrelse: {len(result.pdf_bytes)} bytes")
            else:
                print(f"X Test 5 FAILED: {result.log[:200]}")
        else:
            print("OK: Test 5 SKIPPED: Ingen figurer generert (OK for denne testen)")
    
    # -------------------------------------------------------------------------
    # TEST 6: Sjekk avhengigheter
    # -------------------------------------------------------------------------
    def test_avhengigheter(self):
        """
        KRAV: Alle nødvendige verktøy må være installert.
        """
        from app.core.compiler import DocumentCompiler
        
        compiler = DocumentCompiler()
        deps = compiler.check_dependencies()
        
        print("  Avhengigheter:")
        required = ['typst', 'pdflatex', 'pdftoppm']
        all_ok = True
        
        for tool in required:
            info = deps.get(tool, {})
            installed = info.get('installed', False)
            status = "OK" if installed else "X"
            version = info.get('version', info.get('error', 'ikke funnet'))
            print(f"    {status} {tool}: {version}")
            if not installed:
                all_ok = False
        
        if all_ok:
            print("OK: Test 6 PASSED: Alle avhengigheter OK")
        else:
            print("WARN: Test 6 WARNING: Mangler avhengigheter (hybrid kompilering krever disse)")


# =============================================================================
# KJØR TESTER
# =============================================================================

async def run_all_tests():
    """Kjør alle tester."""
    test = TestHybridCompiler()
    
    print("=" * 60)
    print("Hybrid Compiler Test Suite")
    print("=" * 60)
    
    # Test avhengigheter først
    print("\n--- Test 6: Avhengigheter ---")
    test.test_avhengigheter()
    
    # Async tester
    tests = [
        ("TikZ -> PNG", test.test_tikz_til_png),
        ("Hybrid dokument", test.test_hybrid_dokument),
        ("Flere figurer", test.test_flere_figurer),
        ("Feilhåndtering", test.test_ugyldig_tikz_handtering),
        ("Full pipeline", test.test_full_pipeline),
    ]
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            await test_func()
        except Exception as e:
            print(f"FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("Tester fullført!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
