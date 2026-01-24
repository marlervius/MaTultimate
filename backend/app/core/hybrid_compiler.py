import os
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

class Figure(BaseModel):
    latex_code: str
    description: str

class HybridCompiler:
    """
    Håndterer den komplekse kompileringen for hybride dokumenter (Typst + LaTeX figurer).
    """
    
    async def compile_hybrid(self, 
                            main_document: str,
                            figures: List[Figure]) -> bytes:
        
        # Bruk en unik mappe for denne genereringen
        unique_id = uuid.uuid4()
        work_dir = Path(f"tmp/matultimate_{unique_id}")
        work_dir.mkdir(parents=True, exist_ok=True)
        figures_dir = work_dir / "figures"
        figures_dir.mkdir(exist_ok=True)
        
        # 1. Kompiler hver LaTeX-figur til PNG
        figure_paths = []
        for i, fig in enumerate(figures):
            png_path = await self._compile_figure_to_png(
                fig.latex_code, 
                figures_dir / f"fig_{i}.png"
            )
            figure_paths.append(png_path)
        
        # 2. Erstatt plassholdere i Typst-dokumentet
        # Antar at Matematiker-agenten bruker [FIGUR: fig_0.png] osv.
        final_typst = main_document
        for i, path in enumerate(figure_paths):
            placeholder = f"figures/fig_{i}.png"
            # Typst image() funksjonen trenger relativ sti
            final_typst = final_typst.replace(f"fig_{i}.png", placeholder)
        
        # 3. Kompiler Typst til PDF
        # (Dette krever at vi har en _compile_typst metode)
        return await self._compile_typst(final_typst, work_dir)
    
    async def _compile_figure_to_png(self, latex: str, output_path: Path) -> Path:
        """Kompilerer en frittstående LaTeX-figur til PNG."""
        
        standalone_doc = f"""
\\documentclass[tikz,border=5pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepackage{{amsmath}}
\\begin{{document}}
{latex}
\\end{{document}}
"""
        tex_path = output_path.with_suffix('.tex')
        tex_path.write_text(standalone_doc, encoding="utf-8")
        
        # Kompiler til PDF
        process = await asyncio.create_subprocess_exec(
            'pdflatex', '-interaction=nonstopmode', str(tex_path.name),
            cwd=str(tex_path.parent),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.wait()
        
        # Konverter PDF til PNG ved hjelp av pdftoppm (del av poppler-utils)
        pdf_path = output_path.with_suffix('.pdf')
        if pdf_path.exists():
            process = await asyncio.create_subprocess_exec(
                'pdftoppm', '-png', '-r', '300', '-singlefile',
                str(pdf_path), str(output_path.with_suffix('')),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
        
        return output_path

    async def _compile_typst(self, content: str, work_dir: Path) -> bytes:
        """Kompilerer Typst-innhold til PDF-bytes."""
        typ_file = work_dir / "main.typ"
        pdf_file = work_dir / "output.pdf"
        typ_file.write_text(content, encoding="utf-8")
        
        process = await asyncio.create_subprocess_exec(
            'typst', 'compile', str(typ_file), str(pdf_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.wait()
        
        if pdf_file.exists():
            return pdf_file.read_bytes()
        return b""
