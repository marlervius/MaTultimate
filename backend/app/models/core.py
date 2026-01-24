import os
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class MaterialConfig(BaseModel):
    title: str
    grade: str
    topic: str
    material_type: str # 'arbeidsark', 'kapittel', 'prøve', 'lekseark'
    include_theory: bool = True
    include_examples: bool = True
    include_exercises: bool = True
    include_solutions: bool = True
    include_graphs: bool = True
    num_exercises: int = 10
    difficulty: str = "Middels"
    differentiation: Literal["single", "three_levels"] = "single"
    language: str = "no"
    output_format: str = "latex" # 'latex' or 'typst'
    competency_goals: List[str] = []
    custom_instructions: Optional[str] = None

class MathBlock(BaseModel):
    type: str # 'definition', 'theorem', 'example', 'exercise', 'remark', 'proof'
    title: Optional[str] = None
    content: str
    solution: Optional[str] = None
    difficulty: Optional[str] = None
    metadata: Dict[str, Any] = {}
