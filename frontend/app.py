import streamlit as st
import requests
import base64
import os
import time
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Last inn miljøvariabler
load_dotenv()

# Konfigurasjon
base_url = os.getenv("API_URL", "http://localhost:8080").rstrip("/")
if not base_url.endswith("/api/v1") and not "/api/v1/" in base_url:
    API_URL = f"{base_url}/api/v1"
else:
    API_URL = base_url

st.set_page_config(
    page_title="MaTultimate - AI Matematikk for Lærere",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for et moderne utseende
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    .status-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def display_pdf(base64_pdf: str):
    """Viser PDF i en iframe."""
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    st.title("📐 MaTultimate")
    st.subheader("Det ultimate verktøyet for matematikk-lærere")

    tab1, tab2 = st.tabs(["🆕 Generer Nytt", "📚 Oppgavebank & Historikk"])

    with tab1:
        # Sidebar for konfigurasjon
        with st.sidebar:
            st.header("🛠️ Innstillinger")
            
            klassetrinn = st.selectbox(
                "Klassetrinn / Kurs",
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "1T", "1P", "R1", "R2", "S1", "S2"],
                index=12  # Default R1
            )
            
            emne = st.text_input("Emne", placeholder="f.eks. Derivasjon")
            
            kompetansemaal = st.text_area(
                "Kompetansemål (LK20)", 
                placeholder="Lim inn kompetansemål her...",
                height=100
            )
            
            with st.expander("Avanserte valg"):
                differentiation = st.radio(
                    "Differensiering",
                    ["Enkelt nivå", "Tre nivåer (Nivå 1-3)"],
                    index=1
                )
                
                doc_format = st.selectbox(
                    "Dokumentformat",
                    ["Typst (Raskest)", "LaTeX", "Hybrid (Best figurer)"],
                    index=0
                )
                
                include_fasit = st.checkbox("Inkluder fasit", value=True)

            generate_button = st.button("🚀 Generer Materiell")

        # Hovedområde
        col1, col2 = st.columns([1, 1])

        if generate_button:
            if not emne or not kompetansemaal:
                st.error("Vennligst fyll inn både emne og kompetansemål.")
            else:
                with st.spinner("🧠 Agentene jobber... Dette kan ta 30-60 sekunder."):
                    try:
                        # Forbered request
                        payload = {
                            "klassetrinn": klassetrinn,
                            "emne": emne,
                            "kompetansemaal": kompetansemaal,
                            "differentiation": "three_levels" if differentiation == "Tre nivåer (Nivå 1-3)" else "single",
                            "include_answer_key": include_fasit,
                            "document_format": doc_format.split()[0].lower()
                        }
                        
                        response = requests.post(f"{API_URL}/generate", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            st.success("🚀 Generering startet! Jeg henter PDF-en så snart den er klar...")
                            
                            # Polling-logikk
                            found = False
                            with st.status("Venter på at agentene skal bli ferdige...", expanded=True) as status:
                                for i in range(60): # Sjekk i 5 minutter
                                    time.sleep(5)
                                    hist_res = requests.get(f"{API_URL}/history?limit=1")
                                    if hist_res.status_code == 200:
                                        history = hist_res.json()
                                        if history and history[0]['emne'] == emne:
                                            st.session_state.current_result = {
                                                "success": True,
                                                "worksheet_pdf": history[0].get('worksheet_pdf_b64'),
                                                "source_code": history[0].get('source_code')
                                            }
                                            status.update(label="✅ Ferdig!", state="complete")
                                            found = True
                                            break
                                    status.write(f"Sjekker status... ({i*5}s)")
                            
                            if not found:
                                st.warning("Det tar litt tid, men PDF-en dukker opp i Oppgavebanken snart!")
                            else:
                                st.rerun()
                        else:
                            st.error(f"API-feil ({response.status_code}): {response.text}")
                    except Exception as e:
                        st.error(f"Kunne ikke koble til backend: {str(e)}")

        # Vis resultater hvis de finnes
        if "current_result" in st.session_state:
            res = st.session_state.current_result
            
            with col1:
                st.header("📄 Forhåndsvisning")
                if res.get("worksheet_pdf"):
                    display_pdf(res["worksheet_pdf"])
                else:
                    st.info("Kildekode generert (PDF-kompilering er i beta):")
                    st.code(res.get("source_code"), language="rust" if "typst" in doc_format.lower() else "latex")

            with col2:
                st.header("📥 Nedlasting")
                
                if res.get("worksheet_pdf"):
                    st.download_button(
                        label="⬇️ Last ned Elevark (PDF)",
                        data=base64.b64decode(res["worksheet_pdf"]),
                        file_name=f"MaTultimate_{emne}_{klassetrinn}.pdf",
                        mime="application/pdf"
                    )
                
                if res.get("answer_key_pdf"):
                    st.download_button(
                        label="⬇️ Last ned Fasit (PDF)",
                        data=base64.b64decode(res["answer_key_pdf"]),
                        file_name=f"MaTultimate_{emne}_{klassetrinn}_fasit.pdf",
                        mime="application/pdf"
                    )
                
                with st.expander("Se kildekode"):
                    st.code(res.get("source_code"), language="rust" if "typst" in doc_format.lower() else "latex")
                    
                st.info("💡 Tips: Du kan dra PDF-filen direkte inn i OneNote for enkel deling med elever.")

        else:
            with col1:
                st.info("Fyll ut skjemaet til venstre og klikk 'Generer' for å starte magien! ✨")
                st.image("https://images.unsplash.com/photo-1509228468518-180dd48a5d5f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", use_column_width=True)

    with tab2:
        st.header("📚 Din Oppgavebank")
        st.write("Her finner du dine tidligere genererte dokumenter.")
        
        if st.button("🔄 Oppdater historikk"):
            try:
                response = requests.get(f"{API_URL}/history", timeout=10)
                if response.status_code == 200:
                    st.session_state.history = response.json()
                else:
                    st.error("Kunne ikke hente historikk fra serveren.")
            except Exception as e:
                st.error(f"Tilkoblingsfeil: {e}")

        if "history" in st.session_state and st.session_state.history:
            for item in st.session_state.history:
                with st.expander(f"📅 {item['timestamp'][:16]} | {item['title']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Trinn:** {item['klassetrinn']}")
                        st.write(f"**Emne:** {item['emne']}")
                        if item.get('worksheet_pdf_b64'):
                            st.download_button(
                                label="⬇️ Last ned PDF",
                                data=base64.b64decode(item['worksheet_pdf_b64']),
                                file_name=f"{item['title']}.pdf",
                                mime="application/pdf",
                                key=f"dl_{item['id']}"
                            )
                    with c2:
                        st.write("**Kildekode:**")
                        st.code(item['source_code'][:200] + "...", language="latex")
        else:
            st.info("Ingen historikk funnet ennå. Begynn å generere materiell!")

if __name__ == "__main__":
    main()
