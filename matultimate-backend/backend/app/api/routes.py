"""
MaTultimate API Routes
======================
FastAPI-endepunkter for oppgavegenerering.
"""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.schemas import (
    GenererOppgaverRequest,
    GenererOppgaverResponse,
    VerifiserMatteRequest,
    VerifiserMatteResponse,
    GenererVarianterRequest,
    GenererVarianterResponse,
    VariantResponse,
    NivaaResponse,
    OppgaveResponse,
    FasitEntry,
    HealthResponse,
    Klassetrinn,
    Emne as EmneSchema,
)
from ..core.math_engine import MathEngine
from ..agents.vgs_agent import VGSAgent, VGSKurs, Emne, OppgaveConfig

# Router
router = APIRouter(prefix="/api/v1", tags=["MaTultimate"])

# Singleton-instanser
_math_engine: Optional[MathEngine] = None
_vgs_agent: Optional[VGSAgent] = None


def get_math_engine() -> MathEngine:
    """Lazy-load MathEngine."""
    global _math_engine
    if _math_engine is None:
        _math_engine = MathEngine()
    return _math_engine


def get_vgs_agent() -> VGSAgent:
    """Lazy-load VGSAgent."""
    global _vgs_agent
    if _vgs_agent is None:
        _vgs_agent = VGSAgent()
    return _vgs_agent


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Sjekk helsestatus for API-et."""
    return HealthResponse(
        status="healthy",
        versjon="0.1.0",
        komponenter={
            "math_engine": True,
            "vgs_agent": True,
            "typst": False,  # Sjekkes ved kompilering
            "latex": False,  # Sjekkes ved kompilering
        }
    )


# =============================================================================
# OPPGAVEGENERERING
# =============================================================================

@router.post("/generer", response_model=GenererOppgaverResponse)
async def generer_oppgaver(request: GenererOppgaverRequest):
    """
    Generer et komplett oppgavesett.
    
    Støtter:
    - VGS-kurs: 1T, 1P, 2P, R1, R2, S1, S2
    - Emner: derivasjon, integrasjon, funksjoner, m.fl.
    - Differensiering i tre nivåer
    - Fasit med steg-for-steg løsninger
    """
    start_time = time.time()
    
    try:
        agent = get_vgs_agent()
        
        # Map request til agent-config
        kurs_mapping = {
            Klassetrinn.VG1_T: VGSKurs.T1,
            Klassetrinn.VG1_P: VGSKurs.P1,
            Klassetrinn.VG2_P: VGSKurs.P2,
            Klassetrinn.VG2_R1: VGSKurs.R1,
            Klassetrinn.VG2_S1: VGSKurs.S1,
            Klassetrinn.VG3_R2: VGSKurs.R2,
            Klassetrinn.VG3_S2: VGSKurs.S2,
        }
        
        emne_mapping = {
            EmneSchema.DERIVASJON: Emne.DERIVASJON,
            EmneSchema.INTEGRASJON: Emne.INTEGRASJON,
            EmneSchema.FUNKSJONER: Emne.FUNKSJONER,
            EmneSchema.ALGEBRA: Emne.ALGEBRA,
            EmneSchema.VEKTORER: Emne.VEKTORER,
            EmneSchema.SANNSYNLIGHET: Emne.SANNSYNLIGHET,
            EmneSchema.STATISTIKK: Emne.STATISTIKK,
            EmneSchema.GEOMETRI: Emne.GEOMETRI,
            EmneSchema.OKONOMI: Emne.OKONOMI,
        }
        
        config = OppgaveConfig(
            kurs=kurs_mapping.get(request.klassetrinn, VGSKurs.R1),
            emne=emne_mapping.get(request.emne, Emne.DERIVASJON),
            kompetansemaal=request.kompetansemaal,
            antall_oppgaver=request.antall_oppgaver,
            differensiering=request.differensiering,
            inkluder_fasit=request.inkluder_fasit,
            inkluder_figurer=request.inkluder_figurer,
        )
        
        # Generer oppgavesett
        oppgavesett = agent.generer_oppgavesett(config)
        
        # Konverter til response-format
        def oppgave_til_response(o) -> OppgaveResponse:
            return OppgaveResponse(
                nummer=o.nummer,
                tekst=o.tekst,
                latex_problem=o.latex_problem,
                latex_svar=o.latex_svar,
                hint=o.hint,
                figur_trengs=o.figur_trengs,
            )
        
        nivaa_beskrivelser = {
            1: "Grunnleggende oppgaver som hjelper deg å forstå det grunnleggende.",
            2: "Standardoppgaver som tester din forståelse.",
            3: "Utfordrende oppgaver som krever kombinasjon av flere teknikker.",
        }
        
        # Bygg response
        response = GenererOppgaverResponse(
            success=True,
            tittel=oppgavesett.tittel,
            klassetrinn=oppgavesett.kurs,
            emne=oppgavesett.emne,
            kompetansemaal=oppgavesett.kompetansemaal,
            dokument_format=request.dokument_format.value,
            genereringstid_ms=int((time.time() - start_time) * 1000),
            antall_oppgaver=(
                len(oppgavesett.nivaa_1) + 
                len(oppgavesett.nivaa_2) + 
                len(oppgavesett.nivaa_3)
            ),
        )
        
        # Legg til nivåer
        if oppgavesett.nivaa_1:
            response.nivaa_1 = NivaaResponse(
                nivaa=1,
                beskrivelse=nivaa_beskrivelser[1],
                oppgaver=[oppgave_til_response(o) for o in oppgavesett.nivaa_1]
            )
        
        if oppgavesett.nivaa_2:
            response.nivaa_2 = NivaaResponse(
                nivaa=2,
                beskrivelse=nivaa_beskrivelser[2],
                oppgaver=[oppgave_til_response(o) for o in oppgavesett.nivaa_2]
            )
        
        if oppgavesett.nivaa_3:
            response.nivaa_3 = NivaaResponse(
                nivaa=3,
                beskrivelse=nivaa_beskrivelser[3],
                oppgaver=[oppgave_til_response(o) for o in oppgavesett.nivaa_3]
            )
        
        # Legg til fasit
        if oppgavesett.fasit and request.inkluder_fasit:
            response.fasit = {}
            for nivaa_key in ['nivaa_1', 'nivaa_2', 'nivaa_3']:
                if nivaa_key in oppgavesett.fasit:
                    response.fasit[nivaa_key] = [
                        FasitEntry(
                            nummer=entry['nummer'],
                            svar=entry['svar'],
                            steg=entry.get('steg')
                        )
                        for entry in oppgavesett.fasit[nivaa_key]
                    ]
        
        # Generer Typst-kode
        if request.dokument_format.value in ['typst', 'hybrid']:
            response.typst_kode = agent.til_typst(oppgavesett)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feil ved generering: {str(e)}"
        )


# =============================================================================
# MATEMATISK VERIFISERING
# =============================================================================

@router.post("/verifiser", response_model=VerifiserMatteResponse)
async def verifiser_matte(request: VerifiserMatteRequest):
    """
    Verifiser et matematisk uttrykk.
    
    Støtter:
    - Derivasjon: Sjekker at f'(x) er korrekt
    - Integral: Sjekker at ∫f(x)dx er korrekt
    - Likning: Sjekker at løsningen er riktig
    - Forenkling: Sjekker algebraisk likhet
    """
    try:
        engine = get_math_engine()
        
        if request.type == "derivasjon":
            result = engine.verify_derivative(
                request.uttrykk,
                request.svar,
                request.variabel,
                request.fra_latex
            )
        elif request.type == "integral":
            result = engine.verify_integral(
                request.uttrykk,
                request.svar,
                request.variabel,
                from_latex=request.fra_latex
            )
        elif request.type == "likning":
            result = engine.verify_equation_solution(
                request.uttrykk,
                request.svar,
                request.variabel,
                request.fra_latex
            )
        elif request.type == "forenkling":
            result = engine.verify_simplification(
                request.uttrykk,
                request.svar,
                request.fra_latex
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Ukjent verifiseringstype: {request.type}"
            )
        
        return VerifiserMatteResponse(
            korrekt=result.is_correct,
            forventet=result.expected,
            oppgitt=result.got,
            differanse=result.simplified_difference,
            melding=result.message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feil ved verifisering: {str(e)}"
        )


# =============================================================================
# VARIANT-GENERERING
# =============================================================================

@router.post("/varianter", response_model=GenererVarianterResponse)
async def generer_varianter(request: GenererVarianterRequest):
    """
    Generer varianter av en oppgavemal.
    
    Nyttig for:
    - Lage flere øvingsoppgaver av samme type
    - Generere prøveoppgaver uten gjentakelse
    - Tilpasse vanskelighetsgrad
    """
    try:
        engine = get_math_engine()
        
        if request.type == "derivasjon":
            variants = engine.generate_derivative_variants(
                request.mal,
                request.antall,
                request.vanskelighetsgrad
            )
        elif request.type == "integral":
            variants = engine.generate_integral_variants(
                request.mal,
                request.antall,
                request.vanskelighetsgrad
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Ukjent oppgavetype: {request.type}"
            )
        
        return GenererVarianterResponse(
            success=True,
            mal=request.mal,
            varianter=[
                VariantResponse(
                    problem_latex=v.problem_latex,
                    svar_latex=v.answer_latex,
                    vanskelighetsgrad=v.difficulty,
                    parametre=v.parameters
                )
                for v in variants
            ],
            antall=len(variants)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feil ved variant-generering: {str(e)}"
        )


# =============================================================================
# HJELPEMETODER
# =============================================================================

@router.get("/emner")
async def list_emner():
    """List alle støttede emner."""
    return {
        "emner": [
            {"id": "derivasjon", "navn": "Derivasjon", "kurs": ["r1", "r2", "s1", "s2"]},
            {"id": "integrasjon", "navn": "Integrasjon", "kurs": ["r1", "r2", "s1", "s2"]},
            {"id": "funksjoner", "navn": "Funksjoner", "kurs": ["1t", "1p", "r1", "r2"]},
            {"id": "algebra", "navn": "Algebra", "kurs": ["1t", "1p", "2p"]},
            {"id": "vektorer", "navn": "Vektorer", "kurs": ["r1", "r2"]},
            {"id": "sannsynlighet", "navn": "Sannsynlighetsregning", "kurs": ["s1", "s2"]},
            {"id": "statistikk", "navn": "Statistikk", "kurs": ["s1", "s2", "2p"]},
            {"id": "geometri", "navn": "Geometri", "kurs": ["1t", "r1"]},
            {"id": "økonomi", "navn": "Økonomi", "kurs": ["s1", "s2", "2p"]},
        ]
    }


@router.get("/klassetrinn")
async def list_klassetrinn():
    """List alle støttede klassetrinn."""
    return {
        "klassetrinn": [
            {"id": "1t", "navn": "1T (Matematikk 1T)", "aar": "VG1"},
            {"id": "1p", "navn": "1P (Matematikk 1P)", "aar": "VG1"},
            {"id": "2p", "navn": "2P (Matematikk 2P)", "aar": "VG2"},
            {"id": "r1", "navn": "R1 (Matematikk R1)", "aar": "VG2"},
            {"id": "s1", "navn": "S1 (Matematikk S1)", "aar": "VG2"},
            {"id": "r2", "navn": "R2 (Matematikk R2)", "aar": "VG3"},
            {"id": "s2", "navn": "S2 (Matematikk S2)", "aar": "VG3"},
        ]
    }
