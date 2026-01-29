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


def fix_decimal_commas_in_math(code: str) -> str:
    """
    Konverterer norske desimaltall (2,5) til Typst-format (2.5) i matematikkmodus.
    Komma i Typst math er en separator, ikke desimalskilletegn.
    """
    import re
    
    def fix_math_block(match):
        math_content = match.group(1)
        # Erstatt tall,tall med tall.tall (norsk desimalformat til internasjonal)
        # Match: digit(s), comma, digit(s) - men ikke hvis det er mellomrom etter komma
        fixed = re.sub(r'(\d),(\d)', r'\1.\2', math_content)
        return f'${fixed}$'
    
    # Fiks inline math $...$
    code = re.sub(r'\$([^$]+)\$', fix_math_block, code)
    
    # Fiks også utstilt math $ ... $ (med mellomrom)
    def fix_display_math(match):
        math_content = match.group(1)
        fixed = re.sub(r'(\d),(\d)', r'\1.\2', math_content)
        return f'$ {fixed} $'
    
    code = re.sub(r'\$\s+([^$]+)\s+\$', fix_display_math, code)
    
    return code


def sanitize_typst_code(code: str) -> str:
    """
    Renser og fikser vanlige feil i AI-generert Typst-kode.
    """
    if not code:
        return ""
    
    # 0. Fiks desimaltall med komma -> punktum i matematikkmodus
    code = fix_decimal_commas_in_math(code)
    
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
    
    # Fiks enheter - legg til mellomrom FØR enhet (tall"enhet" -> tall "enhet")
    code = re.sub(r'(\d)"([a-zA-Z])', r'\1 "\2', code)
    
    # Fiks d x -> dif x i integraler
    code = re.sub(r'\bd\s+x\b', 'dif x', code)
    code = re.sub(r'\bd\s+t\b', 'dif t', code)
    code = re.sub(r'\bd\s+y\b', 'dif y', code)
    
    # Fiks multiplikasjon: bruk cdot (IKKE dot.c som kan bli doblet)
    # Først fiks eventuelle dot.c.c feil
    code = code.replace('dot.c.c', 'cdot')
    code = code.replace('dot.c', 'cdot')
    # Erstatt bare frittstående "dot" med cdot (ikke dot.op eller lignende)
    code = re.sub(r'\bdot\b(?!\.)', 'cdot', code)
    
    # 4. Fiks LaTeX-syntaks som AI ofte blander inn
    code = code.replace('\\frac', 'frac')
    code = code.replace('\\sqrt', 'sqrt')
    code = code.replace('\\cdot', 'cdot')
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
