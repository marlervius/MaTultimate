from pydantic import BaseModel
from typing import List, Literal

class FormatDecision(BaseModel):
    format: Literal["typst", "latex", "hybrid"]
    reason: str

class FormatSelector:
    """
    Intelligent format selection based on content analysis.
    """
    
    TYPST_CAPABLE = [
        "tallinje",
        "enkel_tabell", 
        "rutenett",
        "brøkillustrasjon_enkel",
        "søylediagram_enkelt"
    ]
    
    REQUIRES_LATEX = [
        "funksjonsplot",
        "funksjonsplot_med_tangent",
        "areal_under_kurve",
        "geometrisk_konstruksjon",
        "vinkelrett_projeksjon",
        "enhetssirkel",
        "normalfordeling",
        "vektordiagram",
        "3d_figur",
        "sannsynlighetstre"
    ]
    
    def analyze(self, orchestrator_output: dict) -> FormatDecision:
        figures = orchestrator_output.get("figurbehov", [])
        
        needs_latex = any(
            fig["type"] == "kompleks" or 
            fig.get("beskrivelse", "").lower() in self.REQUIRES_LATEX
            for fig in figures
        )
        
        all_simple = all(
            fig["type"] in ["ingen", "enkel"]
            for fig in figures
        )
        
        if not figures or all_simple:
            return FormatDecision(
                format="typst",
                reason="Ingen komplekse figurer, Typst gir raskest kompilering"
            )
        elif needs_latex and len([f for f in figures if f["type"] == "kompleks"]) > 3:
            return FormatDecision(
                format="latex",
                reason="Mange komplekse figurer, LaTeX gjennomgående er mest effektivt"
            )
        else:
            return FormatDecision(
                format="hybrid",
                reason=f"Hovedsakelig tekst med {len([f for f in figures if f['type'] == 'kompleks'])} komplekse figurer"
            )
