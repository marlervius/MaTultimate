"""
MaTultimate Compiler
====================
Kompileringsmotor for Typst, LaTeX og hybrid-dokumenter.

Støtter:
- Typst → PDF (rask, primær)
- LaTeX → PDF (full pakke-støtte)
- LaTeX figur → PNG (for inkludering i Typst)
- Hybrid: Typst-dokument med LaTeX-figurer
"""

import asyncio
import subprocess
import tempfile
import shutil
import base64
import uuid
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from .sanitizer import CodeSanitizer, SanitizeResult

logger = logging.getLogger(__name__)


class CompilationError(Exception):
    """Feil under kompilering."""
    def __init__(self, message: str, log: str = "", source_code: str = ""):
        super().__init__(message)
        self.log = log
        self.source_code = source_code


class DocumentFormat(str, Enum):
    TYPST = "typst"
    LATEX = "latex"
    HYBRID = "hybrid"


@dataclass
class CompilationResult:
    """Resultat av kompilering."""
    success: bool
    pdf_bytes: Optional[bytes] = None
    pdf_base64: Optional[str] = None
    log: str = ""
    warnings: list[str] = field(default_factory=list)
    compilation_time_ms: int = 0
    source_code: str = ""


@dataclass
class FigureResult:
    """Resultat av figur-kompilering."""
    success: bool
    png_bytes: Optional[bytes] = None
    png_base64: Optional[str] = None
    png_path: Optional[Path] = None
    log: str = ""


class DocumentCompiler:
    """
    Hovedklasse for dokumentkompilering.
    
    Eksempel:
        compiler = DocumentCompiler()
        result = await compiler.compile_typst(typst_code)
        if result.success:
            with open("output.pdf", "wb") as f:
                f.write(result.pdf_bytes)
    """
    
    def __init__(
        self,
        work_dir: Optional[Path] = None,
        typst_path: str = "typst",
        pdflatex_path: str = "pdflatex",
        keep_temp_files: bool = False
    ):
        """
        Args:
            work_dir: Arbeidsmappe for midlertidige filer
            typst_path: Sti til typst-binæren
            pdflatex_path: Sti til pdflatex
            keep_temp_files: Om midlertidige filer skal beholdes (for debugging)
        """
        self.work_dir = work_dir or Path(tempfile.gettempdir()) / "matultimate"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.typst_path = typst_path
        self.pdflatex_path = pdflatex_path
        self.keep_temp_files = keep_temp_files
        
        self.sanitizer = CodeSanitizer()
    
    def _create_session_dir(self) -> Path:
        """Opprett en unik mappe for denne kompileringen."""
        session_id = str(uuid.uuid4())[:8]
        session_dir = self.work_dir / f"compile_{session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def _cleanup_session(self, session_dir: Path):
        """Rydd opp midlertidige filer."""
        if not self.keep_temp_files and session_dir.exists():
            shutil.rmtree(session_dir, ignore_errors=True)
    
    async def compile_typst(
        self,
        code: str,
        sanitize: bool = True,
        timeout: int = 30
    ) -> CompilationResult:
        """
        Kompiler Typst-kode til PDF.
        
        Args:
            code: Typst-kildekode
            sanitize: Om koden skal renses først
            timeout: Timeout i sekunder
            
        Returns:
            CompilationResult med PDF-bytes hvis vellykket
        """
        import time
        start_time = time.time()
        
        session_dir = self._create_session_dir()
        warnings = []
        
        try:
            # Sanitize hvis ønsket
            if sanitize:
                sanitize_result = self.sanitizer.sanitize(code, 'typst')
                code = sanitize_result.cleaned_code
                warnings.extend(sanitize_result.warnings)
            
            # Skriv kildekoden
            source_file = session_dir / "document.typ"
            source_file.write_text(code, encoding='utf-8')
            
            output_file = session_dir / "document.pdf"
            
            # Kompiler med Typst
            process = await asyncio.create_subprocess_exec(
                self.typst_path, "compile", str(source_file), str(output_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise CompilationError(
                    f"Typst-kompilering tok mer enn {timeout} sekunder",
                    source_code=code
                )
            
            log = stdout.decode() + stderr.decode()
            
            if process.returncode != 0:
                raise CompilationError(
                    f"Typst-kompilering feilet (kode {process.returncode})",
                    log=log,
                    source_code=code
                )
            
            # Les PDF
            if not output_file.exists():
                raise CompilationError(
                    "PDF ble ikke opprettet",
                    log=log,
                    source_code=code
                )
            
            pdf_bytes = output_file.read_bytes()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            compilation_time = int((time.time() - start_time) * 1000)
            
            return CompilationResult(
                success=True,
                pdf_bytes=pdf_bytes,
                pdf_base64=pdf_base64,
                log=log,
                warnings=warnings,
                compilation_time_ms=compilation_time,
                source_code=code
            )
            
        except CompilationError:
            raise
        except Exception as e:
            raise CompilationError(f"Uventet feil: {e}", source_code=code)
        finally:
            self._cleanup_session(session_dir)
    
    async def compile_latex(
        self,
        code: str,
        sanitize: bool = True,
        timeout: int = 60,
        runs: int = 2
    ) -> CompilationResult:
        """
        Kompiler LaTeX-kode til PDF.
        
        Args:
            code: LaTeX-kildekode
            sanitize: Om koden skal renses først
            timeout: Timeout i sekunder per kjøring
            runs: Antall kompileringskjøringer (for referanser etc.)
        """
        import time
        start_time = time.time()
        
        session_dir = self._create_session_dir()
        warnings = []
        
        try:
            if sanitize:
                sanitize_result = self.sanitizer.sanitize(code, 'latex')
                code = sanitize_result.cleaned_code
                warnings.extend(sanitize_result.warnings)
            
            source_file = session_dir / "document.tex"
            source_file.write_text(code, encoding='utf-8')
            
            all_logs = []
            
            # Kjør pdflatex flere ganger
            for run in range(runs):
                process = await asyncio.create_subprocess_exec(
                    self.pdflatex_path,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    str(source_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session_dir
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    raise CompilationError(
                        f"LaTeX-kompilering (kjøring {run+1}) tok mer enn {timeout} sekunder",
                        source_code=code
                    )
                
                log = stdout.decode(errors='replace') + stderr.decode(errors='replace')
                all_logs.append(f"=== Kjøring {run+1} ===\n{log}")
                
                # Sjekk for fatale feil
                if process.returncode != 0 and run == 0:
                    raise CompilationError(
                        f"LaTeX-kompilering feilet (kode {process.returncode})",
                        log='\n'.join(all_logs),
                        source_code=code
                    )
            
            output_file = session_dir / "document.pdf"
            
            if not output_file.exists():
                raise CompilationError(
                    "PDF ble ikke opprettet",
                    log='\n'.join(all_logs),
                    source_code=code
                )
            
            pdf_bytes = output_file.read_bytes()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            compilation_time = int((time.time() - start_time) * 1000)
            
            return CompilationResult(
                success=True,
                pdf_bytes=pdf_bytes,
                pdf_base64=pdf_base64,
                log='\n'.join(all_logs),
                warnings=warnings,
                compilation_time_ms=compilation_time,
                source_code=code
            )
            
        except CompilationError:
            raise
        except Exception as e:
            raise CompilationError(f"Uventet feil: {e}", source_code=code)
        finally:
            self._cleanup_session(session_dir)
    
    async def compile_latex_figure_to_png(
        self,
        tikz_code: str,
        dpi: int = 300,
        timeout: int = 30
    ) -> FigureResult:
        """
        Kompiler TikZ/pgfplots-figur til PNG.
        
        Brukes for å inkludere LaTeX-figurer i Typst-dokumenter.
        
        Args:
            tikz_code: TikZ eller pgfplots-kode (uten document-wrapper)
            dpi: Oppløsning
            timeout: Timeout i sekunder
        """
        session_dir = self._create_session_dir()
        
        try:
            # Wrap i standalone document
            full_latex = self._wrap_tikz_standalone(tikz_code)
            
            source_file = session_dir / "figure.tex"
            source_file.write_text(full_latex, encoding='utf-8')
            
            # Kompiler til PDF
            process = await asyncio.create_subprocess_exec(
                self.pdflatex_path,
                "-interaction=nonstopmode",
                str(source_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return FigureResult(
                    success=False,
                    log=f"Figur-kompilering tok mer enn {timeout} sekunder"
                )
            
            pdf_file = session_dir / "figure.pdf"
            
            if not pdf_file.exists():
                return FigureResult(
                    success=False,
                    log=stdout.decode(errors='replace') + stderr.decode(errors='replace')
                )
            
            # Konverter PDF til PNG
            png_file = session_dir / "figure.png"
            
            # Prøv pdftoppm først (ImageMagick kan være restriktivt)
            convert_process = await asyncio.create_subprocess_exec(
                "pdftoppm",
                "-png",
                "-r", str(dpi),
                "-singlefile",
                str(pdf_file),
                str(png_file.with_suffix('')),  # pdftoppm legger til .png selv
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await convert_process.communicate()
            
            # pdftoppm lager filnavn-1.png eller filnavn.png
            possible_names = [
                session_dir / "figure.png",
                session_dir / "figure-1.png",
            ]
            
            actual_png = None
            for name in possible_names:
                if name.exists():
                    actual_png = name
                    break
            
            if actual_png is None:
                # Fallback til ImageMagick convert
                convert_process = await asyncio.create_subprocess_exec(
                    "convert",
                    "-density", str(dpi),
                    str(pdf_file),
                    "-quality", "100",
                    str(png_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await convert_process.communicate()
                actual_png = png_file if png_file.exists() else None
            
            if actual_png is None or not actual_png.exists():
                return FigureResult(
                    success=False,
                    log="Kunne ikke konvertere PDF til PNG"
                )
            
            png_bytes = actual_png.read_bytes()
            png_base64 = base64.b64encode(png_bytes).decode('utf-8')
            
            return FigureResult(
                success=True,
                png_bytes=png_bytes,
                png_base64=png_base64,
                png_path=actual_png,
                log=""
            )
            
        except Exception as e:
            return FigureResult(
                success=False,
                log=f"Feil: {e}"
            )
        finally:
            self._cleanup_session(session_dir)
    
    def _wrap_tikz_standalone(self, tikz_code: str) -> str:
        """Wrap TikZ-kode i et standalone LaTeX-dokument."""
        return f"""\\documentclass[tikz,border=5pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}

\\begin{{document}}
{tikz_code}
\\end{{document}}
"""
    
    async def compile_hybrid(
        self,
        typst_code: str,
        figures: list[dict],
        sanitize: bool = True,
        timeout: int = 60
    ) -> CompilationResult:
        """
        Kompiler hybrid-dokument: Typst med LaTeX-figurer.
        
        Args:
            typst_code: Typst-kildekode med #image("figurer/fig_N.png") plassholdere
            figures: Liste med {"id": "fig_0", "latex": "TikZ-kode"}
            sanitize: Om koden skal renses
            timeout: Total timeout
            
        Returns:
            CompilationResult med ferdig PDF
        """
        import time
        start_time = time.time()
        
        session_dir = self._create_session_dir()
        figures_dir = session_dir / "figurer"
        figures_dir.mkdir()
        
        warnings = []
        
        try:
            # 1. Kompiler alle figurer til PNG
            for i, fig in enumerate(figures):
                fig_id = fig.get('id', f'fig_{i}')
                latex_code = fig.get('latex', '')
                
                if not latex_code:
                    warnings.append(f"Figur {fig_id} har tom LaTeX-kode")
                    continue
                
                result = await self.compile_latex_figure_to_png(latex_code)
                
                if not result.success:
                    warnings.append(f"Figur {fig_id} feilet: {result.log}")
                    continue
                
                # Lagre PNG
                png_path = figures_dir / f"{fig_id}.png"
                png_path.write_bytes(result.png_bytes)
            
            # 2. Oppdater Typst-kode med korrekte stier
            processed_typst = typst_code.replace(
                '#image("figurer/',
                f'#image("{figures_dir}/'
            )
            
            # Sanitize hvis ønsket
            if sanitize:
                sanitize_result = self.sanitizer.sanitize(processed_typst, 'typst')
                processed_typst = sanitize_result.cleaned_code
                warnings.extend(sanitize_result.warnings)
            
            # 3. Kompiler Typst
            source_file = session_dir / "document.typ"
            source_file.write_text(processed_typst, encoding='utf-8')
            
            output_file = session_dir / "document.pdf"
            
            process = await asyncio.create_subprocess_exec(
                self.typst_path, "compile", str(source_file), str(output_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise CompilationError(
                    f"Hybrid-kompilering tok mer enn {timeout} sekunder",
                    source_code=typst_code
                )
            
            log = stdout.decode() + stderr.decode()
            
            if process.returncode != 0:
                raise CompilationError(
                    f"Typst-kompilering feilet (kode {process.returncode})",
                    log=log,
                    source_code=processed_typst
                )
            
            if not output_file.exists():
                raise CompilationError(
                    "PDF ble ikke opprettet",
                    log=log,
                    source_code=processed_typst
                )
            
            pdf_bytes = output_file.read_bytes()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            compilation_time = int((time.time() - start_time) * 1000)
            
            return CompilationResult(
                success=True,
                pdf_bytes=pdf_bytes,
                pdf_base64=pdf_base64,
                log=log,
                warnings=warnings,
                compilation_time_ms=compilation_time,
                source_code=processed_typst
            )
            
        except CompilationError:
            raise
        except Exception as e:
            raise CompilationError(f"Uventet feil: {e}", source_code=typst_code)
        finally:
            self._cleanup_session(session_dir)
    
    async def compile(
        self,
        code: str,
        format: DocumentFormat = DocumentFormat.TYPST,
        figures: Optional[list[dict]] = None,
        **kwargs
    ) -> CompilationResult:
        """
        Generisk kompileringsmetode - velger riktig backend.
        
        Args:
            code: Kildekode
            format: DocumentFormat (TYPST, LATEX, HYBRID)
            figures: For HYBRID - liste med LaTeX-figurer
        """
        if format == DocumentFormat.TYPST:
            return await self.compile_typst(code, **kwargs)
        elif format == DocumentFormat.LATEX:
            return await self.compile_latex(code, **kwargs)
        elif format == DocumentFormat.HYBRID:
            return await self.compile_hybrid(code, figures or [], **kwargs)
        else:
            raise ValueError(f"Ukjent format: {format}")
    
    def check_dependencies(self) -> dict:
        """Sjekk at alle nødvendige verktøy er installert."""
        results = {}
        
        # Sjekk Typst
        try:
            result = subprocess.run(
                [self.typst_path, "--version"],
                capture_output=True,
                timeout=5
            )
            results['typst'] = {
                'installed': result.returncode == 0,
                'version': result.stdout.decode().strip() if result.returncode == 0 else None
            }
        except Exception as e:
            results['typst'] = {'installed': False, 'error': str(e)}
        
        # Sjekk pdflatex
        try:
            result = subprocess.run(
                [self.pdflatex_path, "--version"],
                capture_output=True,
                timeout=5
            )
            results['pdflatex'] = {
                'installed': result.returncode == 0,
                'version': result.stdout.decode().split('\n')[0] if result.returncode == 0 else None
            }
        except Exception as e:
            results['pdflatex'] = {'installed': False, 'error': str(e)}
        
        # Sjekk pdftoppm
        try:
            result = subprocess.run(
                ["pdftoppm", "-v"],
                capture_output=True,
                timeout=5
            )
            results['pdftoppm'] = {
                'installed': True,
                'version': result.stderr.decode().strip()
            }
        except Exception as e:
            results['pdftoppm'] = {'installed': False, 'error': str(e)}
        
        return results


# =============================================================================
# TYPST TEMPLATES
# =============================================================================

class TypstTemplates:
    """Ferdiglagde Typst-maler for matematikkdokumenter."""
    
    @staticmethod
    def worksheet_header(
        title: str,
        grade: str,
        topic: str
    ) -> str:
        """Standard header for arbeidsark."""
        return f"""#set text(lang: "nb", font: "Linux Libertine", size: 11pt)
#set page(paper: "a4", margin: 2.5cm)
#set heading(numbering: "1.1.")

// Definisjon av stiler for bokser
#let box_style(title, body, color) = {{
  rect(
    width: 100%,
    fill: color.lighten(95%),
    stroke: 0.5pt + color,
    inset: 12pt,
    radius: 4pt,
    stack(
      spacing: 8pt,
      text(weight: "bold", size: 1.1em, fill: color.darken(30%))[#title],
      body
    )
  )
}}

#let oppgave(body) = box_style("Oppgave", body, blue)
#let eksempel(title: "Eksempel", body) = box_style(title, body, gray)
#let definisjon(body) = box_style("Definisjon", body, green)
#let teorem(title: "Teorem", body) = box_style(title, body, red)
#let hint(body) = box_style("Hint", body, orange)

// Tittel
#align(center)[
  #text(size: 1.5em, weight: "bold")[{title}]
  
  #text(size: 1.1em, style: "italic")[{grade} · {topic}]
]

#v(1em)
"""
    
    @staticmethod
    def answer_key_header(
        title: str,
        grade: str,
        topic: str
    ) -> str:
        """Header for fasit-dokument."""
        return f"""#set text(lang: "nb", font: "Linux Libertine", size: 10pt)
#set page(paper: "a4", margin: 2cm)

#align(center)[
  #text(size: 1.3em, weight: "bold")[Fasit: {title}]
  
  #text(size: 1em, style: "italic", fill: gray)[{grade} · {topic}]
  
  #v(0.5em)
  #text(size: 0.9em, fill: red)[Kun for lærerbruk]
]

#line(length: 100%, stroke: 0.5pt)
#v(1em)
"""
    
    @staticmethod
    def level_divider(level: int, description: str) -> str:
        """Skillelinje mellom differensieringsnivåer."""
        level_names = {
            1: "Nivå 1 – Grunnleggende",
            2: "Nivå 2 – Middels",
            3: "Nivå 3 – Utfordring"
        }
        level_colors = {
            1: "green",
            2: "orange",
            3: "red"
        }
        
        name = level_names.get(level, f"Nivå {level}")
        color = level_colors.get(level, "gray")
        
        return f"""
#pagebreak()

#rect(
  width: 100%,
  fill: {color}.lighten(90%),
  stroke: 2pt + {color},
  inset: 15pt,
  radius: 8pt
)[
  #align(center)[
    #text(size: 1.4em, weight: "bold", fill: {color}.darken(30%))[{name}]
    
    #v(0.3em)
    
    #text(style: "italic")[{description}]
  ]
]

#v(1em)
"""


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        compiler = DocumentCompiler(keep_temp_files=True)
        
        print("=== MaTultimate Compiler Test ===\n")
        
        # Sjekk avhengigheter
        print("1. Sjekker avhengigheter:")
        deps = compiler.check_dependencies()
        for tool, info in deps.items():
            status = "✓" if info.get('installed') else "✗"
            version = info.get('version', info.get('error', 'ukjent'))
            print(f"   {status} {tool}: {version}")
        
        # Test Typst-kompilering
        print("\n2. Tester Typst-kompilering:")
        typst_code = """#set text(lang: "nb")

= Test

Dette er en test av $f(x) = x^2$.

$ integral_0^1 x^2 dif x = 1/3 $
"""
        
        try:
            result = await compiler.compile_typst(typst_code)
            print(f"   ✓ Kompilering vellykket ({result.compilation_time_ms}ms)")
            print(f"   PDF-størrelse: {len(result.pdf_bytes)} bytes")
        except CompilationError as e:
            print(f"   ✗ Feilet: {e}")
            print(f"   Log: {e.log[:200]}...")
        
        print("\n=== Ferdig ===")
    
    asyncio.run(main())
