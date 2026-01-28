import re

def strip_markdown_fences(code: str) -> str:
    """
    Fjerner markdown code fences (```) fra AI-generert kode.
    """
    if not code:
        return ""
    
    # Fjern start-fence
    code = re.sub(r'^```(?:[a-zA-Z]*)\n?', '', code.strip())
    # Fjern slutt-fence
    code = re.sub(r'```$', '', code.strip())
    
    return code.strip()


def sanitize_typst_code(code: str) -> str:
    """
    Renser og fikser vanlige feil i AI-generert Typst-kode.
    """
    if not code:
        return ""
    
    # 1. Fjern markdown fences
    code = strip_markdown_fences(code)
    
    # 2. Fjern HELE #set text linjer som inneholder font-spesifikasjoner
    # og erstatt med en ren versjon
    code = re.sub(
        r'#set\s+text\s*\([^)]*font:[^)]*\)',
        '#set text(lang: "nb", size: 11pt)',
        code,
        flags=re.IGNORECASE
    )
    
    # 3. Fiks LaTeX-syntaks som AI ofte blander inn
    # \frac{a}{b} -> $frac(a, b)$ (men bare utenfor $ $)
    code = code.replace('\\frac', 'frac')
    code = code.replace('\\sqrt', 'sqrt')
    code = code.replace('\\cdot', 'dot')
    code = code.replace('\\times', 'times')
    code = code.replace('\\div', 'div')
    code = code.replace('\\pm', 'plus.minus')
    code = code.replace('\\infty', 'infinity')
    code = code.replace('\\pi', 'pi')
    code = code.replace('\\alpha', 'alpha')
    code = code.replace('\\beta', 'beta')
    code = code.replace('\\gamma', 'gamma')
    code = code.replace('\\theta', 'theta')
    code = code.replace('\\Delta', 'Delta')
    code = code.replace('\\sum', 'sum')
    code = code.replace('\\int', 'integral')
    code = code.replace('\\lim', 'lim')
    code = code.replace('\\rightarrow', 'arrow.r')
    code = code.replace('\\leftarrow', 'arrow.l')
    code = code.replace('\\Rightarrow', 'arrow.r.double')
    code = code.replace('\\neq', 'eq.not')
    code = code.replace('\\leq', 'lt.eq')
    code = code.replace('\\geq', 'gt.eq')
    code = code.replace('\\approx', 'approx')
    
    # 4. Fjern tomme font-attributter som kan oppstå
    code = re.sub(r',\s*,', ',', code)
    code = re.sub(r'\(\s*,', '(', code)
    code = re.sub(r',\s*\)', ')', code)
    
    # 5. Fiks doble linjeskift som kan forårsake problemer
    code = re.sub(r'\n{4,}', '\n\n\n', code)
    
    return code.strip()
