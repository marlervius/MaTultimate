#!/usr/bin/env python3
"""
FigurAgent Test Suite
=====================
Konkrete test-cases for å validere FigurAgent-implementasjonen.

Kjør: pytest tests/test_figur_agent.py -v
Eller: python tests/test_figur_agent.py
"""

import sys
sys.path.insert(0, '/home/claude/matultimate/backend')

import pytest
from typing import Optional


# =============================================================================
# TEST CASES - Gi disse til Cursor-agenten
# =============================================================================

class TestFigurAgentSpec:
    """
    Spesifikasjonstester for FigurAgent.
    Hver test beskriver forventet oppførsel.
    """
    
    # -------------------------------------------------------------------------
    # TEST 1: Enkel funksjonsplot
    # -------------------------------------------------------------------------
    def test_funksjonsplot_enkel(self):
        """
        KRAV: Skal generere en enkel graf av f(x) = x²
        
        Input:
            figur_type: FUNKSJONSPLOT
            funksjon: "x**2"
            x_range: (-3, 3)
        
        Forventet output (TikZ):
            - Inneholder \begin{tikzpicture}
            - Inneholder \begin{axis}
            - Inneholder \addplot med {x^2}
            - Har axis lines=middle
            - Har xlabel=$x$, ylabel=$y$
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.FUNKSJONSPLOT,
            funksjon="x**2",
            x_range=(-3, 3),
        )
        
        tikz = agent.generer(request)
        
        # Assertions
        assert "\\begin{tikzpicture}" in tikz
        assert "\\begin{axis}" in tikz
        assert "\\addplot" in tikz
        assert "x^2" in tikz or "x**2" in tikz
        assert "\\end{axis}" in tikz
        assert "\\end{tikzpicture}" in tikz
        
        print("OK: Test 1 PASSED: Enkel funksjonsplot")
        print(f"  Output (første 200 tegn):\n  {tikz[:200]}...")
    
    # -------------------------------------------------------------------------
    # TEST 2: Funksjonsplot med tangent (KRITISK for R1)
    # -------------------------------------------------------------------------
    def test_funksjonsplot_med_tangent(self):
        """
        KRAV: Skal generere graf med tangentlinje i gitt punkt.
        
        Input:
            figur_type: FUNKSJONSPLOT_TANGENT
            funksjon: "x**2 - 2*x"
            tangent_x: 3
            x_range: (-1, 5)
        
        Matematikk som må beregnes:
            f(x) = x² - 2x
            f(3) = 9 - 6 = 3
            f'(x) = 2x - 2
            f'(3) = 4
            Tangent: y - 3 = 4(x - 3)  =>  y = 4x - 9
        
        Forventet output:
            - Hovedfunksjon plottet
            - Tangentlinje y = 4x - 9 (eller tilsvarende)
            - Punkt markert ved (3, 3)
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.FUNKSJONSPLOT_TANGENT,
            funksjon="x**2 - 2*x",
            tangent_x=3.0,
            x_range=(-1, 5),
        )
        
        tikz = agent.generer(request)
        
        # Skal ha to \addplot (funksjon + tangent)
        assert tikz.count("\\addplot") >= 2, "Mangler tangentlinje"
        
        # Skal ha punkt-markering
        assert "node" in tikz.lower() or "circle" in tikz.lower(), "Mangler punktmarkering"
        
        # Tangentens stigningstall skal være 4
        # (kan være formatert som 4, 4.0, eller 4*x)
        assert "4" in tikz, "Tangentens stigningstall (4) ikke funnet"
        
        print("OK: Test 2 PASSED: Funksjonsplot med tangent")
        print(f"  Tangent i x=3 for f(x)=x²-2x")
    
    # -------------------------------------------------------------------------
    # TEST 3: Areal under kurve (KRITISK for R2 integrasjon)
    # -------------------------------------------------------------------------
    def test_areal_under_kurve(self):
        """
        KRAV: Skal generere graf med skravert areal mellom kurve og x-akse.
        
        Input:
            figur_type: AREAL_UNDER_KURVE
            funksjon: "x**2"
            nedre_grense: 0
            ovre_grense: 2
        
        Forventet output:
            - Funksjon plottet
            - Skravert område fra x=0 til x=2
            - fill opacity for synlighet
            - \closedcycle for lukket område
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.AREAL_UNDER_KURVE,
            funksjon="x**2",
            nedre_grense=0,
            ovre_grense=2,
            x_range=(-1, 3),
        )
        
        tikz = agent.generer(request)
        
        assert "fill" in tikz.lower(), "Mangler fill for skravering"
        assert "closedcycle" in tikz.lower() or "closed" in tikz.lower(), "Mangler closedcycle"
        
        print("OK: Test 3 PASSED: Areal under kurve")
    
    # -------------------------------------------------------------------------
    # TEST 4: Normalfordeling (KRITISK for S2 statistikk)
    # -------------------------------------------------------------------------
    def test_normalfordeling(self):
        """
        KRAV: Skal generere normalfordelingskurve med skravert område.
        
        Input:
            figur_type: NORMALFORDELING
            mu: 0
            sigma: 1
            skraver_fra: -1
            skraver_til: 1
        
        Forventet output:
            - Gaussisk klokkeform
            - Skravert område mellom -1 og 1 (ca. 68%)
            - Korrekt formel: 1/(σ√(2π)) * e^(-(x-μ)²/(2σ²))
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.NORMALFORDELING,
            mu=0,
            sigma=1,
            skraver_fra=-1,
            skraver_til=1,
        )
        
        tikz = agent.generer(request)
        
        # Skal inneholde normalfordelingsformel-elementer
        assert "exp" in tikz.lower(), "Mangler eksponentialfunksjon"
        assert "sqrt" in tikz.lower() or "pi" in tikz.lower(), "Mangler sqrt eller pi"
        assert "fill" in tikz.lower(), "Mangler skravering"
        
        print("OK: Test 4 PASSED: Normalfordeling")
    
    # -------------------------------------------------------------------------
    # TEST 5: Trigonometrisk funksjon
    # -------------------------------------------------------------------------
    def test_trigonometrisk_funksjon(self):
        """
        KRAV: Skal håndtere trigonometriske funksjoner korrekt.
        
        Input:
            figur_type: FUNKSJONSPLOT
            funksjon: "sin(x)"
            x_range: (-2*pi, 2*pi)  eller (-6.28, 6.28)
        
        Forventet:
            - sin(x) plottet korrekt (pgfplots forstår sin)
            - x-akse fra -2π til 2π
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        import math
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.FUNKSJONSPLOT,
            funksjon="sin(x)",
            x_range=(-2*math.pi, 2*math.pi),
        )
        
        tikz = agent.generer(request)
        
        assert "sin" in tikz.lower()
        assert "\\addplot" in tikz
        
        print("OK: Test 5 PASSED: Trigonometrisk funksjon")
    
    # -------------------------------------------------------------------------
    # TEST 6: Eksponentialfunksjon
    # -------------------------------------------------------------------------
    def test_eksponentialfunksjon(self):
        """
        KRAV: Skal håndtere e^x korrekt.
        
        Input:
            funksjon: "exp(x)"
        
        Forventet:
            - Konverteres til pgfplots-kompatibel syntaks
            - exp(x) eller e^x i output
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.FUNKSJONSPLOT,
            funksjon="exp(x)",
            x_range=(-2, 3),
        )
        
        tikz = agent.generer(request)
        
        assert "exp" in tikz.lower() or "e^" in tikz
        
        print("OK: Test 6 PASSED: Eksponentialfunksjon")
    
    # -------------------------------------------------------------------------
    # TEST 7: Logaritmisk funksjon
    # -------------------------------------------------------------------------
    def test_logaritmisk_funksjon(self):
        """
        KRAV: Skal håndtere ln(x) korrekt.
        
        Input:
            funksjon: "ln(x)"
            x_range: (0.1, 5)  # Må starte > 0
        
        Forventet:
            - ln(x) i pgfplots-format
            - Korrekt domene (x > 0)
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.FUNKSJONSPLOT,
            funksjon="ln(x)",
            x_range=(0.1, 5),
        )
        
        tikz = agent.generer(request)
        
        assert "ln" in tikz.lower() or "log" in tikz.lower()
        
        print("OK: Test 7 PASSED: Logaritmisk funksjon")
    
    # -------------------------------------------------------------------------
    # TEST 8: Sympy-til-TikZ konvertering
    # -------------------------------------------------------------------------
    def test_sympy_til_tikz_konvertering(self):
        """
        KRAV: Intern metode skal konvertere SymPy-syntaks til pgfplots.
        
        Konverteringer:
            x**2      ->  x^2
            x**3      ->  x^3  
            exp(x)    ->  exp(x)   (OK i pgfplots)
            ln(x)     ->  ln(x)    (OK i pgfplots)
            sqrt(x)   ->  sqrt(x)  (OK i pgfplots)
            pi        ->  pi       (OK i pgfplots)
            2*x       ->  2*x      (OK)
        """
        from app.agents.figur_agent import FigurAgent
        
        agent = FigurAgent()
        
        test_cases = [
            ("x**2", "x^2"),
            ("x**3 + 2*x", "x^3 + 2*x"),
            ("3*x**2 - 2*x + 1", "3*x^2 - 2*x + 1"),
        ]
        
        for sympy_expr, expected_contains in test_cases:
            result = agent._sympy_til_tikz(sympy_expr)
            # ** skal bli ^
            assert "**" not in result, f"Fant ** i output: {result}"
            print(f"  '{sympy_expr}' -> '{result}'")
        
        print("OK: Test 8 PASSED: SymPy-til-TikZ konvertering")
    
    # -------------------------------------------------------------------------
    # TEST 9: Komplett LaTeX-output (ingen document-wrapper)
    # -------------------------------------------------------------------------
    def test_output_er_ren_tikz(self):
        """
        KRAV: Output skal være REN TikZ, IKKE komplett LaTeX-dokument.
        
        Skal IKKE inneholde:
            - \\documentclass
            - \\begin{document}
            - \\usepackage
        
        Skal inneholde:
            - \\begin{tikzpicture}
            - \\end{tikzpicture}
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        request = FigurRequest(
            figur_type=FigurType.FUNKSJONSPLOT,
            funksjon="x**2",
        )
        
        tikz = agent.generer(request)
        
        # Skal IKKE ha document-wrapper
        assert "\\documentclass" not in tikz, "Output skal ikke ha \\documentclass"
        assert "\\begin{document}" not in tikz, "Output skal ikke ha \\begin{document}"
        
        # Skal ha tikzpicture
        assert "\\begin{tikzpicture}" in tikz
        assert "\\end{tikzpicture}" in tikz
        
        print("OK: Test 9 PASSED: Output er ren TikZ")
    
    # -------------------------------------------------------------------------
    # TEST 10: Integrasjon med MathEngine for tangentberegning
    # -------------------------------------------------------------------------
    def test_tangent_bruker_math_engine(self):
        """
        KRAV: Tangentberegning skal bruke MathEngine for korrekthet.
        
        For f(x) = x³ - 3x, tangent i x = 2:
            f(2) = 8 - 6 = 2
            f'(x) = 3x² - 3
            f'(2) = 12 - 3 = 9
            Tangent: y = 9(x - 2) + 2 = 9x - 16
        
        Test at agenten beregner dette korrekt via MathEngine.
        """
        from app.agents.figur_agent import FigurAgent, FigurRequest, FigurType
        
        agent = FigurAgent()
        
        # Bruk intern metode for å teste tangentberegning
        tangent_ligning, y_verdi = agent._beregn_tangent("x**3 - 3*x", 2.0)
        
        # y-verdi skal være 2
        assert abs(y_verdi - 2.0) < 0.01, f"Feil y-verdi: {y_verdi}, forventet 2"
        
        # Tangentligning skal inneholde stigningstall 9
        assert "9" in tangent_ligning, f"Feil stigningstall i: {tangent_ligning}"
        
        print("OK: Test 10 PASSED: Tangent bruker MathEngine")
        print(f"  f(x) = x³ - 3x, tangent i x=2: y = {tangent_ligning}")


# =============================================================================
# KJØR TESTER
# =============================================================================

def run_all_tests():
    """Kjør alle tester manuelt."""
    test_instance = TestFigurAgentSpec()
    
    tests = [
        ("Enkel funksjonsplot", test_instance.test_funksjonsplot_enkel),
        ("Funksjonsplot med tangent", test_instance.test_funksjonsplot_med_tangent),
        ("Areal under kurve", test_instance.test_areal_under_kurve),
        ("Normalfordeling", test_instance.test_normalfordeling),
        ("Trigonometrisk funksjon", test_instance.test_trigonometrisk_funksjon),
        ("Eksponentialfunksjon", test_instance.test_eksponentialfunksjon),
        ("Logaritmisk funksjon", test_instance.test_logaritmisk_funksjon),
        ("SymPy-til-TikZ", test_instance.test_sympy_til_tikz_konvertering),
        ("Ren TikZ output", test_instance.test_output_er_ren_tikz),
        ("Tangent med MathEngine", test_instance.test_tangent_bruker_math_engine),
    ]
    
    print("=" * 60)
    print("FigurAgent Test Suite")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Resultat: {passed} PASSED, {failed} FAILED")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
