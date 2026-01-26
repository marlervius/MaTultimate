"""
MaTultimate API
===============
Hovedapplikasjon for MaTultimate backend.

Kjør med:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .api.routes import router

# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="MaTultimate API",
    description="""
## AI-drevet matematikkgenerator for norske lærere

MaTultimate genererer differensierte matematikkoppgaver med:
- ✅ **SymPy-verifiserte svar** (100% matematisk korrekthet)
- ✅ **Tre nivåer** (grunnleggende, middels, utfordring)
- ✅ **Steg-for-steg fasit**
- ✅ **LK20-tilpasset** innhold

### Støttede kurs
- VG1: 1T, 1P
- VG2: 2P, R1, S1
- VG3: R2, S2

### Støttede emner
Derivasjon, integrasjon, funksjoner, algebra, vektorer, 
sannsynlighet, statistikk, geometri, økonomi

---
*Kvalitet først. Bredde etterpå.*
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# =============================================================================
# CORS
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev
        "http://localhost:8501",      # Streamlit
        "https://*.streamlit.app",    # Streamlit Cloud
        "https://*.railway.app",      # Railway
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROUTES
# =============================================================================

app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect til dokumentasjon."""
    return RedirectResponse(url="/docs")


@app.get("/status")
async def status():
    """Enkel status-sjekk."""
    return {
        "status": "online",
        "app": "MaTultimate",
        "version": "0.1.0"
    }


# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Kjører ved oppstart."""
    print("🚀 MaTultimate API starter...")
    print("📚 Dokumentasjon: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Kjører ved avslutning."""
    print("👋 MaTultimate API avslutter...")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
