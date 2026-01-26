from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import Enum
from datetime import datetime


class DifferentiationLevel(str, Enum):
    SINGLE = "single"
    THREE_LEVELS = "three_levels"


class ExportFormat(str, Enum):
    COMBINED_PDF = "combined_pdf"
    SEPARATE_FILES = "separate_files"


class DocumentFormat(str, Enum):
    TYPST = "typst"
    LATEX = "latex"


class MaterialConfig(BaseModel):
    """Konfigurasjon for generering av matematikkmateriell."""
    
    # === Faglig innhold ===
    klassetrinn: str = Field(..., description="Klassetrinn eller kursnavn (f.eks. '10', 'R1', '1T')")
    emne: str = Field(..., min_length=2, max_length=100, examples=["Potenser", "Brøk", "Algebra"])
    kompetansemaal: str = Field(..., min_length=10, description="LK20-kompetansemål")
    
    # === Differensiering ===
    differentiation: DifferentiationLevel = Field(
        default=DifferentiationLevel.SINGLE,
        description="Generer ett nivå eller tre differensierte nivåer"
    )
    
    # === Fasit ===
    include_answer_key: bool = Field(
        default=True,
        description="Generer separat fasit med steg-for-steg løsninger"
    )
    
    # === Eksport ===
    document_format: DocumentFormat = Field(
        default=DocumentFormat.TYPST,
        description="Typst (raskere) eller LaTeX (flere pakker)"
    )
    export_format: ExportFormat = Field(
        default=ExportFormat.COMBINED_PDF,
        description="Én samlet PDF eller separate filer per nivå"
    )
    
    # === Tilpasninger ===
    antall_oppgaver: int = Field(default=8, ge=3, le=20)
    include_hints: bool = Field(default=True, description="Inkluder hint på nivå 1")
    include_visuals: bool = Field(default=False, description="Inkluder illustrasjoner/diagrammer")
    
    # === Metadata ===
    title: Optional[str] = Field(default=None, max_length=100)
    author: Optional[str] = Field(default=None, max_length=50)
    
    @field_validator('klassetrinn')
    @classmethod
    def validate_klassetrinn(cls, v: str) -> str:
        """Valider at klassetrinn er et støttet trinn eller kurs."""
        valid_trinn = [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            "1t", "1p", "2p", "2t", "r1", "r2", "s1", "s2",
            "vg1", "vg2", "vg3"
        ]
        if v.lower() not in valid_trinn:
            raise ValueError(f"Ugyldig klassetrinn: {v}. Må være ett av {valid_trinn}")
        return v # Bevar original casing hvis ønskelig, eller returner v.lower()
    
    @field_validator('emne')
    @classmethod
    def sanitize_emne(cls, v: str) -> str:
        """Fjern potensielt skadelige tegn."""
        forbidden = ['```', '${', '\\input', '\\include']
        for char in forbidden:
            if char in v.lower():
                raise ValueError(f"Ugyldig tegn i emne: {char}")
        return v.strip()
    
    @field_validator('kompetansemaal')
    @classmethod
    def validate_kompetansemaal(cls, v: str) -> str:
        """Enkel validering av kompetansemål."""
        if len(v.split()) < 3:
            raise ValueError("Kompetansemål must be a full sentence")
        return v.strip()
    
    @property
    def grade(self) -> str:
        """Alias for bakoverkompatibilitet med eldre kode."""
        return self.klassetrinn

    @property
    def topic(self) -> str:
        """Alias for bakoverkompatibilitet."""
        return self.emne

    @property
    def competency_goals(self) -> list[str]:
        """Alias for bakoverkompatibilitet (returnerer som liste)."""
        return [self.kompetansemaal]

    @property
    def output_format(self) -> str:
        """Alias for bakoverkompatibilitet."""
        return self.document_format.value

    def get_output_filename(self) -> str:
        """Generer filnavn basert på konfigurasjon."""
        date_str = datetime.now().strftime("%Y%m%d")
        safe_emne = self.emne.lower().replace(" ", "_")[:20]
        return f"{self.klassetrinn}_{safe_emne}_{date_str}"
    
    @property
    def generates_multiple_files(self) -> bool:
        """Sjekk om konfigurasjonen genererer flere filer."""
        return (
            self.export_format == ExportFormat.SEPARATE_FILES and
            self.differentiation == DifferentiationLevel.THREE_LEVELS
        )


class GenerationResponse(BaseModel):
    """Respons fra /generate-endepunktet."""
    
    success: bool
    
    # === Hovedfiler ===
    worksheet_pdf: Optional[str] = Field(None, description="Base64-kodet PDF")
    answer_key_pdf: Optional[str] = Field(None, description="Base64-kodet fasit-PDF")
    
    # === Ved separate filer ===
    level_1_pdf: Optional[str] = None
    level_2_pdf: Optional[str] = None
    level_3_pdf: Optional[str] = None
    
    # === Kildekode ===
    source_code: Optional[str] = Field(None, description="Rå Typst/LaTeX-kode")
    answer_key_source: Optional[str] = None
    
    # === Metadata ===
    metadata: dict = Field(default_factory=dict)
    compilation_time_ms: Optional[int] = None
    
    # === Feilhåndtering ===
    error_message: Optional[str] = None
    raw_ai_output: Optional[str] = Field(
        None, 
        description="Rå AI-output ved kompileringsfeil, for debugging"
    )


class HistoryEntry(BaseModel):
    """For lagring i oppgavebanken."""
    
    id: str
    created_at: datetime
    config: MaterialConfig
    kompetansemaal_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    
    # Statistikk
    download_count: int = 0
    last_downloaded: Optional[datetime] = None
