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
