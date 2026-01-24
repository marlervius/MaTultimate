import os
from crewai import Agent, LLM
from app.prompts.figur import FIGUR_AGENT_PROMPT

class FigurAgent:
    def __init__(self, llm: LLM):
        self.llm = llm

    def get_agent(self) -> Agent:
        return Agent(
            role="Teknisk Illustratør",
            goal="Generer nøyaktig TikZ/LaTeX-kode for matematiske figurer.",
            backstory=FIGUR_AGENT_PROMPT,
            llm=self.llm,
            allow_delegation=False
        )
