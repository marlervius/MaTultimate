import subprocess
import os
import tempfile
import base64
import time
import shutil
import asyncio
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class FigureResult:
    success: bool
    png_bytes: Optional[bytes] = None
    png_base64: Optional[str] = None
    log: str = ""

@dataclass
class CompilationResult:
    success: bool
    pdf_bytes: Optional[bytes] = None
    pdf_base64: Optional[str] = None
    log: str = ""
    warnings: List[str] = field(default_factory=list)
    compilation_time_ms: int = 0

class DocumentCompiler:
    """
    Håndterer kompilering av Typst, LaTeX og Hybrid (Typst + TikZ) dokumenter.
    """

    def _wrap_tikz_standalone(self, tikz_code: str) -> str:
        """Wrap TikZ i standalone dokument med alle nødvendige pakker."""
        return r"""\documentclass[tikz,border=5pt]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{tikz}
\usetikzlibrary{calc,positioning,arrows.meta}

\begin{document}
""" + tikz_code + r"""
\end{document}
"""

    async def compile_latex_figure_to_png(self, tikz_code: str, dpi: int = 300, timeout: int = 30) -> FigureResult:
        """
        Kompilerer en TikZ-figur til PNG ved bruk av pdflatex og pdftoppm.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            tex_file = tmp_path / "figure.tex"
            pdf_file = tmp_path / "figure.pdf"
            png_base = tmp_path / "figure"
            png_file = tmp_path / "figure-1.png" # pdftoppm legger til -1 med -singlefile noen ganger, eller bare .png
            
            # Wrap og lagre
            standalone_code = self._wrap_tikz_standalone(tikz_code)
            tex_file.write_text(standalone_code, encoding="utf-8")
            
            try:
                # 1. pdflatex
                process = await asyncio.create_subprocess_exec(
                    "pdflatex", "-interaction=nonstopmode", "figure.tex",
                    cwd=tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                if process.returncode != 0:
                    return FigureResult(success=False, log=f"pdflatex feilet: {stdout.decode()}")

                if not pdf_file.exists():
                    return FigureResult(success=False, log="PDF ble ikke generert")

                # 2. pdftoppm (foretrukket)
                process = await asyncio.create_subprocess_exec(
                    "pdftoppm", "-png", "-r", str(dpi), "-singlefile", "figure.pdf", "figure",
                    cwd=tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                # pdftoppm -singlefile lager figure.png
                actual_png = tmp_path / "figure.png"
                if not actual_png.exists():
                    # Noen versjoner lager figure-1.png
                    actual_png = tmp_path / "figure-1.png"

                if actual_png.exists():
                    png_bytes = actual_png.read_bytes()
                    return FigureResult(
                        success=True,
                        png_bytes=png_bytes,
                        png_base64=base64.b64encode(png_bytes).decode("utf-8")
                    )
                else:
                    return FigureResult(success=False, log=f"PNG ble ikke generert av pdftoppm: {stderr.decode()}")

            except asyncio.TimeoutError:
                return FigureResult(success=False, log="Kompilering timet ut")
            except FileNotFoundError as e:
                return FigureResult(success=False, log=f"Mangler verktøy: {str(e)}")
            except Exception as e:
                return FigureResult(success=False, log=f"Uventet feil: {str(e)}")

    async def compile_hybrid(self, typst_code: str, figures: List[Dict[str, str]]) -> CompilationResult:
        """
        Orkestrerer hybrid kompilering: TikZ -> PNG -> Typst -> PDF.
        figures: list av {"id": "fig_0", "latex": "..."}
        """
        start_time = time.time()
        warnings = []
        
        with tempfile.TemporaryDirectory() as session_dir:
            session_path = Path(session_dir)
            fig_dir = session_path / "figurer"
            fig_dir.mkdir(exist_ok=True)
            
            # 1. Kompiler alle figurer
            for fig in figures:
                fig_id = fig.get("id")
                latex = fig.get("latex")
                
                res = await self.compile_latex_figure_to_png(latex)
                if res.success:
                    (fig_dir / f"{fig_id}.png").write_bytes(res.png_bytes)
                else:
                    warnings.append(f"Kunne ikke generere figur {fig_id}: {res.log}")
            
            # 2. Lagre Typst-fil
            typst_file = session_path / "document.typ"
            typst_file.write_text(typst_code, encoding="utf-8")
            pdf_file = session_path / "document.pdf"
            
            # 3. Kompiler Typst
            try:
                process = await asyncio.create_subprocess_exec(
                    "typst", "compile", str(typst_file), str(pdf_file),
                    cwd=session_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if pdf_file.exists():
                    pdf_bytes = pdf_file.read_bytes()
                    return CompilationResult(
                        success=True,
                        pdf_bytes=pdf_bytes,
                        pdf_base64=base64.b64encode(pdf_bytes).decode("utf-8"),
                        warnings=warnings,
                        compilation_time_ms=int((time.time() - start_time) * 1000)
                    )
                else:
                    return CompilationResult(
                        success=False,
                        log=f"Typst feilet: {stderr.decode()}",
                        warnings=warnings
                    )
            except Exception as e:
                return CompilationResult(success=False, log=str(e), warnings=warnings)

    def check_dependencies(self) -> Dict[str, Any]:
        """Sjekk at verktøyene finnes."""
        results = {}
        for tool, cmd in [
            ('typst', ['typst', '--version']),
            ('pdflatex', ['pdflatex', '--version']),
            ('pdftoppm', ['pdftoppm', '-v']),
        ]:
            try:
                proc = subprocess.run(cmd, capture_output=True, timeout=5)
                results[tool] = {
                    'installed': True,
                    'version': (proc.stdout or proc.stderr).decode().split('\n')[0].strip()
                }
            except Exception as e:
                results[tool] = {'installed': False, 'error': str(e)}
        return results

async def compile_latex_to_pdf(latex_code: str) -> Tuple[Optional[str], Optional[str]]:
    """Legacy wrapper for bakoverkompatibilitet."""
    compiler = DocumentCompiler()
    # Enkel implementasjon for nå
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_file = tmp_path / "document.tex"
        tex_file.write_text(latex_code, encoding="utf-8")
        try:
            process = await asyncio.create_subprocess_exec(
                "pdflatex", "-interaction=nonstopmode", "document.tex",
                cwd=tmpdir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            pdf_file = tmp_path / "document.pdf"
            if pdf_file.exists():
                return base64.b64encode(pdf_file.read_bytes()).decode("utf-8"), None
            return None, "Kompilering feilet"
        except Exception as e:
            return None, str(e)

async def compile_typst_to_pdf(typst_code: str) -> Tuple[Optional[str], Optional[str]]:
    """Legacy wrapper for bakoverkompatibilitet."""
    compiler = DocumentCompiler()
    # Enkel implementasjon
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        typ_file = tmp_path / "document.typ"
        typ_file.write_text(typst_code, encoding="utf-8")
        pdf_file = tmp_path / "document.pdf"
        try:
            process = await asyncio.create_subprocess_exec(
                "typst", "compile", str(typ_file), str(pdf_file),
                cwd=tmpdir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            if pdf_file.exists():
                return base64.b64encode(pdf_file.read_bytes()).decode("utf-8"), None
            return None, "Kompilering feilet"
        except Exception as e:
            return None, str(e)
