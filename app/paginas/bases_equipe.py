"""Tela 2 — Bases levantadas pela equipe.

Cruza a simulação do INCT com duas bases externas:
- IBGE, Censo 2022: renda média por bairro (baixada por scripts/limpeza_ibge.py);
- Zenodo, ADA RH Guaíba v0.4: impacto observado da enchente de maio/2024 por município.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.dados import (
    carregar_bairros_ibge,
    carregar_inct,
    carregar_zenodo,
    recorte_nivel,
)
from utils.estilo import (
    AZUL,
    BORDA,
    CINZA,
    CORAL,
    PLOTLY_CONFIG,
    aplicar_estilo,
    card_titulo,
    estilo_plotly,
    fmt_int,
    fmt_m,
    fmt_pct,
    fmt_reais,
    icone,
)

COD_POA = 4314902
CORES_FAIXA = ["#0A3D62", "#2F7FBF", "#6BAED6", "#A9CBE6"]
FONTES = [
    {
        "nome": "INCT SiMAI",
        "desc": "Simulação de cheias por bairro e nível do Guaíba (base da Tela 1 e do cruzamento por bairro).",
        "tipo": "JSON FORNECIDO",
        "cor": CINZA,
        "link": "http://vhlab.com.br/INCT/floods/",
        "coleta": "08/11/2026",
    },
    {
        "nome": "IBGE · Censo 2022",
        "desc": "Agregados por setor censitário e renda por área de ponderação (Tab. 8.3), ligados aos 94 bairros.",
        "tipo": "DOWNLOAD AUTOMATIZADO",
        "cor": AZUL,
        "link": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/",
        "coleta": "08/11/2026",
    },
    {
        "nome": "Zenodo · ADA RH Guaíba v0.4",
        "desc": "Impacto observado da enchente de maio/2024 em 139 municípios da Região Hidrográfica do Guaíba.",
        "tipo": "DOWNLOAD DO CSV",
        "cor": AZUL,
        "link": "https://zenodo.org/records/11177244",
        "coleta": "09/11/2026",
    },
]

aplicar_estilo()

inct = carregar_inct()
ibge = carregar_bairros_ibge()
zenodo = carregar_zenodo()
niveis = sorted(inct["nivel_m"].unique())

# faixas de renda (quartis dos 94 bairros)
ibge = ibge.copy()
ibge["faixa_n"] = pd.qcut(ibge["renda_media_total"], 4, labels=False)
limites = ibge.groupby("faixa_n")["renda_media_total"].agg(["min", "max"])
ROTULOS = ["Q1", "Q2", "Q3", "Q4"]
FAIXA_RS = [
    f"até {fmt_reais(limites.loc[0, 'max'])}",
    f"{fmt_reais(limites.loc[1, 'min'])} a {fmt_reais(limites.loc[1, 'max'])}",
    f"{fmt_reais(limites.loc[2, 'min'])} a {fmt_reais(limites.loc[2, 'max'])}",
    f"acima de {fmt_reais(limites.loc[3, 'min'])}",
]
ibge["faixa"] = ibge["faixa_n"].map(dict(enumerate(ROTULOS)))

# ---------- cabeçalho ----------
st.html(
    '<div class="eyebrow">Bases externas · IBGE Censo 2022 · Zenodo ADA RH Guaíba</div>'
    '<div class="titulo">O que as outras bases mostram</div>'
    '<div class="sub">Bases levantadas pela equipe na Fase 1, cruzadas com a simulação do INCT '
    "por bairro, pelo nível do Guaíba e pela enchente de maio de 2024.</div>"
)

# ---------- filtros ----------
nivel_padrao = round(st.session_state.get("nivel", 5.3), 1)
with st.container(key="card_filtros"):
    st.html(f'<div class="filtros-t">{icone("filtro", AZUL, 18)}Filtros</div>')
    c1, c2, c3 = st.columns([1, 1, 1.4], gap="medium")
    nivel = c1.selectbox(
        "Nível do Guaíba", niveis, index=niveis.index(nivel_padrao), format_func=fmt_m,
        help="Nível usado no cruzamento com os bairros (mesma escala da Tela 1).",
    )
    top_n = c2.selectbox(
        "Municípios (Zenodo)", [5, 6, 10, 15, 20], index=1,
        format_func=lambda n: f"Top {n} por pessoas afetadas",
    )
    faixas = c3.multiselect(
        "Faixa de renda (IBGE) · Q1 = menor", ROTULOS, default=ROTULOS,
        help="Quartis da renda média dos 94 bairros: " + "; ".join(
            f"{r} {v}" for r, v in zip(ROTULOS, FAIXA_RS)),
    )

# ---------- renda × exposição + simulação × realidade ----------
col_disp, col_cmp = st.columns([1.55, 1], gap="medium")

cruz = recorte_nivel(inct, nivel).merge(ibge, left_on="bairro", right_on="bairro_inct", how="inner")
sel = cruz[cruz["faixa"].isin(faixas)]

with col_disp, st.container(key="card_dispersao"):
    if sel.empty:
        st.html(card_titulo("Os bairros mais expostos são os de menor renda?"))
        st.info("Selecione ao menos uma faixa de renda.")
    else:
        por_faixa = cruz.groupby("faixa_n").agg(afet=("affected_population", "sum"), pop=("population", "sum"))
        taxa = por_faixa["afet"] / por_faixa["pop"]
        if taxa.iloc[0] == taxa.max() and taxa.iloc[0] > 0:
            resposta = "Neste nível, sim: a faixa de menor renda tem a maior parcela da população afetada."
        elif taxa.max() == 0:
            resposta = "Neste nível, nenhum bairro tem população afetada."
        else:
            resposta = (
                f"Neste nível, não: a maior parcela afetada está na faixa {ROTULOS[int(taxa.idxmax())]}, "
                f"e a de menor renda fica em {fmt_pct(taxa.iloc[0])}."
            )
        st.html(card_titulo(
            "Os bairros mais expostos são os de menor renda?",
            f"Cada ponto é um bairro · renda média (IBGE) × % de prédios afetados a {fmt_m(nivel)} (INCT). "
            f"<b>{resposta}</b>",
        ))
        fig = go.Figure()
        for i, rot in enumerate(ROTULOS):
            parte = sel[sel["faixa"] == rot]
            if parte.empty:
                continue
            fig.add_trace(go.Scatter(
                x=parte["renda_media_total"], y=parte["percentage"], mode="markers", name=rot,
                marker=dict(size=11, color=CORES_FAIXA[i], opacity=0.85, line=dict(color="#FFFFFF", width=1.5)),
                customdata=parte[["bairro", "affected_population"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Renda média: R$ %{x:,.0f}<br>"
                "%{y}% dos prédios · %{customdata[1]:,.0f} pessoas<extra></extra>",
            ))
        if len(sel) >= 3 and sel["percentage"].nunique() > 1:
            a, b = np.polyfit(sel["renda_media_total"], sel["percentage"], 1)
            xs = np.array([sel["renda_media_total"].min(), sel["renda_media_total"].max()])
            fig.add_trace(go.Scatter(
                x=xs, y=a * xs + b, mode="lines", hoverinfo="skip", name="tendência",
                line=dict(color=CORAL, width=2, dash="dash"),
            ))
        fig.update_xaxes(tickprefix="R$ ", tickformat=",.0f", showgrid=False, title=None)
        fig.update_yaxes(range=[-4, 104], ticksuffix="%", gridcolor=BORDA, griddash="dot", title=None)
        estilo_plotly(fig, 440)
        st.plotly_chart(fig, config=PLOTLY_CONFIG, key="dispersao")
        st.html('<div class="faixas">' + "".join(
            f'<div><span><i style="background:{CORES_FAIXA[i]}"></i>{rot} · {FAIXA_RS[i]}</span>'
            f"<b>{fmt_pct(taxa.get(i, 0))}</b></div>"
            for i, rot in enumerate(ROTULOS)
        ) + "</div>"
            '<div class="nota">Parcela da população de cada faixa de renda que fica afetada neste nível.</div>')

poa = zenodo[zenodo["cd_mun"] == COD_POA].iloc[0]
observado = poa["pessoas_afetadas"]
serie = inct.groupby("nivel_m")["affected_population"].sum()
sim_baixo, sim_alto = serie.loc[5.3], serie.loc[5.4]
escala = max(observado, sim_alto) * 1.05

with col_cmp:
    barras = "".join(
        f'<div><div class="cmp-l">{rot}<b>{fmt_int(v)}</b></div>'
        f'<div class="cmp-bar"><span style="width:{100 * v / escala:.1f}%;background:{cor}"></span></div></div>'
        for rot, v, cor in [
            ("Observado · Zenodo ADA, mai/2024", observado, "#9AD0F5"),
            ("Simulado · INCT a 5,3 m", sim_baixo, "#4FA3DB"),
            ("Simulado · INCT a 5,4 m", sim_alto, "#2F7FBF"),
        ]
    )
    st.html(
        '<div class="cmp"><div><div class="cmp-e">SIMULAÇÃO × REALIDADE</div>'
        '<div class="cmp-t">A simulação perto de 5,35 m bate com maio de 2024?</div>'
        '<div class="cmp-s">Pessoas afetadas em Porto Alegre</div></div>'
        f"{barras}"
        f'<div class="cmp-d"><b>{fmt_pct(sim_baixo / observado - 1).replace("-", "−")}</b>'
        f"<span>A 5,3 m a simulação fica {fmt_int(observado - sim_baixo)} pessoas abaixo do observado "
        f"(a 5,4 m, {fmt_pct(sim_alto / observado - 1).replace('-', '−')}). O recorde foi "
        "5,35 m e o INCT só tem passos de 0,1 m.</span></div></div>"
    )

# ---------- municípios + Porto Alegre ----------
col_mun, col_poa = st.columns([1.55, 1], gap="medium")

with col_mun, st.container(key="card_municipios"):
    top = zenodo.nlargest(top_n, "pessoas_afetadas")
    st.html(card_titulo(
        "Municípios com mais pessoas afetadas em maio/2024",
        f"Pessoas afetadas e % da população · RH Guaíba ({len(zenodo)} municípios) · fonte: Zenodo ADA v0.4",
    ))
    fig = go.Figure(go.Bar(
        x=top["pessoas_afetadas"], y=top["nm_mun"], orientation="h",
        marker_color=[CORAL if c == COD_POA else AZUL for c in top["cd_mun"]],
        text=[f"{fmt_int(v)} · {fmt_pct(p / 100)}" for v, p in zip(top["pessoas_afetadas"], top["pessoas_pct"])],
        textposition="outside", cliponaxis=False,
        textfont=dict(family="IBM Plex Mono, monospace", size=12),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} pessoas afetadas<extra></extra>",
    ))
    fig.update_layout(barcornerradius=6, bargap=0.4)
    fig.update_xaxes(visible=False, range=[0, top["pessoas_afetadas"].max() * 1.45])
    fig.update_yaxes(autorange="reversed", ticksuffix="  ", showgrid=False)
    estilo_plotly(fig, 52 * len(top) + 40)
    st.plotly_chart(fig, config=PLOTLY_CONFIG, key="municipios")

with col_poa, st.container(key="card_poa"):
    st.html(
        card_titulo("Porto Alegre em 2024", "O que a enchente atingiu na capital")
        + '<div class="mini">'
        + "".join(f"<div><span>{r}</span><b>{v}</b></div>" for r, v in [
            ("DOMICÍLIOS", fmt_int(poa["domicilios_afetados"])),
            ("VIAS", f"{fmt_int(poa['vias_diretamente_afetadas_km'])} km"),
            ("ESCOLAS", fmt_int(poa["estabelecim_ensino_afetados_diretamente"])),
            ("UNID. DE SAÚDE", fmt_int(poa["estabelecim_saude_afetados_diretamente"])),
        ])
        + "</div>"
        + f'<div class="nota">{fmt_int(observado)} pessoas afetadas ({fmt_pct(poa["pessoas_pct"] / 100)} da '
        "população). Estabelecimentos de ensino e de saúde atingidos diretamente. "
        "Fonte: Zenodo ADA RH Guaíba v0.4.</div>"
    )

# ---------- fontes ----------
st.html(
    '<div class="secao-t">Fontes e data de coleta</div>'
    '<div class="card-s">Cada visualização indica a base usada. O IBGE é baixado por código '
    "(<code>scripts/limpeza_ibge.py</code>).</div>"
)
for coluna, f in zip(st.columns(3, gap="medium"), FONTES):
    coluna.html(
        f'<div class="fonte"><span class="tipo" style="color:{f["cor"]};background:{f["cor"]}1A">{f["tipo"]}</span>'
        f'<div class="nome">{f["nome"]}</div><div class="desc">{f["desc"]}</div>'
        f'<a href="{f["link"]}" target="_blank">{f["link"].split("://")[1].rstrip("/")} ↗</a>'
        f'<div class="data">Coletado em {f["coleta"]}</div></div>'
    )
