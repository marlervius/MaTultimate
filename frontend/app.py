# /frontend/app.py

import streamlit as st
import requests
import base64
from datetime import datetime
from typing import Optional

# === KONFIGURASJON ===
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# === SIDEOPPSETT ===
st.set_page_config(
    page_title="MaTultimate",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
    .download-section {
        background: linear-gradient(135deg, #667eea11 0%, #764ba211 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .level-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .level-1 { background: #d4edda; color: #155724; }
    .level-2 { background: #fff3cd; color: #856404; }
    .level-3 { background: #f8d7da; color: #721c24; }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
    }
    .stDownloadButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# === HJELPEFUNKSJONER ===
def get_pdf_download_link(base64_pdf: str, filename: str) -> bytes:
    """Konverter base64 til bytes for nedlasting."""
    return base64.b64decode(base64_pdf)


def render_pdf_preview(base64_pdf: str, height: int = 500):
    """Vis PDF-forhåndsvisning i iframe."""
    pdf_display = f"""
    <iframe 
        src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" 
        height="{height}px" 
        type="application/pdf"
        style="border: 1px solid #ddd; border-radius: 8px;">
    </iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)


def generate_material(config: dict) -> dict:
    """Kall backend API for å generere materiell."""
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json=config,
            timeout=120  # AI-generering kan ta tid
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "error_message": str(e)}


# === SESSION STATE INIT ===
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None
if "generation_history" not in st.session_state:
    st.session_state.generation_history = []


# === SIDEBAR: INNSTILLINGER ===
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=MaTultimate", width=200)
    st.markdown("---")
    
    st.header("⚙️ Innstillinger")
    
    # Faglig konfigurasjon
    with st.expander("📚 Faglig innhold", expanded=True):
        klassetrinn = st.selectbox(
            "Klassetrinn",
            options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "vg1", "vg2", "vg3"],
            index=7,  # Default: 8. trinn
            help="Velg klassetrinn for oppgavesettet"
        )
        
        emne = st.text_input(
            "Emne",
            value="Potenser",
            max_chars=100,
            help="F.eks. 'Potenser', 'Brøk', 'Lineære funksjoner'"
        )
        
        kompetansemaal = st.text_area(
            "Kompetansemål (LK20)",
            value="Eleven skal kunne utforske og beskrive strukturer og forandringer i geometriske mønster og tallmønster med figurer, ord og formler",
            height=100,
            help="Lim inn kompetansemålet fra LK20"
        )
    
    # Differensiering
    with st.expander("🎯 Differensiering", expanded=True):
        use_differentiation = st.toggle(
            "Generer tre differensierte nivåer",
            value=False,
            help="Lag Nivå 1 (grunnleggende), Nivå 2 (middels) og Nivå 3 (utfordring)"
        )
        
        if use_differentiation:
            st.markdown("""
            <div style="font-size: 0.85rem; color: #666; margin-top: 0.5rem;">
                <span class="level-badge level-1">Nivå 1</span> Grunnleggende<br>
                <span class="level-badge level-2">Nivå 2</span> Middels<br>
                <span class="level-badge level-3">Nivå 3</span> Utfordring
            </div>
            """, unsafe_allow_html=True)
            
            export_format = st.radio(
                "Eksportformat",
                options=["combined_pdf", "separate_files"],
                format_func=lambda x: "Én samlet PDF" if x == "combined_pdf" else "Separate filer",
                help="Velg om du vil ha alt i én fil eller separate filer per nivå"
            )
        else:
            export_format = "combined_pdf"
    
    # Fasit
    with st.expander("✅ Fasit", expanded=True):
        include_answer_key = st.toggle(
            "Inkluder fasit med løsningsforslag",
            value=True,
            help="Generer separat dokument med steg-for-steg løsninger"
        )
        
        if include_answer_key:
            st.info("Fasiten inkluderer full utregning for hver oppgave, ikke bare svar.")
    
    # Avanserte innstillinger
    with st.expander("🔧 Avansert", expanded=False):
        antall_oppgaver = st.slider(
            "Antall oppgaver per nivå",
            min_value=3,
            max_value=20,
            value=8
        )
        
        include_hints = st.checkbox(
            "Inkluder hint på Nivå 1",
            value=True
        )
        
        include_visuals = st.checkbox(
            "Inkluder illustrasjoner",
            value=False,
            help="Eksperimentell: Legg til TikZ-figurer"
        )
        
        document_format = st.radio(
            "Dokumentformat",
            options=["typst", "latex"],
            format_func=lambda x: "Typst (raskere)" if x == "typst" else "LaTeX (flere pakker)"
        )


# === HOVEDINNHOLD ===
st.title("📐 MaTultimate")
st.markdown("*Generer differensierte matematikkoppgaver med AI*")

# Generer-knapp
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    generate_clicked = st.button(
        "🚀 Generer materiell",
        type="primary",
        use_container_width=True
    )

if generate_clicked:
    # Bygg konfigurasjon
    config = {
        "klassetrinn": klassetrinn,
        "emne": emne,
        "kompetansemaal": kompetansemaal,
        "differentiation": "three_levels" if use_differentiation else "single",
        "include_answer_key": include_answer_key,
        "document_format": document_format,
        "export_format": export_format,
        "antall_oppgaver": antall_oppgaver,
        "include_hints": include_hints,
        "include_visuals": include_visuals
    }
    
    with st.spinner("🔮 Genererer materiell... Dette kan ta 30-60 sekunder."):
        result = generate_material(config)
        st.session_state.generated_result = result
        
        # Legg til i historikk
        if result.get("success"):
            st.session_state.generation_history.append({
                "timestamp": datetime.now(),
                "config": config,
                "result": result
            })


# === RESULTATVISNING ===
if st.session_state.generated_result:
    result = st.session_state.generated_result
    
    if result.get("success"):
        st.markdown('<div class="success-box">✅ Materiell generert!</div>', unsafe_allow_html=True)
        
        # Metadata
        metadata = result.get("metadata", {})
        st.markdown(f"""
        **Generert:** {metadata.get('klassetrinn', '')}. trinn · {metadata.get('emne', '')} · 
        {metadata.get('levels', 1)} nivå(er)
        """)
        
        st.markdown("---")
        
        # === NEDLASTINGSSEKSJON ===
        st.subheader("📥 Last ned")
        
        # Dynamisk visning basert på hva som ble generert
        download_cols = st.columns(2 if include_answer_key else 1)
        
        with download_cols[0]:
            st.markdown("#### 📄 Elevark")
            
            if export_format == "separate_files" and use_differentiation:
                # Separate filer per nivå
                level_cols = st.columns(3)
                
                if result.get("level_1_pdf"):
                    with level_cols[0]:
                        st.download_button(
                            label="⬇️ Nivå 1",
                            data=get_pdf_download_link(result["level_1_pdf"], ""),
                            file_name=f"{emne.lower()}_nivaa1_{klassetrinn}.pdf",
                            mime="application/pdf"
                        )
                
                if result.get("level_2_pdf"):
                    with level_cols[1]:
                        st.download_button(
                            label="⬇️ Nivå 2",
                            data=get_pdf_download_link(result["level_2_pdf"], ""),
                            file_name=f"{emne.lower()}_nivaa2_{klassetrinn}.pdf",
                            mime="application/pdf"
                        )
                
                if result.get("level_3_pdf"):
                    with level_cols[2]:
                        st.download_button(
                            label="⬇️ Nivå 3",
                            data=get_pdf_download_link(result["level_3_pdf"], ""),
                            file_name=f"{emne.lower()}_nivaa3_{klassetrinn}.pdf",
                            mime="application/pdf"
                        )
            else:
                # Én samlet fil
                if result.get("worksheet_pdf"):
                    st.download_button(
                        label="⬇️ Last ned elevark (PDF)",
                        data=get_pdf_download_link(result["worksheet_pdf"], ""),
                        file_name=f"{emne.lower()}_{klassetrinn}_elevark.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        if include_answer_key and result.get("answer_key_pdf"):
            with download_cols[1]:
                st.markdown("#### 🔑 Fasit")
                st.download_button(
                    label="⬇️ Last ned fasit (PDF)",
                    data=get_pdf_download_link(result["answer_key_pdf"], ""),
                    file_name=f"{emne.lower()}_{klassetrinn}_fasit.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.caption("Inneholder steg-for-steg løsninger")
        
        # Kildekode (for debugging/redigering)
        with st.expander("🔧 Vis kildekode"):
            source_tab, answer_tab = st.tabs(["Elevark", "Fasit"])
            
            with source_tab:
                if result.get("source_code"):
                    st.code(result["source_code"], language="latex" if document_format == "latex" else "text")
                    st.download_button(
                        label="Last ned kildekode",
                        data=result["source_code"],
                        file_name=f"{emne.lower()}_{klassetrinn}.{'tex' if document_format == 'latex' else 'typ'}",
                        mime="text/plain"
                    )
            
            with answer_tab:
                if result.get("answer_key_source"):
                    st.code(result["answer_key_source"], language="latex" if document_format == "latex" else "text")
        
        # === FORHÅNDSVISNING ===
        st.markdown("---")
        st.subheader("👁️ Forhåndsvisning")
        
        preview_tabs = st.tabs(["Elevark", "Fasit"] if include_answer_key else ["Elevark"])
        
        with preview_tabs[0]:
            if result.get("worksheet_pdf"):
                render_pdf_preview(result["worksheet_pdf"])
        
        if include_answer_key and len(preview_tabs) > 1:
            with preview_tabs[1]:
                if result.get("answer_key_pdf"):
                    render_pdf_preview(result["answer_key_pdf"])
    
    else:
        # Feilhåndtering
        st.error(f"❌ Generering feilet: {result.get('error_message', 'Ukjent feil')}")
        
        if result.get("raw_ai_output"):
            with st.expander("🔍 Debug: Rå AI-output"):
                st.code(result["raw_ai_output"])
                st.info("Du kan kopiere denne koden og manuelt fikse eventuelle syntaksfeil.")


# === FOOTER ===
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.85rem;'>"
    "MaTultimate · Laget for norske lærere · Følger LK20"
    "</div>",
    unsafe_allow_html=True
)
