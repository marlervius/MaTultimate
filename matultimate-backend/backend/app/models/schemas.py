"""
MaTultimate API Schemas
=======================
Pydantic-modeller for request/response validering.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class Klassetrinn(str, Enum):
    """Alle støttede klassetrinn."""
    # VGS
    VG1_T = "1t"
    VG1_P = "1p"
    VG2_P = "2p"
    VG2_R1 = "r1"
    VG2_S1 = "s1"
    VG3_R2 = "r2"
    VG3_S2 = "s2"
    
    # Ungdomsskole (fremtidig)
    # U8 = "8"
    # U9 = "9"
    # U10 = "10"


class Emne(str, Enum):
    """Matematikkemner."""
    ALGEBRA = "algebra"
    FUNKSJONER = "funksjoner"
    DERIVASJON = "derivasjon"
    INTEGRASJON = "integrasjon"
    VEKTORER = "vektorer"
    SANNSYNLIGHET = "sannsynlighet"
    STATISTIKK = "statistikk"
    GEOMETRI = "geometri"
    OKONOMI = "økonomi"
    TALLTEORI = "tallteori"
    LIKNINGER = "likninger"


class DokumentFormat(str, Enum):
    """Output-format."""
    TYPST = "typst"
    LATEX = "latex"
    HYBRID = "hybrid"  # Typst + LaTeX-figurer


class EksportFormat(str, Enum):
    """Eksportmåte for differensierte oppgaver."""
    COMBINED = "combined"  # Alle nivåer i én PDF
    SEPARATE = "separate"  # Tre separate PDF-er


# =============================================================================
# REQUEST MODELS
# =============================================================================

class GenererOppgaverRequest(BaseModel):
    """Forespørsel om å generere oppgaver."""
    
    klassetrinn: Klassetrinn = Field(
        ...,
        description="Klassetrinn/kurs (f.eks. 'r1', '1t')"
    )
    
    emne: Emne = Field(
        ...,
        description="Matematikkemne"
    )
    
    kompetansemaal: Optional[str] = Field(
        None,
        description="Spesifikt LK20-kompetansemål (valgfritt)"
    )
    
    antall_oppgaver: int = Field(
        default=9,
        ge=3,
        le=30,
        description="Antall oppgaver totalt"
    )
    
    differensiering: bool = Field(
        default=True,
        description="Om oppgavene skal differensieres i tre nivåer"
    )
    
    inkluder_fasit: bool = Field(
        default=True,
        description="Om fasit med løsninger skal inkluderes"
    )
    
    inkluder_figurer: bool = Field(
        default=True,
        description="Om figurer (grafer, geometri) skal genereres"
    )
    
    dokument_format: DokumentFormat = Field(
        default=DokumentFormat.TYPST,
        description="Output-format for dokumenter"
    )
    
    eksport_format: EksportFormat = Field(
        default=EksportFormat.COMBINED,
        description="Om nivåene skal være i én eller flere filer"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "klassetrinn": "r1",
                "emne": "derivasjon",
                "antall_oppgaver": 9,
                "differensiering": True,
                "inkluder_fasit": True
            }
        }


class VerifiserMatteRequest(BaseModel):
    """Forespørsel om å verifisere matematisk uttrykk."""
    
    type: Literal["derivasjon", "integral", "likning", "forenkling"] = Field(
        ...,
        description="Type verifisering"
    )
    
    uttrykk: str = Field(
        ...,
        description="Det matematiske uttrykket (Python-syntaks eller LaTeX)"
    )
    
    svar: str = Field(
        ...,
        description="Svaret som skal verifiseres"
    )
    
    variabel: str = Field(
        default="x",
        description="Variabelen det opereres på"
    )
    
    fra_latex: bool = Field(
        default=False,
        description="Om input er i LaTeX-format"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "derivasjon",
                "uttrykk": "x**3 + 2*x",
                "svar": "3*x**2 + 2"
            }
        }


class GenererVarianterRequest(BaseModel):
    """Forespørsel om å generere varianter av en oppgavemal."""
    
    mal: str = Field(
        ...,
        description="Oppgavemal med parametere, f.eks. '{a}*x**{n}'"
    )
    
    antall: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Antall varianter"
    )
    
    vanskelighetsgrad: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Vanskelighetsgrad (0.0 = lett, 1.0 = vanskelig)"
    )
    
    type: Literal["derivasjon", "integral"] = Field(
        default="derivasjon",
        description="Type oppgave"
    )


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class OppgaveResponse(BaseModel):
    """En enkelt oppgave i responsen."""
    nummer: str
    tekst: str
    latex_problem: str
    latex_svar: str
    hint: Optional[str] = None
    figur_trengs: bool = False
    figur_url: Optional[str] = None


class NivaaResponse(BaseModel):
    """Et differensieringsnivå."""
    nivaa: int
    beskrivelse: str
    oppgaver: list[OppgaveResponse]


class FasitEntry(BaseModel):
    """En fasit-oppføring."""
    nummer: str
    svar: str
    steg: Optional[list[dict]] = None


class GenererOppgaverResponse(BaseModel):
    """Respons med genererte oppgaver."""
    
    success: bool
    tittel: str
    klassetrinn: str
    emne: str
    kompetansemaal: str
    
    # Oppgaver per nivå
    nivaa_1: Optional[NivaaResponse] = None
    nivaa_2: Optional[NivaaResponse] = None
    nivaa_3: Optional[NivaaResponse] = None
    
    # Fasit
    fasit: Optional[dict[str, list[FasitEntry]]] = None
    
    # Dokumenter
    dokument_format: str
    typst_kode: Optional[str] = None
    latex_kode: Optional[str] = None
    
    # PDF (base64)
    pdf_base64: Optional[str] = None
    fasit_pdf_base64: Optional[str] = None
    
    # Metadata
    genereringstid_ms: int = 0
    antall_oppgaver: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "tittel": "Arbeidsark: Derivasjon",
                "klassetrinn": "R1",
                "emne": "Derivasjon",
                "antall_oppgaver": 9
            }
        }


class VerifiserMatteResponse(BaseModel):
    """Respons på matematisk verifisering."""
    
    korrekt: bool
    forventet: str
    oppgitt: str
    differanse: Optional[str] = None
    melding: str


class VariantResponse(BaseModel):
    """En generert variant."""
    problem_latex: str
    svar_latex: str
    vanskelighetsgrad: float
    parametre: dict


class GenererVarianterResponse(BaseModel):
    """Respons med genererte varianter."""
    
    success: bool
    mal: str
    varianter: list[VariantResponse]
    antall: int


# =============================================================================
# HEALTH/STATUS
# =============================================================================

class HealthResponse(BaseModel):
    """Helsestatus for API-et."""
    status: str
    versjon: str
    komponenter: dict[str, bool]


class DependencyStatus(BaseModel):
    """Status for en avhengighet."""
    navn: str
    installert: bool
    versjon: Optional[str] = None
    feilmelding: Optional[str] = None
