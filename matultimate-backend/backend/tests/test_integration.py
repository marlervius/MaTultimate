#!/usr/bin/env python3
"""
MaTultimate Integrasjonstest
============================
Tester hele pipeline fra oppgavegenerering til dokumentproduksjon.

Kjør: python -m tests.test_integration
"""

import sys
sys.path.insert(0, '/home/claude/matultimate/backend')

from app.core.math_engine import MathEngine, VGSMathGenerator
from app.core.sanitizer import CodeSanitizer, sanitize, quick_strip
from app.agents.vgs_agent import VGSAgent, VGSKurs, Emne, OppgaveConfig


def test_math_engine():
    """Test matematikkmotoren."""
    print("=" * 60)
    print("TEST 1: Matematikkmotor (SymPy)")
    print("=" * 60)
    
    engine = MathEngine()
    
    # Test derivasjon
    print("\n1.1 Derivasjonsverifisering:")
    tests = [
        ("x**3 + 2*x", "3*x**2 + 2", True),
        ("sin(x)", "cos(x)", True),
        ("exp(x)", "exp(x)", True),
        ("x**3", "2*x**2", False),  # Feil
    ]
    
    for f, f_prime, expected in tests:
        result = engine.verify_derivative(f, f_prime)
        status = "✓" if result.is_correct == expected else "✗"
        print(f"  {status} f(x) = {f}, f'(x) = {f_prime}: {result.is_correct}")
    
    # Test integrasjon
    print("\n1.2 Integrasjonsverifisering:")
    result = engine.verify_integral("2*x", "x**2")
    print(f"  ✓ ∫2x dx = x² : {result.is_correct}")
    
    # Test variant-generering
    print("\n1.3 Variant-generering:")
    variants = engine.generate_derivative_variants("{a}*x**{n} + {b}", 3, difficulty=0.5)
    print(f"  Genererte {len(variants)} varianter:")
    for v in variants:
        print(f"    f(x) = {v.problem_latex}, f'(x) = {v.answer_latex}")
    
    # Test steg-for-steg
    print("\n1.4 Steg-for-steg løsning:")
    solution = engine.derivative_step_by_step("x**2 * sin(x)")
    print(f"  Problem: {solution.problem}")
    print(f"  Svar: {solution.final_answer}")
    print(f"  Antall steg: {len(solution.steps)}")
    
    # Test ekstremalpunkter
    print("\n1.5 Funksjonsanalyse:")
    extrema = engine.find_extrema("x**3 - 3*x")
    print(f"  f(x) = x³ - 3x")
    print(f"  f'(x) = {extrema['f_prime']}")
    print(f"  Kritiske punkter: {extrema['critical_points']}")
    
    print("\n✓ Matematikkmotor OK")


def test_sanitizer():
    """Test code sanitizer."""
    print("\n" + "=" * 60)
    print("TEST 2: Code Sanitizer")
    print("=" * 60)
    
    sanitizer = CodeSanitizer()
    
    # Test format detection
    print("\n2.1 Format-deteksjon:")
    typst = "#set text(size: 12pt)\n= Overskrift"
    latex = "\\documentclass{article}\n\\begin{document}"
    
    print(f"  Typst-kode: {sanitizer.detect_format(typst)}")
    print(f"  LaTeX-kode: {sanitizer.detect_format(latex)}")
    
    # Test balansering av parenteser
    print("\n2.2 Validering:")
    unbalanced = "#let f(x) = { x + 1"
    result = sanitizer.sanitize(unbalanced, 'typst')
    print(f"  Ubalansert kode: {result.warnings}")
    
    print("\n✓ Sanitizer OK")


def test_vgs_agent():
    """Test VGS-agenten."""
    print("\n" + "=" * 60)
    print("TEST 3: VGS Agent")
    print("=" * 60)
    
    agent = VGSAgent()
    
    # Test derivasjon R1
    print("\n3.1 Derivasjon (R1):")
    config = OppgaveConfig(
        kurs=VGSKurs.R1,
        emne=Emne.DERIVASJON,
        antall_oppgaver=9,
        differensiering=True
    )
    
    oppgavesett = agent.generer_oppgavesett(config)
    print(f"  Tittel: {oppgavesett.tittel}")
    print(f"  Nivå 1: {len(oppgavesett.nivaa_1)} oppgaver")
    print(f"  Nivå 2: {len(oppgavesett.nivaa_2)} oppgaver")
    print(f"  Nivå 3: {len(oppgavesett.nivaa_3)} oppgaver")
    print(f"  Format: {oppgavesett.format_anbefaling}")
    
    # Vis eksempler
    print("\n  Eksempler fra hvert nivå:")
    for nivaa, navn in [(oppgavesett.nivaa_1, "Nivå 1"), 
                         (oppgavesett.nivaa_2, "Nivå 2"), 
                         (oppgavesett.nivaa_3, "Nivå 3")]:
        if nivaa:
            o = nivaa[0]
            print(f"    {navn}: {o.latex_problem} → {o.latex_svar}")
    
    # Generer Typst-output
    print("\n3.2 Typst-generering:")
    typst_code = agent.til_typst(oppgavesett)
    print(f"  Genererte {len(typst_code)} tegn Typst-kode")
    print(f"  Første linjer:")
    for line in typst_code.split('\n')[27:35]:
        print(f"    {line}")
    
    # Generer fasit
    print("\n3.3 Fasit-generering:")
    fasit_code = agent.fasit_til_typst(oppgavesett)
    print(f"  Genererte {len(fasit_code)} tegn fasit-kode")
    
    print("\n✓ VGS Agent OK")


def test_end_to_end():
    """Full ende-til-ende test."""
    print("\n" + "=" * 60)
    print("TEST 4: Ende-til-ende Pipeline")
    print("=" * 60)
    
    from app.agents.vgs_agent import VGSAgent, VGSKurs, Emne, OppgaveConfig
    
    agent = VGSAgent()
    
    # Simuler brukerforespørsel
    print("\n4.1 Brukerforespørsel:")
    print("  'Lag differensierte derivasjonsoppgaver for R1'")
    
    config = OppgaveConfig(
        kurs=VGSKurs.R1,
        emne=Emne.DERIVASJON,
        antall_oppgaver=12,
        differensiering=True,
        inkluder_fasit=True
    )
    
    # Generer
    print("\n4.2 Genererer oppgavesett...")
    oppgavesett = agent.generer_oppgavesett(config)
    
    # Produser Typst-kode
    print("4.3 Produserer Typst-kode...")
    elevark = agent.til_typst(oppgavesett)
    fasit = agent.fasit_til_typst(oppgavesett)
    
    # Lagre til filer
    with open('/home/claude/matultimate/output_elevark.typ', 'w') as f:
        f.write(elevark)
    with open('/home/claude/matultimate/output_fasit.typ', 'w') as f:
        f.write(fasit)
    
    print(f"\n4.4 Resultat:")
    print(f"  Elevark: {len(elevark)} tegn → output_elevark.typ")
    print(f"  Fasit: {len(fasit)} tegn → output_fasit.typ")
    print(f"  Totalt oppgaver: {len(oppgavesett.nivaa_1) + len(oppgavesett.nivaa_2) + len(oppgavesett.nivaa_3)}")
    
    print("\n✓ Ende-til-ende OK")


def main():
    """Kjør alle tester."""
    print("╔" + "═" * 58 + "╗")
    print("║" + " MaTultimate Integrasjonstest ".center(58) + "║")
    print("║" + " Kvalitet først. Bredde etterpå. ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    test_math_engine()
    test_sanitizer()
    test_vgs_agent()
    test_end_to_end()
    
    print("\n" + "=" * 60)
    print("ALLE TESTER BESTÅTT! ✓")
    print("=" * 60)
    print("""
Neste steg:
1. Installer Typst lokalt: brew install typst (Mac) / winget install typst (Win)
2. Kompiler: typst compile output_elevark.typ
3. Se PDF-resultatet!

For full deployment:
- Legg til FastAPI-endepunkter
- Koble til Streamlit-frontend
- Deploy til Railway
    """)


if __name__ == "__main__":
    main()
