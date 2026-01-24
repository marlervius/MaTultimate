import re

def strip_markdown_fences(code: str) -> str:
    """
    Strips markdown code fences from the start and end of generated code.
    Handles variations like ```typst, ```latex, ```tex, or plain ```.
    Preserves all other content unchanged and is idempotent.
    """
    if not code:
        return ""
    
    # Clean whitespace from start/end first to ensure fences are at the very edges
    code = code.strip()
    
    # Regex to match starting fence: ``` followed by optional language name and newline
    # Regex to match ending fence: ``` at the very end
    start_fence_pattern = r'^```(?:[a-zA-Z]*)\n?'
    end_fence_pattern = r'```$'
    
    # Remove start fence
    code = re.sub(start_fence_pattern, '', code)
    # Remove end fence
    code = re.sub(end_fence_pattern, '', code)
    
    return code.strip()
