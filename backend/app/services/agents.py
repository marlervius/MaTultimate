import os
from crewai import Agent, LLM
from app.models.core import MaterialConfig
from app.core.curriculum import format_boundaries_for_prompt, get_grade_boundaries

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

    def pedagogue(self, config: MaterialConfig) -> Agent:
        grade_context = format_boundaries_for_prompt(config.grade)
        
        differentiation_instruction = ""
        if config.differentiation == "three_levels":
            differentiation_instruction = (
                "\n=== DIFFERENSIERING: TRE NIVÅER ===\n"
                "Du skal lage en plan som dekker TRE nivåer for de samme kompetansemålene:\n"
                "1. NIVÅ 1 (Grunnleggende): Færre steg, enklere tall, mer støtte/hints, gjerne utfylling.\n"
                "2. NIVÅ 2 (Middels): Standard nivå for trinnet.\n"
                "3. NIVÅ 3 (Utfordring): Flere steg, mer komplekse tall, krever kombinasjon av konsepter.\n"
                "Sørg for at hvert nivå har en tydelig overskrift i planen din."
            )

        backstory = (
            "Du er en ledende ekspert på norsk matematikkdidaktikk og læreplanen LK20. "
            "Din spesialitet er å designe læringsløp som fremmer dybdelæring, utforsking og forståelse.\n\n"
            "=== KRITISK: NIVÅTILPASNING ===\n"
            f"Du må planlegge innholdet spesifikt for {config.grade}. "
            "Dette innebærer:\n"
            "- Sikre at progresjonen er logisk (fra enkel til kompleks).\n"
            "- Inkludere elementer av utforsking og problemløsning.\n"
            "- Velge relevante kompetansemål fra LK20.\n\n"
            f"{grade_context}\n"
            f"{differentiation_instruction}\n\n"
            "Du skal produsere en detaljert plan som matematikeren kan bruke for å skrive innholdet."
        )

        return Agent(
            role="Pedagogisk arkitekt (LK20)",
            goal=f"Lag en pedagogisk optimal disposisjon for et {config.material_type} om {config.topic} for {config.grade}.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def mathematician(self, config: MaterialConfig) -> Agent:
        is_latex = config.output_format == "latex"
        format_name = "LaTeX" if is_latex else "Typst"
        
        differentiation_formatting = ""
        if config.differentiation == "three_levels":
            if is_latex:
                differentiation_formatting = (
                    "\n=== FORMATERING FOR TRE NIVÅER ===\n"
                    "Start hvert nivå på en ny side med \\newpage.\n"
                    "Bruk en tydelig overskrift for hvert nivå: \\section*{Nivå 1: Grunnleggende}, osv.\n"
                )
            else:
                differentiation_formatting = (
                    "\n=== FORMATERING FOR TRE NIVÅER ===\n"
                    "Start hvert nivå på en ny side med #pagebreak().\n"
                    "Bruk en tydelig overskrift for hvert nivå: = Nivå 1: Grunnleggende, osv.\n"
                )

        # Formatting rules based on format
        if is_latex:
            format_rules = (
                "1. DEFINISJONER: Bruk \\begin{definisjon} ... \\end{definisjon}\n"
                "2. EKSEMPLER: Bruk \\begin{eksempel}[title=...] ... \\end{eksempel}\n"
                "3. OPPGAVER: Bruk \\begin{taskbox}{Oppgave N} ... \\end{taskbox}\n"
                "4. FASIT: Bruk \\begin{losning} ... \\end{losning}\n"
                "5. MATEMATIKK: Bruk $...$ for inline og \\begin{equation} for display."
            )
        else:
            format_rules = (
                "1. DEFINISJONER: Bruk #definition[ ... ]\n"
                "2. EKSEMPLER: Bruk #example(title: \"...\")[ ... ]\n"
                "3. THEOREMER: Bruk #theorem[ ... ]\n"
                "4. MATEMATIKK: Bruk $ ... $ for både inline og display (display har mellomrom etter $)."
            )

        backstory = (
            f"Du er en presis matematiker som skriver elegant kode i {format_name}. "
            "Du er ekspert på å forklare komplekse konsepter på en forståelig måte for elever.\n\n"
            "=== VIKTIG: OUTPUT-FORMAT ===\n"
            f"Du skal returnere KUN rå {format_name}-kode. \n"
            "IKKE bruk markdown code fences (som ```latex eller ```typst).\n"
            "IKKE inkluder forklarende tekst før eller etter koden.\n"
            "Output skal kunne sendes direkte til en kompilator.\n\n"
            "=== DINE REGLER ===\n"
            f"{format_rules}\n"
            f"{differentiation_formatting}\n\n"
            "=== MATEMATISK RIGOR ===\n"
            "- Bruk korrekt notasjon.\n"
            "- Sørg for at alle mellomregninger i eksempler og løsninger er korrekte.\n"
            f"- Tilpass kompleksiteten til {config.grade}."
        )

        return Agent(
            role="Matematiker og innholdsprodusent",
            goal=f"Skriv det matematiske innholdet for {config.topic} i {format_name}-format.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def editor(self, config: MaterialConfig) -> Agent:
        format_name = "LaTeX" if config.output_format == "latex" else "Typst"
        
        backstory = (
            "Du er sjefredaktør for et stort forlag og har ansvar for at alle læremidler "
            "holder høyeste tekniske og språklige kvalitet.\n\n"
            "=== VIKTIG: OUTPUT-FORMAT ===\n"
            f"Du skal returnere KUN den ferdige, rå {format_name}-koden.\n"
            "IKKE bruk markdown code fences (som ```latex eller ```typst).\n"
            "IKKE inkluder kommentarer, forklaringer eller hilsener.\n"
            "Output skal være 100% klar for direkte kompilering.\n\n"
            f"Din oppgave er å gå gjennom {format_name}-koden og sikre:\n"
            "- At all kode er syntaktisk korrekt og kan kompileres.\n"
            "- At språket er feilfritt norsk (bokmål).\n"
            "- At alle bokser og miljøer er korrekt lukket.\n"
            "- At dokumentet har en profesjonell layout."
        )

        return Agent(
            role="Sjefredaktør",
            goal=f"Kvalitetssikre og ferdigstill {format_name}-dokumentet.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def solution_writer(self, config: MaterialConfig) -> Agent:
        is_latex = config.output_format == "latex"
        format_name = "LaTeX" if is_latex else "Typst"
        
        backstory = (
            f"Du er en matematikkdidaktiker som spesialiserer seg på å lage løsningsforslag. "
            "Din jobb er å ta oppgavene og lage en komplett fasit med steg-for-steg forklaringer.\n\n"
            "=== KRAV TIL LØSNING ===\n"
            "- Vis ALLE utregninger, ikke bare svaret.\n"
            "- Forklar det matematiske resonnementet bak hvert steg.\n"
            "- Bruk formatet: Oppgave X: [problem] -> Løsning: [steg] -> Svar: [endelig svar].\n"
            "- Overskriften skal inneholde: Tema, Klassetrinn, og teksten 'Kun for lærerbruk'.\n\n"
            "=== VIKTIG: OUTPUT-FORMAT ===\n"
            f"Du skal returnere KUN rå {format_name}-kode uten markdown fences.\n"
            "Output skal være et SEPARAT dokument klart for kompilering."
        )

        return Agent(
            role="Løsningsarkitekt",
            goal=f"Lag en komplett, pedagogisk fasit i {format_name}-format.",
            backstory=backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
