import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from src.models.core import MaterialConfig
from src.agents.core_agents import MaTultimateAgents
from src.services.orchestrator import MaTultimateOrchestrator
from src.tools.storage import init_db, save_to_history, get_history, add_to_exercise_bank
from src.tools.geogebra import get_geogebra_embed_html, extract_functions_from_content, GRAPH_TEMPLATES
from src.tools.word_exporter import latex_to_word, is_word_export_available
from src.tools.pptx_exporter import latex_to_pptx, is_pptx_available

# Import curriculum data for UI
from MateMaTeX.src.curriculum import TOPIC_LIBRARY, COMPETENCY_GOALS

load_dotenv()

def initialize_session_state():
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

def main():
    init_db()
    st.set_page_config(
        page_title="MaTultimate", 
        page_icon="💎", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    # Custom CSS for a modern look
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
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .config-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("💎 MaTultimate")
    st.markdown("---")
    
    with st.sidebar:
        st.header("⚙️ Konfigurasjon")
        
        grade = st.selectbox(
            "Klassetrinn", 
            options=list(TOPIC_LIBRARY.keys()),
            index=2 # Default to 8. trinn
        )
        
        material_type = st.selectbox(
            "Type materiale", 
            options=["arbeidsark", "kapittel", "prøve", "lekseark"],
            format_func=lambda x: x.capitalize()
        )
        
        output_format = st.radio(
            "Eksportformat", 
            options=["latex", "typst"],
            format_func=lambda x: "LaTeX (.tex)" if x == "latex" else "Typst (.typ)"
        )
        
        difficulty = st.select_slider(
            "Vanskelighetsgrad",
            options=["Lett", "Middels", "Vanskelig"],
            value="Middels"
        )
        
        st.markdown("---")
        st.write("### 🛠️ Innhold")
        include_theory = st.checkbox("Teori", value=True)
        include_examples = st.checkbox("Eksempler", value=True)
        include_exercises = st.checkbox("Oppgaver", value=True)
        include_solutions = st.checkbox("Løsningsforslag", value=True)
        
        st.markdown("---")
        st.write("### 📜 Historikk")
        history = get_history(limit=5)
        for item in history:
            if st.button(f"📄 {item['title']}", key=f"hist_{item['id']}"):
                st.session_state.generated_content = {
                    "content": item["content"],
                    "format": item["format"],
                    "timestamp": item["timestamp"],
                    "config": item["config"]
                }
                st.rerun()
        
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.write("### 📚 Tema og Mål")
        
        # Get topics for selected grade
        grade_topics = TOPIC_LIBRARY.get(grade, {})
        categories = list(grade_topics.keys())
        
        selected_category = st.selectbox("Kategori", options=categories)
        topics = grade_topics.get(selected_category, [])
        
        topic = st.selectbox("Velg tema", options=topics)
        
        custom_topic = st.text_input("Eller skriv eget tema", placeholder="f.eks. Trigonometri i hverdagen")
        final_topic = custom_topic if custom_topic else topic
        
        num_exercises = st.number_input("Antall oppgaver", min_value=0, max_value=50, value=10)
        
        # Competency goals
        st.write("#### 🎯 Kompetansemål (LK20)")
        goals = COMPETENCY_GOALS.get(grade, [])
        selected_goals = []
        for i, goal in enumerate(goals):
            if st.checkbox(goal, key=f"goal_{i}"):
                selected_goals.append(goal)
        
        custom_instructions = st.text_area("Tilleggsinstruksjoner", placeholder="f.eks. Bruk kun positive heltall i oppgavene.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("◇ Generer MaTultimate Materiale", type="primary"):
            if not final_topic:
                st.error("Vennligst velg eller skriv et tema.")
            else:
                config = MaterialConfig(
                    title=f"{final_topic} - {grade}",
                    grade=grade,
                    topic=final_topic,
                    material_type=material_type,
                    include_theory=include_theory,
                    include_examples=include_examples,
                    include_exercises=include_exercises,
                    include_solutions=include_solutions,
                    num_exercises=num_exercises,
                    difficulty=difficulty,
                    output_format=output_format,
                    competency_goals=selected_goals,
                    custom_instructions=custom_instructions
                )
                
                orchestrator = MaTultimateOrchestrator()
                
                with st.spinner("💎 MaTultimate AI-teamet jobber..."):
                    try:
                        result = orchestrator.generate_material(config)
                        st.session_state.generated_content = result
                        
                        # Save to history
                        save_to_history(
                            title=config.title,
                            grade=config.grade,
                            topic=config.topic,
                            material_type=config.material_type,
                            content=result["content"],
                            output_format=result["format"],
                            config=result["config"]
                        )
                        
                        st.success("Materiale generert!")
                    except Exception as e:
                        st.error(f"En feil oppstod: {e}")
    
    with col2:
        st.write("### ✨ Forhåndsvisning")
        if st.session_state.generated_content:
            res = st.session_state.generated_content
            st.markdown(f"**Format:** {res['format'].upper()}")
            st.markdown(f"**Generert:** {res['timestamp']}")
            
            with st.expander("Se kildekode", expanded=True):
                st.code(res['content'], language=res['format'])
            
            # Download buttons
            ext = ".tex" if res['format'] == "latex" else ".typ"
            st.download_button(
                label=f"Last ned {res['format'].upper()}",
                data=res['content'],
                file_name=f"matultimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}",
                mime="text/plain"
            )
            
            # Export options (only for LaTeX for now)
            if res['format'] == 'latex':
                col_exp1, col_exp2 = st.columns(2)
                with col_exp1:
                    if is_word_export_available():
                        if st.button("📘 Eksporter til Word"):
                            with st.spinner("Konverterer..."):
                                path = f"output/matultimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                                word_path = latex_to_word(res['content'], path)
                                if word_path:
                                    with open(word_path, "rb") as f:
                                        st.download_button("⬇️ Last ned Word", f, file_name=os.path.basename(word_path))
                    else:
                        st.button("📘 Word (ikke inst.)", disabled=True)
                
                with col_exp2:
                    if is_pptx_available():
                        if st.button("📽️ Eksporter til PPTX"):
                            with st.spinner("Konverterer..."):
                                path = f"output/matultimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
                                pptx_path = latex_to_pptx(res['content'], path)
                                if pptx_path:
                                    with open(pptx_path, "rb") as f:
                                        st.download_button("⬇️ Last ned PPTX", f, file_name=os.path.basename(pptx_path))
                    else:
                        st.button("📽️ PPTX (ikke inst.)", disabled=True)
            
            st.markdown("---")
            st.write("### 📊 GeoGebra Integrasjon")
            if st.button("🔍 Finn funksjoner i innholdet"):
                funcs = extract_functions_from_content(res['content'])
                if funcs:
                    st.session_state.ggb_commands = funcs
                    st.success(f"Fant {len(funcs)} funksjoner!")
                else:
                    st.warning("Fant ingen funksjoner i innholdet.")
            
            # Template selector
            selected_tmpl = st.selectbox("Eller velg en mal", options=["Ingen"] + list(GRAPH_TEMPLATES.keys()))
            if selected_tmpl != "Ingen":
                st.session_state.ggb_commands = GRAPH_TEMPLATES[selected_tmpl]["commands"]
            
            if "ggb_commands" in st.session_state:
                st.write("**Interaktiv graf:**")
                html = get_geogebra_embed_html(st.session_state.ggb_commands)
                st.components.v1.html(html, height=450)
            
            st.markdown("---")
            st.write("### 🏦 Lagre til oppgavebank")
            if st.button("💾 Ekstraher og lagre oppgaver"):
                # Simple extraction logic for now
                content = res['content']
                # In a real scenario, we'd use a more robust parser
                add_to_exercise_bank(
                    title=f"Oppgaver fra {res['config']['topic']}",
                    topic=res['config']['topic'],
                    grade=res['config']['grade'],
                    content=content,
                    solution="Se kildekode",
                    difficulty=res['config']['difficulty']
                )
                st.success("Innhold lagret i oppgavebanken!")
        else:
            st.info("Konfigurer og trykk på 'Generer' for å se innholdet her.")

if __name__ == "__main__":
    main()
