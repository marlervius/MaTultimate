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
    
    # 3. Fiks TYPST-syntaksfeil som AI ofte genererer
    
    # arrow -> pil i lim-uttrykk
    code = code.replace('arrow 0', '-> 0')
    code = code.replace('arrow.r 0', '-> 0')
    code = re.sub(r'arrow\s+(\d)', r'-> \1', code)
    
    # Fjern & i cases (Typst bruker ikke &)
    code = re.sub(r'\s*&\s*"for"', ' "for"', code)
    code = re.sub(r'\s*&\s*"hvis"', ' "hvis"', code)
    code = re.sub(r'\s*&\s*"når"', ' "når"', code)
    
    # Fiks enheter med mellomrom
    code = code.replace('" cm"', '"cm"')
    code = code.replace('" m"', '"m"')
    code = code.replace('" km"', '"km"')
    code = code.replace('" kg"', '"kg"')
    code = code.replace('" g"', '"g"')
    code = code.replace('" s"', '"s"')
    code = code.replace('" kr"', '"kr"')
    
    # Bruk cdot for multiplikasjon (sikrere enn dot)
    code = re.sub(r'\bdot\b', 'dot.c', code)
    
    # 4. Fiks LaTeX-syntaks som AI ofte blander inn
    code = code.replace('\\frac', 'frac')
    code = code.replace('\\sqrt', 'sqrt')
    code = code.replace('\\cdot', 'dot.c')
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
    code = code.replace('\\rightarrow', '->')
    code = code.replace('\\leftarrow', '<-')
    code = code.replace('\\Rightarrow', '=>')
    code = code.replace('\\neq', 'eq.not')
    code = code.replace('\\leq', '<=')
    code = code.replace('\\geq', '>=')
    code = code.replace('\\approx', 'approx')
    
    # 4. Fjern tomme font-attributter som kan oppstå
    code = re.sub(r',\s*,', ',', code)
    code = re.sub(r'\(\s*,', '(', code)
    code = re.sub(r',\s*\)', ')', code)
    
    # 5. Fiks doble linjeskift som kan forårsake problemer
    code = re.sub(r'\n{4,}', '\n\n\n', code)
    
    return code.strip()
