"""Tela 2 — Bases levantadas pela equipe.

Visualmente alinhada à Tela 1 (hero, KPIs, cards expansíveis e mapa interativo).
Cruza a simulação do INCT com duas bases externas:
- IBGE, Censo 2022: renda média por bairro de Porto Alegre;
- Zenodo, ADA RH Guaíba v0.4: impacto observado da enchente de maio/2024 por município.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.dados import (
    carregar_bairros_ibge,
    carregar_geojson_bairros,
    carregar_inct,
    carregar_zenodo,
    recorte_nivel,
)
from utils.estilo import (
    AMBAR,
    AZUL,
    BORDA,
    CINZA,
    CORAL,
    FAIXAS,
    PLOTLY_CONFIG,
    TINTA,
    aplicar_estilo,
    card_titulo,
    cor_faixa,
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
ibge = carregar_bairros_ibge().copy()
zenodo = carregar_zenodo().copy()

# ---------- colunas derivadas (Zenodo) ----------
zenodo["area_afetada_km2"] = zenodo["area_diretamente_afetada_municipio_m2"] / 1e6
zenodo["area_municipio_km2"] = zenodo["area_municipio_m2"] / 1e6
zenodo["area_urbana_afetada_km2"] = zenodo["area_diretamente_afetada_urbana_m2"] / 1e6
zenodo["area_urbana_km2"] = zenodo["area_urbana_m2"] / 1e6
_rural_afetada_m2 = (
    zenodo["area_diretamente_afetada_municipio_m2"] - zenodo["area_diretamente_afetada_urbana_m2"]
).clip(lower=0)
zenodo["area_rural_afetada_km2"] = _rural_afetada_m2 / 1e6
zenodo["area_rural_km2"] = zenodo["area_nao_urbana_m2"] / 1e6
zenodo["area_diretamente_afetada_rural_pct"] = np.where(
    zenodo["area_nao_urbana_m2"] > 0,
    _rural_afetada_m2 / zenodo["area_nao_urbana_m2"] * 100,
    0.0,
)
zenodo["saude_por_100k"] = np.where(
    zenodo["pessoas_2022"] > 0,
    zenodo["estabelecim_saude_afetados_diretamente"] / zenodo["pessoas_2022"] * 100_000,
    0.0,
)
zenodo["ensino_por_100k"] = np.where(
    zenodo["pessoas_2022"] > 0,
    zenodo["estabelecim_ensino_afetados_diretamente"] / zenodo["pessoas_2022"] * 100_000,
    0.0,
)

# ---------- faixas de renda dos 94 bairros (IBGE) ----------
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

# ---------- estado de expansão e mapa ----------
for k_exp in (
    "exp_area_pct",
    "exp_area_pop",
    "exp_saude",
    "exp_ensino",
    "exp_mapa_renda",
    "exp_dispersao",
):
    if k_exp not in st.session_state:
        st.session_state[k_exp] = False

if "mapa_renda_zoom" not in st.session_state:
    st.session_state["mapa_renda_zoom"] = 9.4
if "mapa_renda_inclinado" not in st.session_state:
    st.session_state["mapa_renda_inclinado"] = False

# ---------- aviso de limitações (igual à Tela 1) ----------
st.html(
    f'<div class="aviso">{icone("alerta", "#8A5A12")}<div><b>Sobre as bases externas</b>'
    "Os indicadores municipais vêm da análise da Área Diretamente Afetada (ADA) da cheia de maio/2024 na "
    "Região Hidrográfica do Guaíba (Zenodo v0.4). A renda média (IBGE Censo 2022, Tab. 8.3) é calculada por "
    "área de ponderação e ligada aos 94 bairros de Porto Alegre. Use o filtro de população mínima bruta "
    "para controlar distorções em taxas proporcionais de municípios pequenos.</div></div>"
)

# ---------- hero com filtro logarítmico de população (alinhado à Tela 1) ----------
nivel = 5.3
ESCALA_POP_LOG = [
    0,
    1_000,
    1_500,
    2_000,
    3_000,
    5_000,
    7_500,
    10_000,
    15_000,
    20_000,
    30_000,
    50_000,
    75_000,
    100_000,
    150_000,
    200_000,
    300_000,
    500_000,
    1_000_000,
]

with st.container(key="hero_t2"):
    hero_top_slot = st.empty()
    pop_min = int(
        st.select_slider(
            "População total mínima bruta",
            options=ESCALA_POP_LOG,
            value=0,
            key="t2_pop_min",
            format_func=lambda v: "0 (todos)" if v == 0 else f"{fmt_int(v)} hab.",
            label_visibility="collapsed",
        )
    )

    zen_f = zenodo[zenodo["pessoas_2022"] >= pop_min].copy()
    valor_hero = "Todos" if pop_min == 0 else f"≥ {fmt_int(pop_min)}"
    sufixo_hero = "" if pop_min == 0 else '<small style="font-size:24px;color:rgba(255,255,255,.55);margin-left:8px">hab.</small>'
    hero_top_slot.html(
        '<div class="hero-top"><div>'
        '<div class="hero-eyebrow">POPULAÇÃO TOTAL MÍNIMA BRUTA</div>'
        f'<div class="hero-valor-t2">{valor_hero}{sufixo_hero}</div>'
        f'<div class="hero-rel">{len(zen_f)} de {len(zenodo)} municípios da RH Guaíba · '
        f"Cota de referência (POA): {fmt_m(nivel)}</div></div>"
        '<div class="chips">'
        f'<span class="chip"><i style="background:{AMBAR}"></i>IBGE · Censo 2022 (Tab. 8.3)</span>'
        f'<span class="chip"><i style="background:{CORAL}"></i>Zenodo · Cheia mai/2024</span>'
        "</div></div>"
    )
    st.html(
        '<div class="hero-dica">Arraste para filtrar municípios por população total mínima.</div>'
    )

# ---------- indicadores KPI (3 cards, igual à Tela 1) ----------
pop_afetada_tot = float(zen_f["pessoas_afetadas"].sum())
pop_total_tot = float(zen_f["pessoas_2022"].sum())
area_afetada_tot = float(zen_f["area_afetada_km2"].sum())
area_total_tot = float(zen_f["area_municipio_km2"].sum())
area_urb_afetada_tot = float(zen_f["area_urbana_afetada_km2"].sum())
saude_tot = float(zen_f["estabelecim_saude_afetados_diretamente"].sum())
ensino_tot = float(zen_f["estabelecim_ensino_afetados_diretamente"].sum())
equip_tot = saude_tot + ensino_tot
equip_base = float(
    zenodo["estabelecim_saude_afetados_diretamente"].sum()
    + zenodo["estabelecim_ensino_afetados_diretamente"].sum()
)

frac_pop = pop_afetada_tot / pop_total_tot if pop_total_tot > 0 else 0.0
frac_area = area_afetada_tot / area_total_tot if area_total_tot > 0 else 0.0
frac_equip = equip_tot / equip_base if equip_base > 0 else 0.0

indicadores = [
    (
        "pessoas",
        "Pessoas afetadas (RH Guaíba)",
        fmt_int(pop_afetada_tot),
        min(frac_pop, 1.0),
        f"{fmt_pct(frac_pop)} dos {fmt_int(pop_total_tot)} moradores nos {len(zen_f)} municípios filtrados",
    ),
    (
        "area",
        "Área diretamente afetada",
        f"{fmt_int(area_afetada_tot)} km²",
        min(frac_area, 1.0),
        f"{fmt_pct(frac_area)} dos {fmt_int(area_total_tot)} km² totais · {fmt_int(area_urb_afetada_tot)} km² urbanos",
    ),
    (
        "saude",
        "Saúde e ensino atingidos",
        fmt_int(equip_tot),
        min(frac_equip, 1.0),
        f"{fmt_int(saude_tot)} unid. de saúde · {fmt_int(ensino_tot)} estabelecimentos de ensino",
    ),
]
for coluna, (ic, rotulo, valor, fracao, detalhe) in zip(st.columns(3, gap="medium"), indicadores):
    coluna.html(
        f'<div class="kpi"><div class="kpi-top"><span class="kpi-ic">{icone(ic)}</span>{rotulo}</div>'
        f'<div class="kpi-v">{valor}</div>'
        f'<div class="kpi-bar"><span style="width:{100 * fracao:.1f}%"></span></div>'
        f'<div class="kpi-d">{detalhe}</div></div>'
    )


# ---------- funções de figuras ----------
def criar_barras_pct_area(
    ordem: pd.DataFrame,
    col_pct: str,
    col_km2: str,
    col_km2_tot: str,
    altura_min: int = 260,
    fonte: int = 15,
    passo_barra: int = 34,
) -> go.Figure:
    valores = ordem[col_pct].round(1)
    custom = ordem[[col_km2, col_km2_tot, "pessoas_2022"]]
    fig = go.Figure(
        go.Bar(
            x=valores,
            y=ordem["nm_mun"],
            orientation="h",
            marker_color=[cor_faixa(p) for p in valores],
            text=[f"{p:.1f}%".replace(".", ",") for p in valores],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=fonte - 2, color=TINTA),
            cliponaxis=False,
            customdata=custom,
            hovertemplate=(
                "<b>%{y}</b><br>%{x:.1f}% de área afetada<br>"
                "%{customdata[0]:,.1f} km² de %{customdata[1]:,.1f} km²<br>"
                "População total: %{customdata[2]:,.0f}<extra></extra>"
            ),
        )
    )
    fig.update_layout(barcornerradius=6, bargap=0.42)
    max_x = max(float(valores.max()) * 1.18, 25.0) if not valores.empty else 100.0
    fig.update_xaxes(range=[0, min(max_x, 118.0)], visible=False)
    fig.update_yaxes(
        autorange="reversed",
        ticksuffix="  ",
        showgrid=False,
        tickfont=dict(family="IBM Plex Sans, sans-serif", size=fonte - 1, color=TINTA),
    )
    estilo_plotly(fig, max(altura_min, passo_barra * len(ordem) + 20))
    fig.update_layout(font=dict(size=fonte))
    return fig


def criar_dispersao_area_pop(df_mun: pd.DataFrame, modo: str, altura: int, fonte: int = 14) -> go.Figure:
    fig = go.Figure()
    pop_ref = max(float(df_mun["pessoas_2022"].max()), 1.0)
    tamanhos = 8 + 26 * np.sqrt(df_mun["pessoas_2022"] / pop_ref)

    if modo == "Absoluto":
        x_col, y_col = "area_afetada_km2", "pessoas_afetadas"
        x_title, y_title = "Área afetada (km²)", "População afetada (pessoas)"
        hover = (
            "<b>%{customdata[0]}</b><br>"
            "Área afetada: %{x:,.1f} km² (%{customdata[1]:.1f}%)<br>"
            "População afetada: %{y:,.0f} (%{customdata[2]:.1f}%)<br>"
            "População total: %{customdata[3]:,.0f}<extra></extra>"
        )
    else:
        x_col, y_col = "area_diretamente_afetada_municipio_pct", "pessoas_pct"
        x_title, y_title = "% da área do município afetada", "% da população afetada"
        hover = (
            "<b>%{customdata[0]}</b><br>"
            "Área afetada: %{x:.1f}% (%{customdata[4]:,.1f} km²)<br>"
            "População afetada: %{y:.1f}% (%{customdata[5]:,.0f} pessoas)<br>"
            "População total: %{customdata[3]:,.0f}<extra></extra>"
        )

    custom_cols = [
        "nm_mun",
        "area_diretamente_afetada_municipio_pct",
        "pessoas_pct",
        "pessoas_2022",
        "area_afetada_km2",
        "pessoas_afetadas",
    ]

    for eh_poa, nome_traco, cor in [(False, "Demais municípios", AZUL), (True, "Porto Alegre", CORAL)]:
        parte = df_mun[df_mun["cd_mun"] == COD_POA] if eh_poa else df_mun[df_mun["cd_mun"] != COD_POA]
        if parte.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=parte[x_col],
                y=parte[y_col],
                mode="markers",
                name=nome_traco,
                marker=dict(
                    size=tamanhos.loc[parte.index],
                    color=cor,
                    opacity=0.85 if not eh_poa else 0.95,
                    line=dict(color="#FFFFFF", width=1.5),
                ),
                customdata=parte[custom_cols],
                hovertemplate=hover,
            )
        )

    # Anotar os 4 municípios mais extremos para facilitar leitura
    destaques = pd.concat([df_mun.nlargest(3, y_col), df_mun.nlargest(2, x_col)]).drop_duplicates("cd_mun")
    for r in destaques.itertuples():
        fig.add_annotation(
            x=getattr(r, x_col),
            y=getattr(r, y_col),
            text=r.nm_mun,
            showarrow=False,
            yshift=14,
            font=dict(size=max(fonte - 3, 11), color=CORAL if r.cd_mun == COD_POA else TINTA),
        )

    if modo == "Absoluto":
        fig.update_xaxes(title=x_title, rangemode="tozero", gridcolor=BORDA, griddash="dot", tickformat=",.0f")
        fig.update_yaxes(title=y_title, rangemode="tozero", gridcolor=BORDA, griddash="dot", tickformat=",.0f")
    else:
        fig.update_xaxes(title=x_title, rangemode="tozero", ticksuffix="%", gridcolor=BORDA, griddash="dot")
        fig.update_yaxes(title=y_title, rangemode="tozero", ticksuffix="%", gridcolor=BORDA, griddash="dot")

    estilo_plotly(fig, altura)
    fig.update_layout(font=dict(size=fonte), margin=dict(l=0, r=12, t=12, b=0))
    return fig


def criar_barras_equipamentos(
    ordem: pd.DataFrame,
    col_valor: str,
    col_bruto: str,
    rotulo_unidade: str,
    eh_taxa: bool,
    altura_min: int = 260,
    fonte: int = 15,
    passo_barra: int = 34,
) -> go.Figure:
    valores = ordem[col_valor]
    textos = [f"{v:.1f}".replace(".", ",") if eh_taxa else fmt_int(v) for v in valores]
    custom = ordem[[col_bruto, "pessoas_2022"]]
    if eh_taxa:
        hover = (
            f"<b>%{{y}}</b><br>%{{x:.1f}} {rotulo_unidade} / 100 mil hab.<br>"
            "Total atingido: %{customdata[0]:,.0f}<br>"
            "População total: %{customdata[1]:,.0f}<extra></extra>"
        )
    else:
        hover = (
            f"<b>%{{y}}</b><br>%{{x:,.0f}} {rotulo_unidade} atingidos<br>"
            "População total: %{customdata[1]:,.0f}<extra></extra>"
        )

    fig = go.Figure(
        go.Bar(
            x=valores,
            y=ordem["nm_mun"],
            orientation="h",
            marker_color=[CORAL if c == COD_POA else AZUL for c in ordem["cd_mun"]],
            text=textos,
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=fonte - 2, color=TINTA),
            cliponaxis=False,
            customdata=custom,
            hovertemplate=hover,
        )
    )
    fig.update_layout(barcornerradius=6, bargap=0.42)
    max_x = float(valores.max()) * 1.24 if not valores.empty and float(valores.max()) > 0 else 10.0
    fig.update_xaxes(range=[0, max_x], visible=False)
    fig.update_yaxes(
        autorange="reversed",
        ticksuffix="  ",
        showgrid=False,
        tickfont=dict(family="IBM Plex Sans, sans-serif", size=fonte - 1, color=TINTA),
    )
    estilo_plotly(fig, max(altura_min, passo_barra * len(ordem) + 20))
    fig.update_layout(font=dict(size=fonte))
    return fig


def criar_mapa_bairros_renda(
    df_cruz: pd.DataFrame,
    malha: dict,
    zoom_atual: float,
    inclinado: bool,
    altura: int,
    fonte: int = 14,
) -> go.Figure:
    vmin = float(df_cruz["renda_media_total"].min())
    vmax = float(df_cruz["renda_media_total"].max())
    if vmax <= vmin:
        vmax = vmin + 1.0

    fig = px.choropleth_map(
        df_cruz,
        geojson=malha,
        locations="bairro",
        featureidkey="properties.bairro",
        color="renda_media_total",
        range_color=(vmin, vmax),
        color_continuous_scale=["#F7F2E7", "#DCE8C8", "#8EC5B6", "#2F7FBF", "#0A3D62"],
        map_style="carto-positron",
        center={"lat": -30.09, "lon": -51.17},
        zoom=zoom_atual,
        opacity=0.9,
        hover_name="bairro",
        hover_data={
            "bairro": False,
            "renda_media_total": ":,.0f",
            "faixa": True,
            "pct_pop": ":.1f",
            "affected_population": ":,.0f",
        },
        labels={
            "renda_media_total": "Renda média (R$)",
            "faixa": "Faixa IBGE",
            "pct_pop": "% população afetada (5,3 m)",
            "affected_population": "Pessoas afetadas (5,3 m)",
        },
    )
    fig.update_traces(marker_line_color="#FFFFFF", marker_line_width=0.6)
    fig.update_layout(
        coloraxis_showscale=False,
        uirevision=f"renda-{zoom_atual}-{inclinado}",
        map=dict(pitch=45 if inclinado else 0, bearing=-15 if inclinado else 0),
    )
    estilo_plotly(fig, altura)
    fig.update_layout(font=dict(size=fonte))
    return fig


# ---------- LINHA 1: % de área afetada por cidade + Área afetada × População afetada ----------
exp_area_pct = st.session_state["exp_area_pct"]
exp_area_pop = st.session_state["exp_area_pop"]
if exp_area_pct or exp_area_pop:
    col_area_pct = st.container()
    col_area_pop = st.container()
else:
    col_area_pct, col_area_pop = st.columns([1.1, 1.1], gap="medium")

with col_area_pct, st.container(key="card_area_pct"):
    cab_esq, cab_exp = st.columns([12, 1], vertical_alignment="top")
    titulo_area_slot = cab_esq.empty()
    if cab_exp.button(
        "⤡" if exp_area_pct else "⤢",
        key="expandir_area_pct",
        help="Reduzir gráfico" if exp_area_pct else "Expandir gráfico",
        use_container_width=True,
    ):
        st.session_state["exp_area_pct"] = not exp_area_pct
        st.rerun()

    modo_area = (
        st.segmented_control(
            "Tipo de área",
            ["Área total", "Área urbana", "Área rural"],
            default="Área total",
            key="modo_area_pct",
            label_visibility="collapsed",
        )
        or "Área total"
    )

    if modo_area == "Área total":
        col_pct = "area_diretamente_afetada_municipio_pct"
        col_km2 = "area_afetada_km2"
        col_km2_tot = "area_municipio_km2"
        sub_area = "% da área total do município atingida"
    elif modo_area == "Área urbana":
        col_pct = "area_diretamente_afetada_urbana_pct"
        col_km2 = "area_urbana_afetada_km2"
        col_km2_tot = "area_urbana_km2"
        sub_area = "% da área urbana do município atingida"
    else:
        col_pct = "area_diretamente_afetada_rural_pct"
        col_km2 = "area_rural_afetada_km2"
        col_km2_tot = "area_rural_km2"
        sub_area = "% da área rural (não urbana) do município atingida"

    ordem_area = (
        zen_f[zen_f[col_pct] > 0]
        .sort_values([col_pct, col_km2], ascending=[False, False])
    )
    sub = f"{sub_area} · {len(ordem_area)} cidades (pop. ≥ {fmt_int(pop_min)})"
    legenda = "".join(f'<span><i style="background:{cor}"></i>{rot}</span>' for _, cor, rot in reversed(FAIXAS))
    titulo_area_slot.html(card_titulo("% de área afetada por cidade", sub))
    st.html(f'<div class="legenda" style="margin-top:0">{legenda}</div>')

    if ordem_area.empty:
        st.info("Nenhum município atende ao filtro de população mínima.")
    else:
        fig_area = criar_barras_pct_area(
            ordem_area,
            col_pct,
            col_km2,
            col_km2_tot,
            altura_min=600 if exp_area_pct else 260,
            fonte=18 if exp_area_pct else 15,
            passo_barra=38 if exp_area_pct else 34,
        )
        if exp_area_pct:
            st.plotly_chart(fig_area, config=PLOTLY_CONFIG, key="area_pct")
        else:
            with st.container(height=500, border=False):
                st.plotly_chart(fig_area, config=PLOTLY_CONFIG, key="area_pct")

with col_area_pop, st.container(key="card_area_pop"):
    cab_esq, cab_exp = st.columns([12, 1], vertical_alignment="top")
    titulo_ap_slot = cab_esq.empty()
    if cab_exp.button(
        "⤡" if exp_area_pop else "⤢",
        key="expandir_area_pop",
        help="Reduzir gráfico" if exp_area_pop else "Expandir gráfico",
        use_container_width=True,
    ):
        st.session_state["exp_area_pop"] = not exp_area_pop
        st.rerun()

    modo_ap = (
        st.segmented_control(
            "Escala área × população",
            ["Absoluto", "Percentual"],
            default="Absoluto",
            key="modo_area_pop",
            label_visibility="collapsed",
        )
        or "Absoluto"
    )
    sub_ap = (
        f"Área afetada (km²) × pessoas afetadas · tamanho = população total · {len(zen_f)} cidades"
        if modo_ap == "Absoluto"
        else f"% área afetada × % população afetada · tamanho = população total · {len(zen_f)} cidades"
    )
    legenda_ap = (
        f'<div class="legenda" style="margin-top:0">'
        f'<span><i style="background:{CORAL}"></i>Porto Alegre</span>'
        f'<span><i style="background:{AZUL}"></i>Demais municípios</span></div>'
    )
    titulo_ap_slot.html(card_titulo("Área afetada × população afetada", sub_ap))
    st.html(legenda_ap)

    if zen_f.empty:
        st.info("Nenhum município atende ao filtro de população mínima.")
    else:
        st.plotly_chart(
            criar_dispersao_area_pop(zen_f, modo_ap, 620 if exp_area_pop else 500, fonte=16 if exp_area_pop else 14),
            config=PLOTLY_CONFIG,
            key="area_pop",
        )

# ---------- LINHA 2: Estabelecimentos de saúde e ensino por população ----------
exp_saude = st.session_state["exp_saude"]
exp_ensino = st.session_state["exp_ensino"]
if exp_saude or exp_ensino:
    col_saude = st.container()
    col_ensino = st.container()
else:
    col_saude, col_ensino = st.columns(2, gap="medium")

with col_saude, st.container(key="card_saude"):
    cab_esq, cab_exp = st.columns([12, 1], vertical_alignment="top")
    titulo_saude_slot = cab_esq.empty()
    if cab_exp.button(
        "⤡" if exp_saude else "⤢",
        key="expandir_saude",
        help="Reduzir gráfico" if exp_saude else "Expandir gráfico",
        use_container_width=True,
    ):
        st.session_state["exp_saude"] = not exp_saude
        st.rerun()

    modo_saude = (
        st.segmented_control(
            "Métrica saúde",
            ["Por 100 mil hab.", "Total"],
            default="Por 100 mil hab.",
            key="modo_saude",
            label_visibility="collapsed",
        )
        or "Por 100 mil hab."
    )
    eh_taxa_saude = modo_saude == "Por 100 mil hab."
    col_val_s = "saude_por_100k" if eh_taxa_saude else "estabelecim_saude_afetados_diretamente"
    cols_ord_s = (
        ["saude_por_100k", "estabelecim_saude_afetados_diretamente"]
        if eh_taxa_saude
        else ["estabelecim_saude_afetados_diretamente", "pessoas_2022"]
    )
    ordem_saude = (
        zen_f[zen_f["estabelecim_saude_afetados_diretamente"] > 0]
        .sort_values(cols_ord_s, ascending=[False, False])
    )
    sub_s = (
        f"Unidades de saúde atingidas a cada 100 mil habitantes · {len(ordem_saude)} cidades"
        if eh_taxa_saude
        else f"Total de unidades de saúde atingidas diretamente · {len(ordem_saude)} cidades"
    )
    titulo_saude_slot.html(card_titulo("Estabelecimentos de saúde por população", sub_s))
    st.html(
        f'<div class="legenda" style="margin-top:0"><span><i style="background:{CORAL}"></i>Porto Alegre</span>'
        f'<span><i style="background:{AZUL}"></i>Demais municípios</span></div>'
    )

    if ordem_saude.empty:
        st.info("Nenhum município com estabelecimentos de saúde atingidos neste filtro.")
    else:
        fig_saude = criar_barras_equipamentos(
            ordem_saude,
            col_val_s,
            "estabelecim_saude_afetados_diretamente",
            "unid. de saúde",
            eh_taxa_saude,
            altura_min=600 if exp_saude else 260,
            fonte=18 if exp_saude else 15,
            passo_barra=38 if exp_saude else 34,
        )
        if exp_saude:
            st.plotly_chart(fig_saude, config=PLOTLY_CONFIG, key="saude")
        else:
            with st.container(height=480, border=False):
                st.plotly_chart(fig_saude, config=PLOTLY_CONFIG, key="saude")

with col_ensino, st.container(key="card_ensino"):
    cab_esq, cab_exp = st.columns([12, 1], vertical_alignment="top")
    titulo_ensino_slot = cab_esq.empty()
    if cab_exp.button(
        "⤡" if exp_ensino else "⤢",
        key="expandir_ensino",
        help="Reduzir gráfico" if exp_ensino else "Expandir gráfico",
        use_container_width=True,
    ):
        st.session_state["exp_ensino"] = not exp_ensino
        st.rerun()

    modo_ensino = (
        st.segmented_control(
            "Métrica ensino",
            ["Por 100 mil hab.", "Total"],
            default="Por 100 mil hab.",
            key="modo_ensino",
            label_visibility="collapsed",
        )
        or "Por 100 mil hab."
    )
    eh_taxa_ensino = modo_ensino == "Por 100 mil hab."
    col_val_e = "ensino_por_100k" if eh_taxa_ensino else "estabelecim_ensino_afetados_diretamente"
    cols_ord_e = (
        ["ensino_por_100k", "estabelecim_ensino_afetados_diretamente"]
        if eh_taxa_ensino
        else ["estabelecim_ensino_afetados_diretamente", "pessoas_2022"]
    )
    ordem_ensino = (
        zen_f[zen_f["estabelecim_ensino_afetados_diretamente"] > 0]
        .sort_values(cols_ord_e, ascending=[False, False])
    )
    sub_e = (
        f"Estabelecimentos de ensino atingidos a cada 100 mil habitantes · {len(ordem_ensino)} cidades"
        if eh_taxa_ensino
        else f"Total de estabelecimentos de ensino atingidos diretamente · {len(ordem_ensino)} cidades"
    )
    titulo_ensino_slot.html(card_titulo("Estabelecimentos de ensino por população", sub_e))
    st.html(
        f'<div class="legenda" style="margin-top:0"><span><i style="background:{CORAL}"></i>Porto Alegre</span>'
        f'<span><i style="background:{AZUL}"></i>Demais municípios</span></div>'
    )

    if ordem_ensino.empty:
        st.info("Nenhum município com estabelecimentos de ensino atingidos neste filtro.")
    else:
        fig_ensino = criar_barras_equipamentos(
            ordem_ensino,
            col_val_e,
            "estabelecim_ensino_afetados_diretamente",
            "estab. de ensino",
            eh_taxa_ensino,
            altura_min=600 if exp_ensino else 260,
            fonte=18 if exp_ensino else 15,
            passo_barra=38 if exp_ensino else 34,
        )
        if exp_ensino:
            st.plotly_chart(fig_ensino, config=PLOTLY_CONFIG, key="ensino")
        else:
            with st.container(height=480, border=False):
                st.plotly_chart(fig_ensino, config=PLOTLY_CONFIG, key="ensino")

# ---------- LINHA 3: Associado à Tela 1 — Mapa renda média por bairro ----------
cruz = recorte_nivel(inct, nivel).merge(ibge, left_on="bairro", right_on="bairro_inct", how="inner")
cruz["pct_pop"] = np.where(
    cruz["population"] > 0,
    cruz["affected_population"] / cruz["population"] * 100,
    0.0,
)
sel = cruz

with st.container(key="card_mapa_renda"):
    malha_bairros = carregar_geojson_bairros()
    exp_mapa_renda = st.session_state["exp_mapa_renda"]
    zoom_renda = st.session_state["mapa_renda_zoom"]
    inc_renda = st.session_state["mapa_renda_inclinado"]

    cab_titulo, cab_cor, cab_exp = st.columns([4, 3, 0.45], vertical_alignment="center")
    r_min = float(cruz["renda_media_total"].min())
    r_max = float(cruz["renda_media_total"].max())
    r_mid = (r_min + r_max) / 2
    barra_renda = (
        '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;min-width:260px">'
        '<div style="width:100%;height:10px;border-radius:999px;'
        'background:linear-gradient(90deg,#F7F2E7 0%,#DCE8C8 25%,#8EC5B6 50%,#2F7FBF 75%,#0A3D62 100%)"></div>'
        f'<div style="width:100%;display:flex;justify-content:space-between;font-family:\'IBM Plex Mono\',monospace;'
        f'font-size:12px;color:{CINZA}"><span>{fmt_reais(r_min)}</span><span>{fmt_reais(r_mid)}</span>'
        f"<span>{fmt_reais(r_max)}</span></div></div>"
    )
    sub_mapa_r = f"Cor = renda média per capita (IBGE) · passe o mouse para ver exposição a {fmt_m(nivel)}"

    with cab_titulo:
        st.html(card_titulo("Mapa de renda média por bairro", sub_mapa_r))
    with cab_cor:
        st.html(barra_renda)
    if cab_exp.button(
        "⤡" if exp_mapa_renda else "⤢",
        key="expandir_mapa_renda",
        help="Reduzir mapa" if exp_mapa_renda else "Expandir mapa",
        use_container_width=True,
        disabled=malha_bairros is None,
    ):
        st.session_state["exp_mapa_renda"] = not exp_mapa_renda
        st.rerun()

    if malha_bairros is None:
        st.html(
            f'<div class="mapa-vazio">Malha dos bairros não encontrada.<br>'
            "Gere com <code>python scripts/malha_bairros.py</code> para ver o mapa.</div>"
        )
    else:
        st.plotly_chart(
            criar_mapa_bairros_renda(
                sel,
                malha_bairros,
                zoom_renda,
                inc_renda,
                840 if exp_mapa_renda else 680,
                fonte=17 if exp_mapa_renda else 14,
            ),
            config=PLOTLY_CONFIG,
            key="mapa_renda_bairros",
        )
        with st.container(key="mapa_controles_renda"):
            if st.button("＋", key="zoom_mais_renda", help="Aproximar", use_container_width=True):
                st.session_state["mapa_renda_zoom"] = min(14.0, round(st.session_state["mapa_renda_zoom"] + 0.6, 1))
                st.rerun()
            if st.button("－", key="zoom_menos_renda", help="Afastar", use_container_width=True):
                st.session_state["mapa_renda_zoom"] = max(8.0, round(st.session_state["mapa_renda_zoom"] - 0.6, 1))
                st.rerun()
            if st.button("↺", key="zoom_reset_renda", help="Resetar visualização", use_container_width=True):
                st.session_state["mapa_renda_zoom"] = 9.4
                st.session_state["mapa_renda_inclinado"] = False
                st.rerun()
            if st.button(
                "2D" if inc_renda else "3D",
                key="btn_inclinado_renda",
                help="Alternar visualização em plano inclinado",
                use_container_width=True,
                type="primary" if inc_renda else "secondary",
            ):
                st.session_state["mapa_renda_inclinado"] = not inc_renda
                st.rerun()

# ---------- LINHA 4: Dispersão renda × exposição por bairro (IBGE × INCT) ----------
with st.container(key="card_dispersao"):
    exp_dispersao = st.session_state["exp_dispersao"]
    cab_esq, cab_exp = st.columns([16, 1], vertical_alignment="top")
    if sel.empty:
        with cab_esq:
            st.html(card_titulo("Os bairros mais expostos são os de menor renda?"))
        st.info("Selecione ao menos uma faixa de renda.")
    else:
        por_faixa = cruz.groupby("faixa_n").agg(afet=("affected_population", "sum"), pop=("population", "sum"))
        taxa = por_faixa["afet"] / por_faixa["pop"]
        with cab_esq:
            st.html(
                card_titulo(
                    "Os bairros mais expostos são os de menor renda?",
                    f"Cada ponto é um bairro (tamanho = população total) · renda média (IBGE) × % da população afetada a {fmt_m(nivel)} (INCT).",
                )
            )
        if cab_exp.button(
            "⤡" if exp_dispersao else "⤢",
            key="expandir_dispersao",
            help="Reduzir gráfico" if exp_dispersao else "Expandir gráfico",
            use_container_width=True,
        ):
            st.session_state["exp_dispersao"] = not exp_dispersao
            st.rerun()

        fig_disp = go.Figure()
        pop_max_b = max(float(sel["population"].max()), 1.0)
        for i, rot in enumerate(ROTULOS):
            parte = sel[sel["faixa"] == rot]
            if parte.empty:
                continue
            tamanhos_b = 8 + 20 * np.sqrt(parte["population"] / pop_max_b)
            fig_disp.add_trace(
                go.Scatter(
                    x=parte["renda_media_total"],
                    y=parte["pct_pop"],
                    mode="markers",
                    name=rot,
                    marker=dict(size=tamanhos_b, color=CORES_FAIXA[i], opacity=0.85, line=dict(color="#FFFFFF", width=1.5)),
                    customdata=parte[["bairro", "affected_population", "population"]],
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>Renda média: R$ %{x:,.0f}<br>"
                        "%{y:.1f}% da população afetada<br>"
                        "%{customdata[1]:,.0f} de %{customdata[2]:,.0f} hab.<extra></extra>"
                    ),
                )
            )
        fig_disp.update_xaxes(tickprefix="R$ ", tickformat=",.0f", showgrid=False, title=None)
        fig_disp.update_yaxes(range=[-4, 104], ticksuffix="%", gridcolor=BORDA, griddash="dot", title=None)
        estilo_plotly(fig_disp, 560 if exp_dispersao else 380)
        fig_disp.update_layout(font=dict(size=16 if exp_dispersao else 14))
        st.plotly_chart(fig_disp, config=PLOTLY_CONFIG, key="dispersao")
        st.html(
            '<div class="faixas" style="grid-template-columns:repeat(4,1fr)">'
            + "".join(
                f'<div><span><i style="background:{CORES_FAIXA[i]}"></i>{rot} · {FAIXA_RS[i]}</span>'
                f"<b>{fmt_pct(taxa.get(i, 0))}</b>"
                f'<small style="display:block;font-size:12px;color:{CINZA};margin-top:2px">'
                f"{fmt_int(por_faixa.loc[i, 'afet'])} de {fmt_int(por_faixa.loc[i, 'pop'])} hab.</small></div>"
                for i, rot in enumerate(ROTULOS)
            )
            + "</div>"
            f'<div class="nota">Parcela e total de pessoas afetadas em cada faixa de renda na cota de {fmt_m(nivel)}.</div>'
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

st.html(
    '<div class="rodape">Fontes: IBGE (Censo 2022, Tab. 8.3) · Zenodo (ADA RH Guaíba v0.4) · '
    "INCT SiMAI · Projeto extensionista CPAD — PUCRS</div>"
)
