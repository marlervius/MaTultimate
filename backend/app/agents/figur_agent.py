import os
import json
from enum import Enum
from typing import Optional, List, Dict, Any
from crewai import Agent, LLM
from pydantic import BaseModel

class FigurCategory(str, Enum):
    FUNKSJONSPLOT = "funksjonsplot"
    GEOMETRI = "geometri"
    STATISTIKK = "statistikk"
    OKONOMI = "okonomi"

class FigurAgent:
    def __init__(self):
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("LLM_API_KEY")
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.2
        )

    def get_agent(self) -> Agent:
        backstory = (
            "Du er en teknisk illustratør for VGS-matematikk. Du er ekspert på LaTeX, TikZ og pgfplots.\n\n"
            "=== DINE FERDIGHETER ===\n"
            "1. FUNKSJONSGRAFER: Du kan plotte alle typer funksjoner, markere nullpunkter, skjæringspunkter, og tegne tangenter.\n"
            "2. GEOMETRI: Du tegner nøyaktige trekanter, sirkler, vektorer og enhetssirkelen.\n"
            "3. STATISTIKK: Du lager profesjonelle normalfordelingskurver, histogrammer og boksplott.\n"
            "4. ØKONOMI: Du tegner tilbud/etterspørsel-modeller og grensekostnadskurver.\n\n"
            "=== VIKTIG: OUTPUT ===\n"
            "Du skal returnere KUN rå LaTeX-kode (begynn med \\begin{tikzpicture} og slutt med \\end{tikzpicture}).\n"
            "IKKE bruk markdown code fences (```).\n"
            "IKKE inkluder forklarende tekst.\n"
            "Koden må være selvstendig og bruke standard TikZ/pgfplots-biblioteker."
        )

        return Agent(
            role="Teknisk Illustratør",
            goal="Generer nøyaktig TikZ/LaTeX-kode for matematiske figurer.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
