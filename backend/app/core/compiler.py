import subprocess
import os
import tempfile
import base64
from pathlib import Path
from typing import Optional, Tuple

def compile_latex_to_pdf(latex_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Compiles LaTeX code to PDF using pdflatex.
    Returns (pdf_base64, error_message).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_file = tmp_path / "document.tex"
        tex_file.write_text(latex_code, encoding="utf-8")
        
        try:
            # Run pdflatex twice for references/toc
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "document.tex"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )
            
            pdf_file = tmp_path / "document.pdf"
            if pdf_file.exists():
                with open(pdf_file, "rb") as f:
                    pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
                return pdf_base64, None
            else:
                return None, f"PDF file not created. Log: {result.stdout}"
                
        except subprocess.TimeoutExpired:
            return None, "Compilation timed out (30s)"
        except Exception as e:
            return None, str(e)

def compile_typst_to_pdf(typst_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Compiles Typst code to PDF using typst CLI.
    Returns (pdf_base64, error_message).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        typ_file = tmp_path / "document.typ"
        typ_file.write_text(typst_code, encoding="utf-8")
        pdf_file = tmp_path / "document.pdf"
        
        try:
            result = subprocess.run(
                ["typst", "compile", str(typ_file), str(pdf_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=20
            )
            
            if pdf_file.exists():
                with open(pdf_file, "rb") as f:
                    pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
                return pdf_base64, None
            else:
                return None, f"Typst compilation failed: {result.stderr}"
                
        except FileNotFoundError:
            return None, "Typst CLI not installed on server"
        except subprocess.TimeoutExpired:
            return None, "Compilation timed out (20s)"
        except Exception as e:
            return None, str(e)
