"""
MaTultimate Sanitizer
=====================
Renser AI-generert kode for markdown-formatering og andre artefakter.

Kritisk viktig for å sikre at Typst/LaTeX-kode kompilerer uten feil.
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class SanitizeResult:
    """Resultat av sanitering."""
    cleaned_code: str
    changes_made: list[str]
    warnings: list[str]


class CodeSanitizer:
    """
    Renser AI-generert kode for kompilering.
    
    Håndterer:
    - Markdown code fences (```typst, ```latex, etc.)
    - Uønsket whitespace
    - Vanlige AI-feil i Typst/LaTeX
    """
    
    # Mønstre for markdown code fences
    CODE_FENCE_PATTERNS = [
        r'^```(?:typst|typ)\n?',      # ```typst eller ```typ
        r'^```(?:latex|tex)\n?',       # ```latex eller ```tex
        r'^```\w*\n?',                 # Generisk ```språk
        r'^```\n?',                    # Bare ```
        r'\n?```$',                    # Avsluttende ```
        r'^```$',                      # Bare ``` på egen linje
    ]
    
    # Typst-spesifikke feilrettinger
    TYPST_FIXES = [
        # Feil: \frac{a}{b} -> Riktig: frac(a, b) for Typst math
        (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'frac(\1, \2)'),
        # Feil: \sqrt{x} -> Riktig: sqrt(x)
        (r'\\sqrt\{([^}]+)\}', r'sqrt(\1)'),
        # Feil: \cdot -> Riktig: dot eller ·
        (r'\\cdot', r'dot'),
        # Feil: \times -> Riktig: times
        (r'\\times', r'times'),
        # Feil: \infty -> Riktig: oo
        (r'\\infty', r'oo'),
    ]
    
    # LaTeX-spesifikke feilrettinger
    LATEX_FIXES = [
        # Sørg for at $ ikke mangler
        # (Komplekse rettinger håndteres separat)
    ]
    
    def __init__(self):
        # Kompiler regex-mønstre for ytelse
        self.fence_patterns = [re.compile(p, re.MULTILINE) for p in self.CODE_FENCE_PATTERNS]
    
    def sanitize(
        self,
        code: str,
        format: str = 'typst',
        aggressive: bool = False
    ) -> SanitizeResult:
        """
        Hovedmetode for å rense kode.
        
        Args:
            code: Rå AI-generert kode
            format: 'typst' eller 'latex'
            aggressive: Om vi skal gjøre mer aggressive rettinger
            
        Returns:
            SanitizeResult med renset kode og logg
        """
        changes = []
        warnings = []
        result = code
        
        # 1. Fjern markdown code fences
        result, fence_changes = self._remove_code_fences(result)
        changes.extend(fence_changes)
        
        # 2. Normaliser whitespace
        result, ws_changes = self._normalize_whitespace(result)
        changes.extend(ws_changes)
        
        # 3. Format-spesifikke rettinger
        if format.lower() == 'typst':
            result, typst_changes, typst_warnings = self._fix_typst(result, aggressive)
            changes.extend(typst_changes)
            warnings.extend(typst_warnings)
        elif format.lower() in ('latex', 'tex'):
            result, latex_changes, latex_warnings = self._fix_latex(result, aggressive)
            changes.extend(latex_changes)
            warnings.extend(latex_warnings)
        
        # 4. Fjern tomme linjer på starten/slutten
        result = result.strip()
        
        return SanitizeResult(
            cleaned_code=result,
            changes_made=changes,
            warnings=warnings
        )
    
    def _remove_code_fences(self, code: str) -> tuple[str, list[str]]:
        """Fjern markdown code fences."""
        changes = []
        result = code
        
        # Metode 1: Regex
        for pattern in self.fence_patterns:
            if pattern.search(result):
                result = pattern.sub('', result)
                changes.append(f"Fjernet code fence: {pattern.pattern}")
        
        # Metode 2: Linje-for-linje (mer robust)
        lines = result.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Sjekk om linjen er en code fence
            if stripped.startswith('```'):
                changes.append(f"Fjernet code fence på linje {i+1}")
                continue
            
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        return result, changes
    
    def _normalize_whitespace(self, code: str) -> tuple[str, list[str]]:
        """Normaliser whitespace uten å ødelegge formateringen."""
        changes = []
        result = code
        
        # Fjern trailing whitespace på hver linje
        lines = result.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        if lines != cleaned_lines:
            changes.append("Fjernet trailing whitespace")
        
        result = '\n'.join(cleaned_lines)
        
        # Fjern mer enn 2 tomme linjer på rad
        original = result
        result = re.sub(r'\n{4,}', '\n\n\n', result)
        if result != original:
            changes.append("Reduserte antall tomme linjer")
        
        return result, changes
    
    def _fix_typst(
        self,
        code: str,
        aggressive: bool
    ) -> tuple[str, list[str], list[str]]:
        """Fiks Typst-spesifikke problemer."""
        changes = []
        warnings = []
        result = code
        
        # Sjekk for LaTeX-syntaks i Typst
        latex_indicators = [
            (r'\\begin\{', "Fant \\begin{} - dette er LaTeX, ikke Typst"),
            (r'\\end\{', "Fant \\end{} - dette er LaTeX, ikke Typst"),
            (r'\\usepackage', "Fant \\usepackage - dette er LaTeX, ikke Typst"),
            (r'\\documentclass', "Fant \\documentclass - dette er LaTeX, ikke Typst"),
        ]
        
        for pattern, warning in latex_indicators:
            if re.search(pattern, result):
                warnings.append(warning)
        
        # Aggressive rettinger (konverter LaTeX math til Typst)
        if aggressive:
            for pattern, replacement in self.TYPST_FIXES:
                original = result
                result = re.sub(pattern, replacement, result)
                if result != original:
                    changes.append(f"Konverterte LaTeX til Typst: {pattern}")
        
        # Sjekk for ubalanserte Typst-konstruksjoner
        open_brackets = result.count('[') - result.count(']')
        open_parens = result.count('(') - result.count(')')
        open_braces = result.count('{') - result.count('}')
        
        if open_brackets != 0:
            warnings.append(f"Ubalanserte firkantparenteser: {open_brackets:+d}")
        if open_parens != 0:
            warnings.append(f"Ubalanserte parenteser: {open_parens:+d}")
        if open_braces != 0:
            warnings.append(f"Ubalanserte krøllparenteser: {open_braces:+d}")
        
        # Sjekk for vanlige Typst-funksjoner som mangler #
        typst_functions = ['set', 'let', 'import', 'include', 'show', 'if', 'for', 'while']
        for func in typst_functions:
            # Finn tilfeller der funksjonen brukes uten # i starten av linjen
            pattern = rf'^(\s*)({func}\s+)'
            matches = re.findall(pattern, result, re.MULTILINE)
            if matches:
                warnings.append(f"Mulig manglende # før '{func}'")
        
        return result, changes, warnings
    
    def _fix_latex(
        self,
        code: str,
        aggressive: bool
    ) -> tuple[str, list[str], list[str]]:
        """Fiks LaTeX-spesifikke problemer."""
        changes = []
        warnings = []
        result = code
        
        # Sjekk for Typst-syntaks i LaTeX
        typst_indicators = [
            (r'^#set\s', "Fant #set - dette er Typst, ikke LaTeX"),
            (r'^#let\s', "Fant #let - dette er Typst, ikke LaTeX"),
            (r'^#import\s', "Fant #import - dette er Typst, ikke LaTeX"),
        ]
        
        for pattern, warning in typst_indicators:
            if re.search(pattern, result, re.MULTILINE):
                warnings.append(warning)
        
        # Sjekk for ubalanserte miljøer
        begin_count = len(re.findall(r'\\begin\{(\w+)\}', result))
        end_count = len(re.findall(r'\\end\{(\w+)\}', result))
        
        if begin_count != end_count:
            warnings.append(f"Ubalanserte \\begin/\\end: {begin_count} begin, {end_count} end")
        
        # Sjekk for ubalanserte $
        dollar_count = result.count('$')
        # Ignorer escaped dollars
        escaped_dollars = len(re.findall(r'\\\$', result))
        actual_dollars = dollar_count - escaped_dollars
        
        if actual_dollars % 2 != 0:
            warnings.append(f"Oddetall av $ (math mode): {actual_dollars}")
        
        return result, changes, warnings
    
    def quick_strip(self, code: str) -> str:
        """
        Rask fjerning av code fences - for enkel bruk.
        
        Eksempel:
            >>> sanitizer.quick_strip("```typst\\n#let x = 1\\n```")
            '#let x = 1'
        """
        lines = code.strip().split('\n')
        
        # Fjern første linje hvis den er en fence
        if lines and lines[0].strip().startswith('```'):
            lines = lines[1:]
        
        # Fjern siste linje hvis den er en fence
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        
        return '\n'.join(lines)
    
    def detect_format(self, code: str) -> Optional[str]:
        """
        Forsøk å detektere om koden er Typst eller LaTeX.
        
        Returns:
            'typst', 'latex', eller None hvis usikkert
        """
        code_lower = code.lower()
        
        # Typst-indikatorer
        typst_score = 0
        typst_patterns = [
            r'#set\s+\w+',
            r'#let\s+\w+',
            r'#import\s+',
            r'#show\s+',
            r'#heading\s*\[',
            r'#text\s*\(',
            r'#rect\s*\(',
            r'#stack\s*\(',
            r'\$[^$]+\$',  # Typst inline math
        ]
        for p in typst_patterns:
            if re.search(p, code):
                typst_score += 1
        
        # LaTeX-indikatorer
        latex_score = 0
        latex_patterns = [
            r'\\documentclass',
            r'\\usepackage',
            r'\\begin\{document\}',
            r'\\section\{',
            r'\\textbf\{',
            r'\\frac\{',
            r'\\newcommand',
            r'\\def\\',
        ]
        for p in latex_patterns:
            if re.search(p, code):
                latex_score += 1
        
        if typst_score > latex_score:
            return 'typst'
        elif latex_score > typst_score:
            return 'latex'
        else:
            return None


# Singleton for enkel bruk
_default_sanitizer = CodeSanitizer()

def sanitize(code: str, format: str = 'typst', aggressive: bool = False) -> SanitizeResult:
    """Convenience function."""
    return _default_sanitizer.sanitize(code, format, aggressive)

def quick_strip(code: str) -> str:
    """Convenience function."""
    return _default_sanitizer.quick_strip(code)

def detect_format(code: str) -> Optional[str]:
    """Convenience function."""
    return _default_sanitizer.detect_format(code)


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    sanitizer = CodeSanitizer()
    
    print("=== MaTultimate Sanitizer Test ===\n")
    
    # Test 1: Fjern code fences
    test_code_1 = """```typst
#set text(lang: "nb")

= Overskrift

Dette er tekst.
```"""
    
    result_1 = sanitizer.sanitize(test_code_1, 'typst')
    print("Test 1: Fjern code fences")
    print(f"Input:\n{test_code_1}\n")
    print(f"Output:\n{result_1.cleaned_code}\n")
    print(f"Endringer: {result_1.changes_made}\n")
    
    # Test 2: Detect format
    typst_code = "#set text(size: 12pt)\n#let x = 5"
    latex_code = "\\documentclass{article}\n\\begin{document}"
    
    print("Test 2: Detect format")
    print(f"Typst-kode: {sanitizer.detect_format(typst_code)}")
    print(f"LaTeX-kode: {sanitizer.detect_format(latex_code)}")
    
    # Test 3: Warnings
    mixed_code = """#set text(size: 12pt)
\\begin{equation}
x^2 + y^2 = z^2
\\end{equation}
"""
    result_3 = sanitizer.sanitize(mixed_code, 'typst')
    print(f"\nTest 3: Warnings for blandet kode")
    print(f"Warnings: {result_3.warnings}")
    
    print("\n=== Ferdig ===")
