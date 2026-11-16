"""Ponto de entrada do dashboard.

Rodar a partir da raiz do projeto:
    streamlit run app/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Enchentes POA — INCT SiMAI",
    page_icon="🌊",
    layout="wide",
)

paginas = [
    st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
    st.Page("paginas/simulacao_inct.py", title="Simulação do INCT", icon="🌊"),
    st.Page("paginas/bases_equipe.py", title="Bases da equipe", icon="📊"),
]

st.navigation(paginas, position="top").run()
