"""
MaTultimate Agents
==================
AI-agenter for matematikkgenerering.
"""

from .vgs_agent import VGSAgent, VGSKurs, Emne, OppgaveConfig, Oppgavesett
from .figur_agent import FigurAgent, FigurConfig, FigurType

__all__ = [
    'VGSAgent',
    'VGSKurs',
    'Emne',
    'OppgaveConfig',
    'Oppgavesett',
    'FigurAgent',
    'FigurConfig',
    'FigurType',
]
