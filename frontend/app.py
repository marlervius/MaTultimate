import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Vi importerer curriculum data
from src.curriculum import TOPIC_LIBRARY, COMPETENCY_GOALS

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="MaTultimate", page_icon="💎", layout="wide")

st.title("💎 MaTultimate")

with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    grade = st.selectbox("Klassetrinn", options=list(TOPIC_LIBRARY.keys()), index=2)
    material_type = st.selectbox("Type materiale", options=["arbeidsark", "kapittel", "prøve", "lekseark"])
    output_format = st.radio("Eksportformat", options=["latex", "typst"])
    
if st.button("◇ Generer Materiale", type="primary"):
    config = {
        "title": f"Generert materiale - {grade}",
        "grade": grade,
        "topic": "Brøk", # Forenklet for demo
        "material_type": material_type,
        "output_format": output_format,
        "num_exercises": 10
    }
    
    with st.spinner("💎 Kobler til backend..."):
        try:
            response = requests.post(f"{API_URL}/generate", json=config)
            if response.status_code == 200:
                res = response.json()
                st.success("Generert!")
                st.code(res['content'], language=res['format'])
            else:
                st.error(f"Feil fra API: {response.text}")
        except Exception as e:
            st.error(f"Kunne ikke koble til backend: {e}")
