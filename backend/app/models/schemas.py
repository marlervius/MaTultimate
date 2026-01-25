from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DocumentFormat(str, Enum):
    TYPST = "typst"
    LATEX = "latex"
    HYBRID = "hybrid"

class DifferentiationLevel(str, Enum):
    SINGLE = "single"
    THREE_LEVELS = "three_levels"

class MaterialRequest(BaseModel):
    klassetrinn: str = Field(..., example="R1")
    emne: str = Field(..., example="Derivasjon")
    kompetansemaal: str = Field(..., example="derivere potens-, eksponential- og logaritmefunksjoner")
    differentiation: DifferentiationLevel = DifferentiationLevel.THREE_LEVELS
    include_answer_key: bool = True
    document_format: DocumentFormat = DocumentFormat.TYPST

class GenerationResponse(BaseModel):
    success: bool
    worksheet_pdf: Optional[str] = None  # Base64
    answer_key_pdf: Optional[str] = None # Base64
    source_code: Optional[str] = None
    metadata: Dict[str, Any] = {}
    error_message: Optional[str] = None
