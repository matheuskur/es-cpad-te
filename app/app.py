"""Ponto de entrada do dashboard.

Rodar a partir da raiz do projeto:
    streamlit run app/app.py
"""
import streamlit as st

from utils.estilo import aplicar_estilo

st.set_page_config(
    page_title="Enchentes POA — INCT SiMAI",
    page_icon="🌊",
    layout="wide",
)

aplicar_estilo()

paginas = [
    st.Page("paginas/inicio.py", title="Início", default=True),
    st.Page("paginas/simulacao_inct.py", title="Simulação do INCT"),
    st.Page("paginas/bases_equipe.py", title="Bases da equipe"),
]

st.navigation(paginas, position="top").run()
