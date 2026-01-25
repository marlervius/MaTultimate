from crewai import Agent, LLM
from app.prompts.redaktor import REDAKTOR_PROMPT

class RedaktorAgent:
    """
    Agent ansvarlig for sluttkontroll og kvalitetssikring av dokumentet.
    """
    def __init__(self, llm: LLM):
        self.llm = llm

    def get_agent(self) -> Agent:
        return Agent(
            role="Sjefredaktør og Kvalitetskontrollør",
            goal="Sikre at dokumentet er teknisk feilfritt, matematisk korrekt og pedagogisk optimalt.",
            backstory=REDAKTOR_PROMPT,
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )
