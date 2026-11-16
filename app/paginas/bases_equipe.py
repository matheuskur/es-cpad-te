"""Tela 2 — Bases levantadas pela equipe (IBGE e Zenodo)."""
import streamlit as st

from utils.dados import carregar_bairros_ibge, carregar_zenodo

st.title("Bases levantadas pela equipe")

ibge = carregar_bairros_ibge()
zenodo = carregar_zenodo()

# TODO: >= 3 visualizações e >= 1 filtro interativo
# TODO: visualização ligando a base externa à Tela 1 (bairro / nível / 2024)
# TODO: fonte de cada dado com link e data de coleta
st.info("Tela em construção.")
