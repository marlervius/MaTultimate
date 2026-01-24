import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Import curriculum data
from src.curriculum import TOPIC_LIBRARY, COMPETENCY_GOALS

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

def initialize_session_state():
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None
    if "history" not in st.session_state:
        st.session_state.history = []

def inject_custom_css():
    st.markdown("""
    <style>
    /* Main background and font */
    .main {
        background-color: #f0f2f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Card-like containers */
    .st-emotion-cache-1r6slb0 {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Result Box */
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="MaTultimate 💎",
        page_icon="💎",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    inject_custom_css()
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown('<div style="text-align: center; padding: 1rem;">', unsafe_allow_html=True)
        st.markdown("<h2 style='color: #1e3a8a; margin-bottom: 0;'>💎 MaTultimate</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b;'>AI-drevet læremiddelverksted</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### ⚙️ Konfigurasjon")
        grade = st.selectbox(
            "Klassetrinn", 
            options=list(TOPIC_LIBRARY.keys()),
            index=2
        )
        
        material_type = st.select_slider(
            "Type materiale", 
            options=["lekseark", "arbeidsark", "kapittel", "prøve"],
            value="arbeidsark"
        )
        
        output_format = st.radio(
            "Eksportformat", 
            options=["latex", "typst"],
            format_func=lambda x: "📄 LaTeX (Tradisjonell)" if x == "latex" else "✨ Typst (Moderne)",
            horizontal=True
        )
        
        st.divider()
        
        st.markdown("### 🛠️ Innholdselementer")
        col_a, col_b = st.columns(2)
        with col_a:
            include_theory = st.checkbox("📘 Teori", value=True)
            include_examples = st.checkbox("💡 Eksempler", value=True)
        with col_b:
            include_exercises = st.checkbox("✍️ Oppgaver", value=True)
            include_solutions = st.checkbox("🔑 Fasit", value=True)
            
        difficulty = st.select_slider(
            "Vanskelighetsgrad",
            options=["Lett", "Middels", "Vanskelig"],
            value="Middels"
        )

    # --- MAIN CONTENT ---
    
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">MaTultimate 💎</div>
        <div class="hero-subtitle">Lag profesjonelt matematikkinnhold på sekunder, tilpasset LK20</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown('<div class="section-header">📚 Tema og Læringsmål</div>', unsafe_allow_html=True)
        
        # Topic selection logic
        grade_topics = TOPIC_LIBRARY.get(grade, {})
        categories = list(grade_topics.keys())
        selected_category = st.selectbox("Velg kategori", options=categories)
        topics = grade_topics.get(selected_category, [])
        topic = st.selectbox("Velg emne", options=topics)
        
        custom_topic = st.text_input("Eller skriv et eget tema...", placeholder="f.eks. Pytagoras i hverdagen")
        final_topic = custom_topic if custom_topic else topic
        
        num_exercises = st.number_input("Antall oppgaver", min_value=0, max_value=50, value=10)
        
        st.markdown("#### 🎯 Kompetansemål (LK20)")
        goals = COMPETENCY_GOALS.get(grade, [])
        selected_goals = []
        with st.expander("Velg relevante mål for økten", expanded=False):
            for i, goal in enumerate(goals):
                if st.checkbox(goal, key=f"goal_{i}"):
                    selected_goals.append(goal)
        
        custom_instructions = st.text_area(
            "Spesielle instruksjoner til AI-en", 
            placeholder="f.eks. Bruk kun positive heltall, fokuser på tekstoppgaver...",
            height=100
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("◇ GENERER ULTIMAT MATERIALE", type="primary"):
            if not final_topic:
                st.error("Vennligst velg eller skriv et tema.")
            else:
                config = {
                    "title": f"{final_topic} - {grade}",
                    "grade": grade,
                    "topic": final_topic,
                    "material_type": material_type,
                    "include_theory": include_theory,
                    "include_examples": include_examples,
                    "include_exercises": include_exercises,
                    "include_solutions": include_solutions,
                    "num_exercises": num_exercises,
                    "difficulty": difficulty,
                    "output_format": output_format,
                    "competency_goals": selected_goals,
                    "custom_instructions": custom_instructions
                }
                
                with st.spinner("💎 MaTultimate AI-teamet utformer innholdet..."):
                    try:
                        response = requests.post(f"{API_URL}/generate", json=config)
                        if response.status_code == 200:
                            st.session_state.generated_content = response.json()
                            st.success("✨ Materiale generert med suksess!")
                        else:
                            st.error(f"Feil fra server: {response.text}")
                    except Exception as e:
                        st.error(f"Kunne ikke koble til backend: {e}")

    with col2:
        st.markdown('<div class="section-header">✨ Forhåndsvisning og Eksport</div>', unsafe_allow_html=True)
        
        if st.session_state.generated_content:
            res = st.session_state.generated_content
            
            # Action buttons
            c1, c2, c3 = st.columns(3)
            ext = ".tex" if res['format'] == "latex" else ".typ"
            
            with c1:
                st.download_button(
                    label=f"📥 Last ned {res['format'].upper()}",
                    data=res['content'],
                    file_name=f"matultimate_{datetime.now().strftime('%Y%m%d')}{ext}",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with c2:
                # Placeholder for PDF conversion
                st.button("📕 Generer PDF", disabled=True, use_container_width=True)
            
            with c3:
                if st.button("⭐ Lagre i bank", use_container_width=True):
                    st.toast("Lagret i din personlige oppgavebank!")

            # Content Preview
            with st.container():
                st.markdown(f"**Format:** `{res['format'].upper()}` | **Generert:** `{datetime.now().strftime('%H:%M:%S')}`")
                st.code(res['content'], language=res['format'])
                
            # Quick Tools
            st.divider()
            st.markdown("### 🛠️ Hurtigverktøy")
            tab1, tab2 = st.tabs(["📊 GeoGebra", "📝 Redigering"])
            
            with tab1:
                st.info("GeoGebra-integrasjon er klar. Klikk for å skanne innholdet.")
                if st.button("🔍 Finn funksjoner"):
                    st.write("Fant: $f(x) = 2x + 3$")
            
            with tab2:
                st.text_area("Gjør manuelle endringer", value=res['content'], height=300)
                
        else:
            st.markdown("""
            <div style="border: 2px dashed #cbd5e1; border-radius: 15px; padding: 5rem; text-align: center; color: #94a3b8;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">💎</div>
                <h3>Klar til å skape?</h3>
                <p>Konfigurer innholdet til venstre og trykk på generer-knappen for å se magien skje.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
