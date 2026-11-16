"""Estilo visual compartilhado (segue o Figma "Dashboard Enchentes POA — CAPD")."""
import base64

import plotly.graph_objects as go
import streamlit as st

TINTA = "#0B1D2E"
AZUL = "#1E6FA8"
AZUL_ESCURO = "#0A3D62"
CEU = "#EAF3FA"
FUNDO = "#F5F7FA"
BORDA = "#E3E8EF"
CINZA = "#5B6B7C"
CORAL = "#E0533D"
AMBAR = "#F0B429"

FAIXAS = [(75, "#0A3D62", "75–100%"), (50, "#2F7FBF", "50–75%"), (25, "#6BAED6", "25–50%"), (0, "#BBD7EE", "até 25%")]

ICONES = {
    "pessoas": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "predios": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "bairros": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "alerta": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
}

CSS = f"""
<style>
.block-container {{ max-width: 100%; padding-top: 4.5rem; padding-bottom: 4rem; padding-left: 2rem; padding-right: 2rem; }}
.eyebrow {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; letter-spacing: .12em;
  text-transform: uppercase; color: {AZUL}; font-weight: 500; }}
.titulo {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 44px; line-height: 1.15;
  color: {TINTA}; margin: 6px 0 8px; }}
.sub {{ color: {CINZA}; font-size: 18px; line-height: 1.5; max-width: 900px; }}

/* bloco de destaque com o controle do nível */
.st-key-hero {{ background: linear-gradient(90deg, {TINTA}, #14507E); border-radius: 20px;
  padding: 28px 32px 18px; gap: .4rem; }}
.st-key-hero [data-testid="stSlider"] * {{ color: rgba(255,255,255,.75); }}
.st-key-hero [data-testid="stSliderThumbValue"] {{ display: none; }}  /* o valor já aparece grande acima */
.aviso img {{ flex-shrink: 0; margin-top: 2px; }}
.hero-top {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; flex-wrap: wrap; }}
.hero-eyebrow {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; letter-spacing: .12em; color: rgba(255,255,255,.6); }}
.hero-valor {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 80px; line-height: 1; color: #fff; }}
.hero-valor small {{ font-size: 34px; color: rgba(255,255,255,.55); margin-left: 6px; }}
.hero-rel {{ color: rgba(255,255,255,.7); font-size: 15px; margin-top: 6px; }}
.chips {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.chip {{ display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px; border-radius: 999px;
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16); color: rgba(255,255,255,.9);
  font-size: 14px; font-weight: 500; }}
.chip i {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
.hero-dica {{ color: rgba(255,255,255,.6); font-size: 14px; }}

/* cards */
[class*="st-key-card"] {{ background: #fff; border: 1px solid {BORDA}; border-radius: 16px; padding: 24px;
  box-shadow: 0 4px 16px rgba(11,29,46,.07); }}
.card-t {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 22px; color: {TINTA}; display: flex;
  align-items: center; gap: 10px; }}
.card-s {{ font-size: 14px; color: {CINZA}; margin-top: 2px; }}
.selo {{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: .06em; padding: 3px 10px;
  border-radius: 999px; background: rgba(224,83,61,.12); color: {CORAL}; font-weight: 500; }}
.legenda {{ display: flex; gap: 14px; font-size: 13px; color: {CINZA}; margin-top: 12px; flex-wrap: wrap; }}
.legenda i {{ width: 10px; height: 10px; border-radius: 3px; display: inline-block; margin-right: 6px; vertical-align: -1px; }}

/* indicadores */
.kpi {{ background: #fff; border: 1px solid {BORDA}; border-radius: 16px; padding: 22px 24px;
  box-shadow: 0 4px 16px rgba(11,29,46,.07); }}
.kpi-top {{ display: flex; align-items: center; gap: 10px; color: {CINZA}; font-weight: 500; font-size: 16px; }}
.kpi-ic {{ width: 36px; height: 36px; border-radius: 10px; background: {CEU}; display: grid; place-items: center; }}
.kpi-v {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 48px; color: {TINTA}; margin: 10px 0 12px; line-height: 1.1; }}
.kpi-bar {{ height: 6px; border-radius: 3px; background: {CEU}; overflow: hidden; }}
.kpi-bar span {{ display: block; height: 100%; background: {AZUL}; border-radius: 3px; }}
.kpi-d {{ font-size: 14px; color: {CINZA}; margin-top: 12px; }}

/* aviso */
.aviso {{ display: flex; gap: 14px; background: #FDF6E7; border: 1px solid rgba(138,90,18,.2); border-radius: 14px;
  padding: 16px 20px; color: #8A5A12; font-size: 15px; line-height: 1.5; }}
.aviso b {{ display: block; font-size: 16px; margin-bottom: 2px; }}

/* resumo da curva */
.resumo {{ display: flex; gap: 12px; }}
.resumo div {{ flex: 1; background: {FUNDO}; border-radius: 12px; padding: 12px 14px; }}
.resumo div.ativo {{ background: rgba(30,111,168,.08); }}
.resumo span {{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: .04em; color: {CINZA}; }}
.resumo div.ativo span {{ color: {AZUL}; }}
.resumo b {{ display: block; font-size: 19px; color: {TINTA}; font-weight: 600; }}

/* ranking */
.rk {{ width: 100%; border-collapse: collapse; margin-top: 14px; }}
.rk th {{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: .08em; color: {CINZA};
  font-weight: 500; text-align: left; padding: 8px 4px; border-bottom: 1px solid {BORDA}; }}
.rk td {{ padding: 10px 4px; border-bottom: 1px solid {BORDA}; font-size: 16px; color: {TINTA}; }}
.rk .pos {{ font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: {CINZA}; width: 28px; }}
.rk .nome {{ font-weight: 500; }}
.rk .num {{ text-align: right; font-weight: 600; }}
.rk .barra {{ width: 90px; }}
.rk .barra div {{ height: 6px; border-radius: 3px; background: {CEU}; overflow: hidden; }}
.rk .barra span {{ display: block; height: 100%; background: {AZUL}; }}
.rk .pct {{ text-align: center; width: 76px; }}
.rk .pct span {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: {AZUL_ESCURO}; background: {CEU};
  border-radius: 999px; padding: 3px 0; display: inline-block; width: 56px; text-align: center; }}
.rodape {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: {CINZA}; margin-top: 8px; }}
</style>
"""


def aplicar_estilo() -> None:
    st.html(CSS)


def icone(nome: str, cor: str = AZUL, tamanho: int = 20) -> str:
    """Ícone SVG como <img> (o st.html remove <svg> embutido)."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{cor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f"{ICONES[nome]}</svg>"
    )
    dados = base64.b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{dados}" width="{tamanho}" height="{tamanho}" alt="">'


def fmt_int(n: float) -> str:
    return f"{round(n):,}".replace(",", ".")


def fmt_pct(x: float, casas: int = 1) -> str:
    return f"{100 * x:.{casas}f}%".replace(".", ",")


def fmt_m(nivel: float) -> str:
    return f"{nivel:.1f} m".replace(".", ",")


def cor_faixa(p: float) -> str:
    return next(cor for limite, cor, _ in FAIXAS if p >= limite)


def card_titulo(titulo: str, sub: str = "", selo: str = "") -> str:
    selo_html = f'<span class="selo">{selo}</span>' if selo else ""
    sub_html = f'<div class="card-s">{sub}</div>' if sub else ""
    return f'<div class="card-t">{titulo}{selo_html}</div>{sub_html}'


def estilo_plotly(fig: go.Figure, altura: int) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=dict(l=0, r=8, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", size=14, color=TINTA),
        separators=",.",
        showlegend=False,
        hoverlabel=dict(bgcolor=TINTA, font_color="#fff", font_family="IBM Plex Sans, sans-serif"),
    )
    return fig


PLOTLY_CONFIG = {"displayModeBar": False}
