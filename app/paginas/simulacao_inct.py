"""Tela 1 — Simulação do INCT.

Usa apenas o JSON do INCT, depois de limpo (dados/processados/INCT/inct_limpo.json).
O controle deslizante do nível do Guaíba atualiza todos os elementos da página.
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.dados import (
    COTA_INUNDACAO,
    NIVEL_MAX,
    NIVEL_MIN,
    NIVEL_PASSO,
    NIVEL_RECORDE_2024,
    carregar_geojson_bairros,
    carregar_inct,
    recorte_nivel,
    serie_cidade,
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
    icone,
)

aplicar_estilo()

df = carregar_inct()
serie = serie_cidade(df)

if "nivel" not in st.session_state:
    st.session_state["nivel"] = 5.3
nivel = round(st.session_state["nivel"], 1)

# ---------- dados do nível escolhido ----------
atual = recorte_nivel(df, nivel)
pessoas = atual["affected_population"].sum()
populacao = atual["population"].sum()
predios = atual["affected_buildings"].sum()
total_predios = atual["total_buildings"].sum()
atingidos = atual[atual["affected_buildings"] > 0]
n_bairros = atual["bairro"].nunique()

# ---------- cabeçalho ----------
st.html(
    '<div class="eyebrow">Porto Alegre · simulação INCT SiMAI</div>'
    f'<div class="titulo">Se o Guaíba chegar a {fmt_m(nivel)}</div>'
    '<div class="sub">Impacto estimado em pessoas, prédios e bairros para cada nível do rio entre '
    "3,0 m e 10,0 m. Fonte: JSON do INCT SiMAI, limpo pela equipe "
    f"({df['nivel_m'].nunique()} níveis × {n_bairros} bairros).</div>"
)

# ---------- controle do nível ----------
dif_cm = round((NIVEL_RECORDE_2024 - nivel) * 100)
if dif_cm > 0:
    relacao = f"{dif_cm} cm abaixo do recorde de maio de 2024"
elif dif_cm < 0:
    relacao = f"{-dif_cm} cm acima do recorde de maio de 2024"
else:
    relacao = "igual ao recorde de maio de 2024"
inteiro, decimal = f"{nivel:.1f}".split(".")
cota_txt = f"{COTA_INUNDACAO:.2f}".replace(".", ",")

with st.container(key="hero"):
    st.html(
        '<div class="hero-top"><div>'
        '<div class="hero-eyebrow">NÍVEL DO GUAÍBA</div>'
        f'<div class="hero-valor">{inteiro},{decimal}<small>m</small></div>'
        f'<div class="hero-rel">{relacao}</div></div>'
        '<div class="chips">'
        f'<span class="chip"><i style="background:{AMBAR}"></i>Cota de inundação · {cota_txt} m</span>'
        f'<span class="chip"><i style="background:{CORAL}"></i>Recorde mai/2024 · 5,35 m</span>'
        "</div></div>"
    )
    st.slider(
        "Nível do Guaíba (m)",
        min_value=NIVEL_MIN,
        max_value=NIVEL_MAX,
        step=NIVEL_PASSO,
        format="%.1f m",
        key="nivel",
        label_visibility="collapsed",
    )
    st.html(
        '<div class="hero-dica">Arraste para escolher o nível (passo de 0,1 m). '
        "Indicadores, gráficos e ranking abaixo se atualizam juntos.</div>"
    )

# ---------- indicadores ----------
milhoes = f"{populacao / 1e6:.2f}".replace(".", ",")
indicadores = [
    ("pessoas", "Pessoas afetadas", fmt_int(pessoas), pessoas / populacao,
     f"{fmt_pct(pessoas / populacao)} dos {milhoes} milhão de moradores"),
    ("predios", "Prédios afetados", fmt_int(predios), predios / total_predios,
     f"{fmt_pct(predios / total_predios)} dos {fmt_int(total_predios)} prédios da cidade"),
    ("bairros", "Bairros atingidos", f"{len(atingidos)} de {n_bairros}", len(atingidos) / n_bairros,
     f"{fmt_pct(len(atingidos) / n_bairros, 0)} dos bairros têm ao menos 1 prédio afetado"),
]
for coluna, (ic, rotulo, valor, fracao, detalhe) in zip(st.columns(3, gap="medium"), indicadores):
    coluna.html(
        f'<div class="kpi"><div class="kpi-top"><span class="kpi-ic">{icone(ic)}</span>{rotulo}</div>'
        f'<div class="kpi-v">{valor}</div>'
        f'<div class="kpi-bar"><span style="width:{100 * fracao:.1f}%"></span></div>'
        f'<div class="kpi-d">{detalhe}</div></div>'
    )

# ---------- aviso de limitações ----------
st.html(
    f'<div class="aviso">{icone("alerta", "#8A5A12")}<div><b>Limitações dos dados</b>'
    "A simulação cruza a cota do Guaíba com a mancha de inundação e não considera diques, comportas, "
    "casas de bombas, chuva local nem duração da cheia. A fonte arredonda o percentual de prédios para "
    "cima, o que superestima a população afetada (até ~500 pessoas por bairro e nível). Leia os números "
    "como ordem de grandeza, não como previsão.</div></div>"
)

# ---------- curva da cidade (largura total) ----------
with st.container(key="card_curva"):
    st.html(card_titulo(
        "População afetada por nível do lago",
        f"Soma da cidade ({n_bairros} bairros) · tracejado: recorde de maio/2024",
    ))
    y_atual = serie.loc[serie["nivel_m"] == nivel, "pessoas"].iloc[0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie["nivel_m"], y=serie["pessoas"], mode="lines",
        line=dict(color=AZUL, width=3, shape="spline", smoothing=0.4),
        fill="tozeroy", fillcolor="rgba(30,111,168,0.12)",
        hovertemplate="%{x:.1f} m<br><b>%{y:,.0f} pessoas</b><extra></extra>",
    ))
    fig.add_vline(x=NIVEL_RECORDE_2024, line=dict(color=CORAL, width=1.5, dash="dash"))
    fig.add_annotation(
        x=NIVEL_RECORDE_2024, y=1, yref="paper", text="Recorde · 5,35 m", showarrow=False,
        xanchor="left", yanchor="top", xshift=6, bgcolor=CORAL, borderpad=4,
        font=dict(color="#FFFFFF", family="IBM Plex Mono, monospace", size=12),
    )
    fig.add_trace(go.Scatter(
        x=[nivel], y=[y_atual], mode="markers", hoverinfo="skip",
        marker=dict(size=12, color="#FFFFFF", line=dict(color=AZUL, width=3)),
    ))
    fig.add_annotation(
        x=nivel, y=y_atual, showarrow=False, align="left", borderpad=8, bgcolor=TINTA,
        xanchor="right" if nivel > 8 else "left", xshift=-14 if nivel > 8 else 14,
        yanchor="top", yshift=-8, font=dict(color="#FFFFFF", size=14),
        text=f"<span style='font-size:12px'>{fmt_m(nivel)}</span><br><b>{fmt_int(y_atual)} pessoas</b>",
    )
    fig.update_xaxes(range=[NIVEL_MIN - 0.05, NIVEL_MAX + 0.1], dtick=1, ticksuffix=" m", showgrid=False,
                     tickfont=dict(family="IBM Plex Mono, monospace", size=12, color=CINZA))
    fig.update_yaxes(rangemode="tozero", gridcolor=BORDA, griddash="dot", tickformat=",.0f",
                     tickfont=dict(family="IBM Plex Mono, monospace", size=12, color=CINZA))
    estilo_plotly(fig, 330)
    st.plotly_chart(fig, config=PLOTLY_CONFIG, key="curva")

    pontos = [(NIVEL_MIN, "início"), (nivel, "escolhido"), (NIVEL_MAX, "máximo")]
    st.html('<div class="resumo">' + "".join(
        f'<div class="{"ativo" if rot == "escolhido" else ""}"><span>{fmt_m(n)} · {rot.upper()}</span>'
        f'<b>{fmt_int(serie.loc[serie["nivel_m"] == round(n, 1), "pessoas"].iloc[0])} pessoas</b></div>'
        for n, rot in pontos
    ) + "</div>")

# ---------- % de prédios por bairro + ranking ----------
col_barras, col_rank = st.columns([1.2, 1], gap="medium")

with col_barras, st.container(key="card_barras"):
    cab_esq, cab_dir = st.columns([2, 1], vertical_alignment="top")
    with cab_dir:
        modo = (
            st.segmented_control(
                "Métrica do gráfico",
                ["Prédios", "População"],
                default="Prédios",
                key="modo_barras",
                label_visibility="collapsed",
            )
            or "Prédios"
        )

    if modo == "Prédios":
        ordem = atingidos.sort_values(["percentage", "affected_buildings"], ascending=[False, False])
        valores = ordem["percentage"]
        custom = ordem[["affected_buildings", "total_buildings"]]
        titulo_barras = "Prédios afetados por bairro"
        sub_base = "% dos prédios de cada bairro atingido"
        hover_rot = "dos prédios"
    else:
        atingidos_pop = atual[atual["affected_population"] > 0].copy()
        atingidos_pop["pct_pop"] = (
            (atingidos_pop["affected_population"] / atingidos_pop["population"].where(atingidos_pop["population"] > 0))
            * 100
        ).fillna(0).clip(upper=100).round().astype(int)
        ordem = atingidos_pop.sort_values(["pct_pop", "affected_population"], ascending=[False, False])
        valores = ordem["pct_pop"]
        custom = ordem[["affected_population", "population"]]
        titulo_barras = "População afetada por bairro"
        sub_base = "% da população de cada bairro atingida"
        hover_rot = "da população"

    sub = f"{sub_base} · {len(ordem)} bairros"
    if len(ordem) > 13:
        sub += " · role para ver todos"
    legenda = "".join(f'<span><i style="background:{cor}"></i>{rot}</span>' for _, cor, rot in reversed(FAIXAS))
    with cab_esq:
        st.html(card_titulo(titulo_barras, sub) + f'<div class="legenda">{legenda}</div>')

    if ordem.empty:
        st.info(f"Nenhum bairro tem {modo.lower()} afetados neste nível.")
    else:
        fig = go.Figure(
            go.Bar(
                x=valores,
                y=ordem["bairro"],
                orientation="h",
                marker_color=[cor_faixa(p) for p in valores],
                text=[f"{p}%" for p in valores],
                textposition="outside",
                textfont=dict(family="IBM Plex Mono, monospace", size=13),
                cliponaxis=False,
                customdata=custom,
                hovertemplate=f"<b>%{{y}}</b><br>%{{x}}% {hover_rot}<br>"
                "%{customdata[0]:,.0f} de %{customdata[1]:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(barcornerradius=6, bargap=0.45)
        fig.update_xaxes(range=[0, 112], visible=False)
        fig.update_yaxes(autorange="reversed", ticksuffix="  ", showgrid=False)
        estilo_plotly(fig, max(260, 30 * len(ordem) + 20))
        with st.container(height=500, border=False):
            st.plotly_chart(fig, config=PLOTLY_CONFIG, key="barras")

with col_rank, st.container(key="card_ranking"):
    st.html(card_titulo("Bairros mais afetados", "Por pessoas afetadas no nível escolhido"))
    top = atingidos.nlargest(10, "affected_population")
    if top.empty:
        st.info("Nenhum bairro tem pessoas afetadas neste nível.")
    else:
        maximo = top["affected_population"].max()
        linhas = "".join(
            f'<tr><td class="pos">{i:02d}</td><td class="nome">{r.bairro}</td>'
            f'<td class="barra"><div><span style="width:{100 * r.affected_population / maximo:.0f}%">'
            f'</span></div></td><td class="num">{fmt_int(r.affected_population)}</td>'
            f'<td class="pct"><span>{r.percentage}%</span></td></tr>'
            for i, r in enumerate(top.itertuples(), start=1)
        )
        st.html(
            '<table class="rk"><tr><th>#</th><th>BAIRRO</th><th></th>'
            '<th style="text-align:right">PESSOAS</th><th style="text-align:center">% PRÉD.</th></tr>'
            f"{linhas}</table>"
        )

# ---------- mapa dos bairros (largura total) ----------
if "mapa_zoom" not in st.session_state:
    st.session_state["mapa_zoom"] = 9.4
if "mapa_inclinado" not in st.session_state:
    st.session_state["mapa_inclinado"] = False

with st.container(key="card_mapa"):
    barra_cores = (
        '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;min-width:260px">'
        '<div style="width:100%;height:10px;border-radius:999px;'
        'background:linear-gradient(90deg,#E9EEF3 0%,#BBD7EE 25%,#6BAED6 50%,#2F7FBF 75%,#0A3D62 100%)"></div>'
        f'<div style="width:100%;display:flex;justify-content:space-between;font-family:\'IBM Plex Mono\',monospace;'
        f'font-size:12px;color:{CINZA}"><span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span></div>'
        "</div>"
    )
    st.html(
        '<div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:16px">'
        f'<div>{card_titulo("Mapa dos bairros", "Cor = % de prédios afetados")}</div>'
        f"{barra_cores}<div></div></div>"
    )

    malha = carregar_geojson_bairros()
    if malha is None:
        st.html(
            f'<div style="border:1px dashed {BORDA};border-radius:12px;padding:28px 20px;'
            f'text-align:center;color:{CINZA};font-size:13px;line-height:1.5;margin-top:12px">'
            "Malha dos bairros não encontrada.<br>Gere com <code>python scripts/malha_bairros.py</code> "
            "para ver o mapa.</div>"
        )
    else:
        zoom_atual = st.session_state["mapa_zoom"]
        inclinado = st.session_state["mapa_inclinado"]
        fig = px.choropleth_map(
            atual,
            geojson=malha,
            locations="bairro",
            featureidkey="properties.bairro",
            color="percentage",
            range_color=(0, 100),
            color_continuous_scale=["#E9EEF3", "#BBD7EE", "#6BAED6", "#2F7FBF", "#0A3D62"],
            map_style="carto-positron",
            center={"lat": -30.09, "lon": -51.17},
            zoom=zoom_atual,
            opacity=0.9,
            hover_name="bairro",
            hover_data={"bairro": False, "percentage": True, "affected_population": True},
            labels={"percentage": "% prédios", "affected_population": "Pessoas"},
        )
        fig.update_traces(marker_line_color="#FFFFFF", marker_line_width=0.6)
        fig.update_layout(
            coloraxis_showscale=False,
            uirevision=f"{zoom_atual}-{inclinado}",
            map=dict(
                pitch=45 if inclinado else 0,
                bearing=-15 if inclinado else 0,
            ),
        )
        estilo_plotly(fig, 740)
        st.plotly_chart(fig, config=PLOTLY_CONFIG, key="mapa")

        with st.container(key="mapa_controles"):
            if st.button("＋", key="zoom_mais", help="Aproximar", use_container_width=True):
                st.session_state["mapa_zoom"] = min(14.0, round(st.session_state["mapa_zoom"] + 0.6, 1))
                st.rerun()
            if st.button("－", key="zoom_menos", help="Afastar", use_container_width=True):
                st.session_state["mapa_zoom"] = max(8.0, round(st.session_state["mapa_zoom"] - 0.6, 1))
                st.rerun()
            if st.button("↺", key="zoom_reset", help="Resetar visualização", use_container_width=True):
                st.session_state["mapa_zoom"] = 9.4
                st.session_state["mapa_inclinado"] = False
                st.rerun()
            if st.button(
                "2D" if inclinado else "3D",
                key="btn_inclinado",
                help="Alternar visualização em plano inclinado",
                use_container_width=True,
                type="primary" if inclinado else "secondary",
            ):
                st.session_state["mapa_inclinado"] = not inclinado
                st.rerun()

st.html(
    '<div class="rodape">Fonte: INCT SiMAI (vhlab.com.br/INCT/floods) · limpeza: '
    "scripts/limpeza_inct.py · Projeto extensionista CAPD — PUCRS</div>"
)
