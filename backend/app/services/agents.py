import os
from datetime import datetime
from crewai import Agent, LLM
from app.models.config import MaterialConfig
from app.core.curriculum import format_boundaries_for_prompt, get_grade_boundaries
from dotenv import load_dotenv

load_dotenv()

from app.prompts.vgs_agents import VGS_PEDAGOGUE_PROMPT, VGS_MATHEMATICIAN_PROMPT
from app.agents.figur_agent import FigurAgent

class MaTultimateAgents:
    def __init__(self):
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("LLM_API_KEY")
        # Google Gemini model configuration
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.4
        )
        # FigurAgent krever llm parameter
        self.figur_factory = FigurAgent(llm=self.llm)

    def pedagogue(self, config: MaterialConfig) -> Agent:
        # Use getattr to safely access properties or fields
        klassetrinn = getattr(config, 'klassetrinn', getattr(config, 'grade', '8'))
        emne = getattr(config, 'emne', getattr(config, 'topic', 'Matematikk'))
        kompetansemaal = getattr(config, 'kompetansemaal', getattr(config, 'competency_goals', ''))
        if isinstance(kompetansemaal, list):
            kompetansemaal = ", ".join(kompetansemaal)

        is_vgs = any(v in str(klassetrinn).lower() for v in ["vg", "r1", "r2", "s1", "s2", "1t", "1p"])
        vgs_context = VGS_PEDAGOGUE_PROMPT if is_vgs else ""

        grade_context = format_boundaries_for_prompt(str(klassetrinn))
        
        if config.differentiation == "three_levels":
            backstory = (
                f"{vgs_context}\n\n"
                "Du er en erfaren matematikklærer med ekspertise i tilpasset opplæring etter Kunnskapsløftet (LK20).\n\n"
                "=== OPPGAVE ===\n"
                "Lag en pedagogisk plan for tre differensierte nivåer av et arbeidsark.\n"
                "Alle nivåer skal dekke SAMME kompetansemål, men med ulik kompleksitet.\n\n"
                f"KOMPETANSEMÅL: {kompetansemaal}\n"
                f"KLASSETRINN: {klassetrinn}\n"
                f"EMNE: {emne}\n\n"
                "=== DIFFERENSIERINGSPRINSIPPER ===\n\n"
                "## NIVÅ 1 – Grunnleggende\n"
                "Målgruppe: Elever som trenger ekstra støtte eller er i startfasen av å forstå konseptet.\n"
                "- Bruk SMÅ, HELE tall (1-20 for barnetrinn, 1-100 for ungdomstrinn)\n"
                "- Maks 2 regneoperasjoner per oppgave\n"
                "- Inkluder visuell støtte (tegninger, tallinjer, rutenett)\n"
                "- Gi delvis utfylte eksempler (\"Regn ut: 2³ = 2 · 2 · __ = __\")\n"
                "- Formuler oppgaver med konkrete, hverdagslige kontekster\n"
                "- 5-6 oppgaver totalt\n\n"
                "## NIVÅ 2 – Middels\n"
                "Målgruppe: Elever som har grunnleggende forståelse og er klare for standard pensum.\n"
                "- Bruk varierte tall, inkludert tosifrede tall og enkle desimaltall\n"
                "- 2-3 regneoperasjoner per oppgave\n"
                "- Bland prosedyreoppgaver med enkle tekstoppgaver\n"
                "- Inkluder 1-2 oppgaver som krever forklaring (\"Forklar hvorfor...\")\n"
                "- 6-8 oppgaver totalt\n\n"
                "## NIVÅ 3 – Utfordring\n"
                "Målgruppe: Elever som mestrer pensum og trenger ekstra utfordringer.\n"
                "- Bruk større tall, negative tall, brøker der relevant\n"
                "- Flerstegsproblemer som krever at eleven kombinerer flere konsepter\n"
                "- Inkluder problemløsningsoppgaver uten opplagt fremgangsmåte\n"
                "- Minst én oppgave som krever resonnering eller bevisføring\n"
                "- Inkluder \"feilsøkingsoppgaver\" (\"Lisa påstår at... Har hun rett?\")\n"
                "- 6-8 oppgaver totalt\n\n"
                "=== VIKTIG ===\n"
                "- Samme matematiske konsept på alle nivåer – kun kompleksiteten endres\n"
                "- Progresjon INNAD i hvert nivå: start enkelt, øk gradvis\n"
                "- Nivå 1 er IKKE \"dummet ned\" – det er stillasbyggende\n"
            )
        else:
            backstory = (
                f"{vgs_context}\n\n"
                "Du er en ledende ekspert på norsk matematikkdidaktikk og læreplanen LK20. "
                "Din spesialitet er å designe læringsløp som fremmer dybdelæring, utforsking og forståelse.\n\n"
                "=== KRITISK: NIVÅTILPASNING ===\n"
                f"Du må planlegge innholdet spesifikt for {klassetrinn}. "
                "Dette innebærer:\n"
                "- Sikre at progresjonen er logisk (fra enkel til kompleks).\n"
                "- Inkludere elementer av utforsking og problemløsning.\n"
                "- Velge relevante kompetansemål fra LK20.\n\n"
                f"{grade_context}\n\n"
                "Du skal produsere en detaljert plan som matematikeren kan bruke for å skrive innholdet."
            )

        return Agent(
            role="Pedagogisk arkitekt (LK20)",
            goal=f"Lag en pedagogisk optimal disposisjon for et matematikkmateriell om {emne} for {klassetrinn}.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def mathematician(self, config: MaterialConfig) -> Agent:
        klassetrinn = getattr(config, 'klassetrinn', getattr(config, 'grade', '8'))
        emne = getattr(config, 'emne', getattr(config, 'topic', 'Matematikk'))
        doc_format = getattr(config, 'document_format', getattr(config, 'output_format', 'typst'))
        if hasattr(doc_format, 'value'):
            doc_format = doc_format.value

        is_latex = doc_format == "latex"
        format_name = "LaTeX" if is_latex else "Typst"
        
        is_vgs = any(v in str(klassetrinn).lower() for v in ["vg", "r1", "r2", "s1", "s2", "1t", "1p"])
        vgs_context = VGS_MATHEMATICIAN_PROMPT if is_vgs else ""

        if config.differentiation == "three_levels":
            if not is_latex: # Typst differentiation prompt
                backstory = (
                    f"{vgs_context}\n\n"
                    "Du er en teknisk skribent som konverterer pedagogiske planer til kompilerbar kode.\n\n"
                    "=== FORMATERINGSKRAV FOR TYPST ===\n"
                    "1. Bruk page breaks mellom nivåer: #pagebreak()\n"
                    "2. Hver nivå får en tydelig header:\n"
                    "   #heading(level: 1)[Nivå 1 – Grunnleggende]\n"
                    "3. Bruk definerte box-stiler for oppgavetyper:\n"
                    "   - #oppgave[...] for standard oppgaver\n"
                    "   - #utfordring[...] for nivå 3-oppgaver\n"
                    "   - #hint[...] for scaffolding-hint på nivå 1\n\n"
                    "4. For matematikk, bruk $...$ for inline og $ ... $ for utstilt\n\n"
                    "5. Nummerer oppgaver konsekvent: 1a, 1b, 2a, 2b osv.\n\n"
                    "6. VIKTIG: IKKE inkluder preamble (#set page, #let oppgave osv.). Dette blir lagt til automatisk.\n\n"
                    "=== STRUKTUR ===\n"
                    "// Nivå 1\n"
                    "#heading(level: 1)[Nivå 1 – Grunnleggende]\n"
                    "#v(0.5em)\n"
                    "#text(style: \"italic\")[Disse oppgavene hjelper deg å forstå det grunnleggende.]\n\n"
                    "[oppgaver...]\n\n"
                    "#pagebreak()\n\n"
                    "// Nivå 2\n"
                    "#heading(level: 1)[Nivå 2 – Middels]\n"
                    "...\n\n"
                    "#pagebreak()\n\n"
                    "// Nivå 3\n"
                    "#heading(level: 1)[Nivå 3 – Utfordring]\n"
                    "...\n\n"
                    "=== KRITISK ===\n"
                    "- Returner KUN rå Typst-kode\n"
                    "- INGEN markdown code fences (```)\n"
                    "- INGEN forklarende tekst før eller etter koden\n"
                    "- Koden skal kompilere direkte uten modifikasjon"
                )
            else: # LaTeX differentiation prompt (adapted from your Typst requirements)
                backstory = (
                    f"{vgs_context}\n\n"
                    "Du er en teknisk skribent som konverterer pedagogiske planer til kompilerbar LaTeX-kode.\n\n"
                    "=== FORMATERINGSKRAV FOR LATEX ===\n"
                    "1. Bruk page breaks mellom nivåer: \\newpage\n"
                    "2. Hver nivå får en tydelig header: \\section*{Nivå X – ...}\n"
                    "3. Bruk definerte miljøer:\n"
                    "   - \\begin{taskbox}{Oppgave N} ... \\end{taskbox} for oppgaver\n"
                    "   - \\begin{merk} ... \\end{merk} for scaffolding-hint på nivå 1\n\n"
                    "4. Nummerer oppgaver konsekvent: 1a, 1b, 2a, 2b osv.\n\n"
                    "=== KRITISK ===\n"
                    "- Returner KUN rå LaTeX-kode\n"
                    "- INGEN markdown code fences (```)\n"
                    "- INGEN forklarende tekst før eller etter koden\n"
                    "- Koden skal kompilere direkte uten modifikasjon"
                )
        else:
            # Standard single-level prompt
            format_rules = (
                "1. DEFINISJONER: Bruk \\begin{definisjon} ... \\end{definisjon}\n"
                "2. EKSEMPLER: Bruk \\begin{eksempel}[title=...] ... \\end{eksempel}\n"
                "3. OPPGAVER: Bruk \\begin{taskbox}{Oppgave N} ... \\end{taskbox}\n"
                "4. FASIT: Bruk \\begin{losning} ... \\end{losning}\n"
                "5. MATEMATIKK: Bruk $...$ for inline og \\begin{equation} for display."
            ) if is_latex else (
                "1. DEFINISJONER: Bruk #definition[ ... ]\n"
                "2. EKSEMPLER: Bruk #example(title: \"...\")[ ... ]\n"
                "3. THEOREMER: Bruk #theorem[ ... ]\n"
                "4. MATEMATIKK: Bruk $ ... $ for både inline og display (display har mellomrom etter $)."
            )

            backstory = (
                f"{vgs_context}\n\n"
                f"Du er en presis matematiker som skriver elegant kode i {format_name}. "
                "Du er ekspert på å forklare komplekse konsepter på en forståelig måte for elever.\n\n"
                "=== VIKTIG: OUTPUT-FORMAT ===\n"
                f"Du skal returnere KUN rå {format_name}-kode. \n"
                "IKKE bruk markdown code fences (```latex eller ```typst).\n"
                "IKKE inkluder forklarende tekst før eller etter koden.\n"
                "Output skal kunne sendes direkte til en kompilator.\n\n"
                "=== DINE REGLER ===\n"
                f"{format_rules}\n\n"
                "=== MATEMATISK RIGOR ===\n"
                "- Bruk korrekt notasjon.\n"
                "- Sørg for at alle mellomregninger i eksempler og løsninger er korrekte.\n"
                f"- Tilpass kompleksiteten til {klassetrinn}."
            )

        return Agent(
            role="Matematiker og innholdsprodusent",
            goal=f"Skriv det matematiske innholdet for {emne} i {format_name}-format.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def editor(self, config: MaterialConfig) -> Agent:
        doc_format = getattr(config, 'document_format', getattr(config, 'output_format', 'typst'))
        if hasattr(doc_format, 'value'):
            doc_format = doc_format.value
        format_name = "LaTeX" if doc_format == "latex" else "Typst"
        
        backstory = (
            "Du er en kvalitetskontrollør for matematiske dokumenter.\n\n"
            "=== VALIDER FØLGENDE ===\n\n"
            "1. KODE-HYGIENE:\n"
            "   - Ingen markdown code fences (``` skal IKKE forekomme)\n"
            "   - Alle Typst/LaTeX-miljøer er lukket korrekt\n"
            "   - Ingen ubalanserte parenteser eller krøllparenteser\n\n"
            "2. PEDAGOGISK KONSISTENS:\n"
            "   - Nivå 1 har faktisk enklere tall/færre steg enn nivå 2\n"
            "   - Nivå 3 har faktisk mer komplekse oppgaver enn nivå 2\n"
            "   - Alle nivåer dekker samme kompetansemål\n\n"
            "3. FASIT-VALIDERING:\n"
            "   - Hver oppgave i elevark har en tilsvarende løsning i fasit\n"
            "   - Løsningene are matematisk korrekte (regn etter!)\n"
            "   - Steg-for-steg viser faktisk alle mellomsteg\n\n"
            "4. FORMATERING:\n"
            "   - Sideskift mellom nivåer\n"
            "   - Konsekvent nummerering\n"
            "   - Lesbar layout\n\n"
            "=== OUTPUT ===\n"
            "Hvis alt er OK: Returner den uendrede koden.\n"
            "Hvis feil finnes: Rett feilen og returner korrigert kode.\n\n"
            "ALDRI returner feilmeldinger eller kommentarer – kun korrigert kode.\n"
            "Returner KUN den rå koden uten markdown fences."
        )

        return Agent(
            role="Sjefredaktør og Kvalitetskontrollør",
            goal=f"Kvalitetssikre og ferdigstill {format_name}-dokumentet.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def solution_writer(self, config: MaterialConfig) -> Agent:
        emne = getattr(config, 'emne', getattr(config, 'topic', 'Matematikk'))
        doc_format = getattr(config, 'document_format', getattr(config, 'output_format', 'typst'))
        if hasattr(doc_format, 'value'):
            doc_format = doc_format.value
            
        is_latex = doc_format == "latex"
        format_name = "LaTeX" if is_latex else "Typst"
        
        if not is_latex: # Typst solution prompt
            backstory = (
                "Du er en matematikklærer som lager detaljerte løsningsforslag.\n\n"
                "=== OPPGAVE ===\n"
                "Lag en komplett fasit med steg-for-steg løsninger for alle oppgaver.\n\n"
                "=== KRAV TIL LØSNINGER ===\n"
                "1. VIS ALLTID UTREGNINGEN – ikke bare svaret\n"
                "   Feil: \"Svar: 16\"\n"
                "   Riktig: \"2⁴ = 2 · 2 · 2 · 2 = 4 · 2 · 2 = 8 · 2 = 16\"\n\n"
                "2. FORKLAR TANKEGANGEN ved overganger\n"
                "   \"Vi bruker potensregelen a^n · a^m = a^(n+m), så...\"\n\n"
                "3. For tekstoppgaver:\n"
                "   - Sett opp regnestykket først\n"
                "   - Vis mellomregning\n"
                "   - Formuler svaret i en hel setning\n\n"
                "4. For \"forklar hvorfor\"-oppgaver:\n"
                "   - Gi et fullstendig resonnement\n"
                "   - Inkluder et konkret talleksempel som illustrerer poenget\n\n"
                "5. For feilsøkingsoppgaver:\n"
                "   - Vis den korrekte utregningen\n"
                "   - Forklar HVOR feilen ligger og HVORFOR det er feil\n\n"
                "=== OUTPUTFORMAT (Typst) ===\n"
                "#set text(size: 10pt)\n"
                f"#heading(level: 1)[Fasit – {emne}]\n"
                f"#text(style: \"italic\", fill: gray)[Kun for lærerbruk. Generert {datetime.now().strftime('%d.%m.%Y')}.]\n\n"
                "#v(1em)\n\n"
                "#heading(level: 2)[Nivå 1 – Grunnleggende]\n\n"
                "*Oppgave 1a:*\n"
                "$ 2^3 = 2 · 2 · 2 = 8 $\n\n"
                "=== KRITISK ===\n"
                "- Returner KUN rå Typst-kode\n"
                "- INGEN markdown-formatering\n"
                "- Løsningene må matche oppgavene eksakt"
            )
        else: # LaTeX solution prompt (adapted)
            backstory = (
                "Du er en matematikklærer som lager detaljerte løsningsforslag i LaTeX.\n\n"
                "=== KRAV TIL LØSNINGER ===\n"
                "- VIS ALLTID UTREGNINGEN (steg-for-steg).\n"
                "- Forklar tankegangen ved overganger.\n"
                "- For tekstoppgaver: Sett opp regnestykket, vis utregning og svar med hel setning.\n"
                "- Overskrift: \\section*{Fasit – " + emne + "}\n"
                "- Inkluder 'Kun for lærerbruk' og dato.\n\n"
                "=== KRITISK ===\n"
                "- Returner KUN rå LaTeX-kode\n"
                "- INGEN markdown code fences (```)\n"
                "- Løsningene må matche oppgavene eksakt"
            )

        return Agent(
            role="Løsningsarkitekt",
            goal=f"Lag en komplett, pedagogisk fasit i {format_name}-format.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
