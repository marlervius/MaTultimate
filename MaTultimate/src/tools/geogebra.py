import re
from typing import Optional, List, Dict
import hashlib

# Predefined graph templates
GRAPH_TEMPLATES = {
    "linear": {
        "title": "Lineær funksjon",
        "commands": ["f(x) = 2x + 1", "SetColor(f, \"#f0b429\")", "ShowLabel(f, true)"],
        "description": "Graf av en lineær funksjon y = ax + b",
    },
    "quadratic": {
        "title": "Andregradsfunksjon",
        "commands": ["f(x) = x^2 - 2x - 3", "SetColor(f, \"#3b82f6\")", "ShowLabel(f, true)", "A = Root(f)", "B = Vertex(f)"],
        "description": "Graf av en andregradsfunksjon med nullpunkter og toppunkt",
    },
    "trigonometric": {
        "title": "Trigonometriske funksjoner",
        "commands": ["f(x) = sin(x)", "g(x) = cos(x)", "SetColor(f, \"#f0b429\")", "SetColor(g, \"#3b82f6\")"],
        "description": "Graf av sinus og cosinus",
    },
}

def get_geogebra_embed_html(
    commands: List[str],
    width: int = 600,
    height: int = 400,
    show_toolbar: bool = False,
    show_algebra_input: bool = False
) -> str:
    commands_js = "[" + ", ".join([f'"{cmd}"' for cmd in commands]) + "]"
    unique_id = hashlib.md5("".join(commands).encode()).hexdigest()[:8]
    
    return f"""
    <div id="ggb-container-{unique_id}" style="border: 1px solid #374151; border-radius: 12px; overflow: hidden; margin: 1rem 0; background: white;">
        <div id="ggb-element-{unique_id}" style="width: {width}px; height: {height}px;"></div>
    </div>
    <script src="https://www.geogebra.org/apps/deployggb.js"></script>
    <script>
    (function() {{
        var params = {{
            "appName": "graphing",
            "width": {width},
            "height": {height},
            "showToolBar": {str(show_toolbar).lower()},
            "showAlgebraInput": {str(show_algebra_input).lower()},
            "language": "nb",
            "country": "NO",
            "appletOnLoad": function(api) {{
                var commands = {commands_js};
                commands.forEach(function(cmd) {{
                    api.evalCommand(cmd);
                }});
            }}
        }};
        var applet = new GGBApplet(params, true);
        applet.inject('ggb-element-{unique_id}');
    }})();
    </script>
    """

def extract_functions_from_content(content: str) -> List[str]:
    functions = []
    # Simple pattern for f(x) = ...
    pattern = r'([a-zA-Z])\s*\(\s*x\s*\)\s*=\s*([^$\n]+)'
    matches = re.finditer(pattern, content)
    for match in matches:
        func_name = match.group(1)
        func_expr = match.group(2).strip()
        # Basic cleanup for GeoGebra
        func_expr = func_expr.replace('\\', '').replace('{', '(').replace('}', ')')
        functions.append(f"{func_name}(x) = {func_expr}")
    return functions
