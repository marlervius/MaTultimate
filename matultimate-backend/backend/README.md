# MaTultimate - Backend

> *Kvalitet først. Bredde etterpå.*

AI-drevet matematikkgenerator for norske lærere. Genererer differensierte oppgaveark med SymPy-verifiserte løsninger.

## 🎯 Hva er dette?

MaTultimate er et multi-agent system som:
- **Genererer matematikkoppgaver** tilpasset LK20-kompetansemål
- **Verifiserer alle svar** med SymPy (100% matematisk korrekthet)
- **Differensierer automatisk** i tre nivåer (grunnleggende/middels/utfordring)
- **Produserer ferdige dokumenter** i Typst eller LaTeX
- **Lager fasit** med steg-for-steg løsninger

## 📁 Struktur

```
backend/
├── app/
│   ├── core/
│   │   ├── math_engine.py      # SymPy-basert matematikkmotor
│   │   ├── sanitizer.py        # Fjerner markdown-fences, validerer kode
│   │   └── compiler.py         # Typst/LaTeX → PDF kompilering
│   ├── agents/
│   │   └── vgs_agent.py        # VGS-spesialist (R1, R2, S1, S2)
│   ├── models/                 # Pydantic-modeller (kommer)
│   └── api/                    # FastAPI-endepunkter (kommer)
├── tests/
│   └── test_integration.py     # Integrasjonstester
└── requirements.txt
```

## 🚀 Kom i gang

### 1. Installer avhengigheter
```bash
cd backend
pip install -r requirements.txt
```

### 2. Installer Typst
```bash
# Mac
brew install typst

# Windows
winget install typst

# Linux
curl -fsSL https://typst.community/typst-install/install.sh | sh
```

### 3. Kjør testene
```bash
python tests/test_integration.py
```

### 4. Generer et arbeidsark
```python
from app.agents.vgs_agent import VGSAgent, VGSKurs, Emne, OppgaveConfig

agent = VGSAgent()

config = OppgaveConfig(
    kurs=VGSKurs.R1,
    emne=Emne.DERIVASJON,
    antall_oppgaver=9,
    differensiering=True
)

oppgavesett = agent.generer_oppgavesett(config)
typst_code = agent.til_typst(oppgavesett)

# Lagre til fil
with open("arbeidsark.typ", "w") as f:
    f.write(typst_code)
```

### 5. Kompiler til PDF
```bash
typst compile arbeidsark.typ
```

## 🔧 Kjernekomponenter

### MathEngine
```python
from app.core.math_engine import MathEngine

engine = MathEngine()

# Verifiser derivasjon
result = engine.verify_derivative("x**3", "3*x**2")
print(result.is_correct)  # True

# Generer varianter
variants = engine.generate_derivative_variants("{a}*x**{n}", 5)

# Steg-for-steg løsning
solution = engine.derivative_step_by_step("x**2 * exp(x)")
```

### CodeSanitizer
```python
from app.core.sanitizer import sanitize, detect_format

# Fjern markdown code fences
result = sanitize("```typst\n#let x = 1\n```", 'typst')
print(result.cleaned_code)  # "#let x = 1"

# Detect format
format = detect_format("#set text(size: 12pt)")  # "typst"
```

### VGSAgent
```python
from app.agents.vgs_agent import VGSAgent, VGSKurs, Emne

agent = VGSAgent()

# Tilgjengelige kurs
# VGSKurs.T1, VGSKurs.P1, VGSKurs.R1, VGSKurs.R2, VGSKurs.S1, VGSKurs.S2

# Tilgjengelige emner
# Emne.DERIVASJON, Emne.INTEGRASJON, Emne.FUNKSJONER, ...
```

## 📊 Arkitekturprinsipp

```
Brukerforespørsel
       │
       ▼
┌─────────────┐
│  VGS Agent  │ ← Forstår LK20, genererer oppgaver
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Math Engine │ ← SymPy verifiserer ALT
│  (SymPy)    │   Genererer varianter
└──────┬──────┘   Steg-for-steg løsninger
       │
       ▼
┌─────────────┐
│  Sanitizer  │ ← Renser kode, fjerner feil
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Compiler   │ ← Typst/LaTeX → PDF
└──────┬──────┘
       │
       ▼
    📄 PDF
```

## 🎓 Differensieringsnivåer

| Nivå | Beskrivelse | Eksempel (derivasjon) |
|------|-------------|----------------------|
| **1** | Grunnleggende | $f(x) = x^3$ med hint |
| **2** | Middels | $f(x) = x^2 e^x$ (produktregel) |
| **3** | Utfordring | $f(x) = \ln(x^2+1)$ (kjerneregel) |

## 🔮 Roadmap

- [x] SymPy matematikkmotor
- [x] Code sanitizer
- [x] VGS-agent for R1/R2
- [x] Typst-dokumentgenerering
- [x] Tre-nivå differensiering
- [ ] FastAPI-endepunkter
- [ ] Streamlit-frontend
- [ ] Figurgenerering (TikZ/pgfplots)
- [ ] OneNote-integrasjon
- [ ] Oppgavebank med historikk
- [ ] Støtte for flere klassetrinn

## 📝 Lisens

MIT

---

*Bygget med ❤️ for norske matematikklærere*
