"""Leitura dos dados já processados (saída dos scripts em scripts/)."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
PROCESSADOS = RAIZ / "dados" / "processados"
GEOJSON_BAIRROS = PROCESSADOS / "geo" / "bairros_poa.geojson"

NIVEL_MIN, NIVEL_MAX, NIVEL_PASSO = 3.0, 10.0, 0.1
NIVEL_RECORDE_2024 = 5.35
COTA_INUNDACAO = 3.0


@st.cache_data
def carregar_inct() -> pd.DataFrame:
    """INCT limpo, formato longo: uma linha por (nivel_m, bairro)."""
    df = pd.read_json(PROCESSADOS / "INCT" / "inct_limpo.json")
    df["nivel_m"] = df["nivel_m"].round(1)
    return df


def recorte_nivel(df: pd.DataFrame, nivel: float) -> pd.DataFrame:
    """Linhas dos 94 bairros em um nível."""
    return df[df["nivel_m"] == round(nivel, 1)]


@st.cache_data
def serie_cidade(df: pd.DataFrame) -> pd.DataFrame:
    """População e prédios afetados na cidade inteira, por nível."""
    return (
        df.groupby("nivel_m", as_index=False)
        .agg(pessoas=("affected_population", "sum"), predios=("affected_buildings", "sum"))
        .sort_values("nivel_m")
    )


@st.cache_data
def carregar_geojson_bairros() -> dict | None:
    """Malha dos bairros (gerada por scripts/malha_bairros.py). None se não existir."""
    if not GEOJSON_BAIRROS.exists():
        return None
    with open(GEOJSON_BAIRROS, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def carregar_bairros_ibge() -> pd.DataFrame:
    """Ligação bairros INCT x IBGE, com população e renda."""
    return pd.read_csv(PROCESSADOS / "IBGE" / "bairros_poa.csv")


@st.cache_data
def carregar_zenodo() -> pd.DataFrame:
    """Impacto da enchente de maio/2024 por município (RH Guaíba)."""
    return pd.read_csv(PROCESSADOS / "zenodo" / "analise_ada_rhguaiba_municipios.csv")
