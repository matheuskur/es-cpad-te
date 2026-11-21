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
    "area": '<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/>',
    "saude": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 7v6"/><path d="M9 10h6"/>',
    "ensino": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
    "filtro": '<path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>',
    "alerta": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
}

CSS = f"""
<style>
.block-container {{ max-width: 100%; padding-top: 6.5rem; padding-bottom: 4rem; padding-left: 2rem; padding-right: 2rem; }}

/* ritmo vertical: 24px entre blocos, 12px dentro dos cards */
.block-container > [data-testid="stVerticalBlock"] {{ gap: 1.5rem; }}
[class*="st-key-card"] {{ gap: .75rem; }}

/* cards da mesma linha com a mesma altura */
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] {{ height: 100%; }}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:last-child,
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child {{ flex: 1 1 auto; }}
[data-testid="stLayoutWrapper"] > [class*="st-key-card"] {{ height: 100%; }}
[data-testid="stHtml"]:has(> .cmp), [data-testid="stHtml"]:has(> .fonte), [data-testid="stHtml"]:has(> .kpi) {{ height: 100%; }}
.kpi {{ height: 100%; box-sizing: border-box; }}
[class*="st-key-card"] > [data-testid="stElementContainer"]:has(.mapa-vazio) {{ flex: 1 1 auto; }}
[data-testid="stHtml"]:has(> .mapa-vazio) {{ height: 100%; }}
.mapa-vazio {{ height: 100%; min-height: 160px; box-sizing: border-box; display: flex; align-items: center;
  justify-content: center; border: 1px dashed {BORDA}; border-radius: 12px; padding: 20px; text-align: center;
  color: {CINZA}; font-size: 13px; line-height: 1.5; background: {FUNDO}; }}

/* barra do topo */
[data-testid="stHeader"] {{ background: {TINTA}; height: 64px; box-shadow: 0 1px 0 rgba(255,255,255,.06); }}
[data-testid="stToolbar"] {{ height: 64px; padding: 0 2rem; }}
[data-testid="stTopNav"] {{ width: 100%; align-items: center; gap: 4px; }}
[data-testid="stTopNav"]::before {{ content: "Enchentes POA"; font-family: 'Fraunces', serif; font-weight: 600;
  font-size: 20px; color: #fff; margin-right: auto; white-space: pre; }}
[data-testid="stTopNavLink"] {{ border-radius: 999px; padding: 6px 16px; background: transparent; }}
[data-testid="stTopNavLink"] * {{ color: rgba(255,255,255,.72) !important; font-weight: 500; }}
[data-testid="stTopNavLink"]:hover {{ background: rgba(255,255,255,.08); }}
[data-testid="stTopNavLink"][aria-current="page"] {{ background: rgba(30,111,168,.55) !important; }}
[data-testid="stTopNavLink"][aria-current="page"] * {{ color: #fff !important; font-weight: 600; }}
[data-testid="stMainMenuButton"] svg, [data-testid="stToolbarActions"] svg {{ color: rgba(255,255,255,.75); fill: currentColor; }}
[data-testid="stDecoration"] {{ display: none; }}
.eyebrow {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; letter-spacing: .12em;
  text-transform: uppercase; color: {AZUL}; font-weight: 500; }}
.titulo {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 44px; line-height: 1.15;
  color: {TINTA}; margin: 6px 0 8px; }}
.sub {{ color: {CINZA}; font-size: 18px; line-height: 1.5; max-width: 900px; }}

/* bloco de destaque com o controle do nível */
.st-key-hero {{ background: linear-gradient(90deg, {TINTA}, #14507E); border-radius: 20px;
  padding: 28px 32px 18px; gap: .4rem; }}
.st-key-hero [data-testid="stSlider"] * {{ color: rgba(255,255,255,.75); }}
.st-key-hero [data-testid="stSliderThumbValue"] {{
  color: #fff !important;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  background: rgba(11,29,46,.85);
  padding: 2px 7px;
  border-radius: 6px;
}}
.st-key-hero [data-baseweb="slider"] > div:first-child {{ position: relative; }}
.st-key-hero [data-baseweb="slider"] > div:first-child::after {{
  content: "";
  position: absolute;
  left: 33.5714%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 3px;
  height: 18px;
  background: {CORAL};
  border-radius: 2px;
  pointer-events: none;
  z-index: 1;
}}
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
  box-shadow: 0 4px 16px rgba(11,29,46,.07); transition: all 0.25s ease; }}
.st-key-card_mapa, .st-key-card_mapa_renda {{ max-height: 100vh; overflow: hidden; position: relative; }}
.st-key-card_mapa [data-testid="stPlotlyChart"],
.st-key-card_mapa_renda [data-testid="stPlotlyChart"] {{ max-height: calc(100vh - 130px); overflow: hidden; }}
.st-key-mapa_controles, .st-key-mapa_controles_renda {{ position: absolute; left: 40px; bottom: 40px; z-index: 10; width: auto !important;
  background: rgba(255,255,255,.94); backdrop-filter: blur(6px); border: 1px solid {BORDA};
  border-radius: 12px; padding: 6px; box-shadow: 0 4px 14px rgba(11,29,46,.14); gap: 4px !important; }}
.st-key-mapa_controles button, .st-key-mapa_controles_renda button {{ min-width: 40px; padding: 4px 10px; font-size: 13px; }}
[class*="st-key-expandir_"] {{ display: flex; justify-content: flex-end; }}
[class*="st-key-expandir_"] button {{ width: 38px !important; min-width: 38px !important; height: 38px !important;
  padding: 0 !important; display: inline-flex; align-items: center; justify-content: center; }}
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
.rk .nome {{ font-weight: 400; }}
.rk .num {{ text-align: right; font-weight: 600; }}
.rk .barra {{ width: 90px; }}
.rk .barra div {{ height: 6px; border-radius: 3px; background: {CEU}; overflow: hidden; }}
.rk .barra span {{ display: block; height: 100%; background: {AZUL}; }}
.rk .pct {{ text-align: center; width: 76px; }}
.rk .pct span {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: {AZUL_ESCURO}; background: {CEU};
  border-radius: 999px; padding: 3px 0; display: inline-block; width: 56px; text-align: center; }}
.rodape {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: {CINZA}; margin-top: 8px; }}
/* ---------- Tela 2 ---------- */
.st-key-hero_t2 {{ background: linear-gradient(90deg, {TINTA}, #14507E); border-radius: 20px;
  padding: 28px 32px 18px; gap: .5rem; }}
.st-key-hero_t2 [data-testid="stSlider"] * {{ color: rgba(255,255,255,.78); }}
.st-key-hero_t2 [data-testid="stSliderThumbValue"] {{
  color: #fff !important;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  background: rgba(11,29,46,.85);
  padding: 2px 8px;
  border-radius: 6px;
}}
.st-key-hero_t2 .hero-valor-t2 {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 56px; line-height: 1.05; color: #fff; margin-top: 4px; }}
.st-key-card_filtros {{ padding: 18px 24px; }}
.filtros-t {{ display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 15px; color: {TINTA}; }}
.faixas {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 4px; }}
.faixas div {{ background: {FUNDO}; border-radius: 12px; padding: 10px 12px; }}
.faixas span {{ font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; white-space: nowrap; color: {CINZA}; display: flex; align-items: center; gap: 6px; }}
.faixas i {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
.faixas b {{ display: block; font-size: 17px; color: {TINTA}; font-weight: 600; }}
.cmp {{ background: linear-gradient(180deg, {TINTA}, #14507E); border-radius: 16px; padding: 28px; color: #fff;
  display: flex; flex-direction: column; gap: 20px; height: 100%; box-sizing: border-box; }}
.cmp-e {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: .12em; color: #7FC3F0; }}
.cmp-t {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 22px; line-height: 1.2; margin: 6px 0 4px; }}
.cmp-s {{ font-size: 13px; color: rgba(255,255,255,.6); }}
.cmp-l {{ display: flex; justify-content: space-between; align-items: baseline; font-size: 13px; color: rgba(255,255,255,.75); }}
.cmp-l b {{ font-family: 'Fraunces', serif; font-size: 26px; color: #fff; font-weight: 600; }}
.cmp-bar {{ height: 10px; border-radius: 5px; background: rgba(255,255,255,.12); margin-top: 8px; overflow: hidden; }}
.cmp-bar span {{ display: block; height: 100%; border-radius: 5px; }}
.cmp-d {{ margin-top: auto; display: flex; gap: 14px; align-items: center; background: rgba(255,255,255,.07); border-radius: 12px; padding: 14px 16px; }}
.cmp-d b {{ font-family: 'Fraunces', serif; font-size: 30px; color: #F7A08F; font-weight: 600; white-space: nowrap; }}
.cmp-d span {{ font-size: 13px; line-height: 1.45; color: rgba(255,255,255,.75); }}
.mini {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }}
.mini div {{ background: {FUNDO}; border-radius: 12px; padding: 12px 14px; }}
.mini span {{ font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: .08em; color: {CINZA}; }}
.mini b {{ display: block; font-family: 'Fraunces', serif; font-size: 24px; color: {TINTA}; font-weight: 600; }}
.nota {{ font-size: 12px; color: {CINZA}; line-height: 1.45; margin-top: 12px; }}
.secao-t {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 22px; color: {TINTA}; margin-top: 8px; }}
.fonte {{ background: #fff; border: 1px solid {BORDA}; border-radius: 16px; padding: 22px 24px;
  box-shadow: 0 4px 16px rgba(11,29,46,.07); display: flex; flex-direction: column; gap: 10px; height: 100%; box-sizing: border-box; }}
.fonte .tipo {{ align-self: flex-start; font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: .08em;
  padding: 3px 10px; border-radius: 999px; }}
.fonte .nome {{ font-weight: 600; font-size: 17px; color: {TINTA}; }}
.fonte .desc {{ font-size: 13px; color: {CINZA}; line-height: 1.45; flex: 1; }}
.fonte a {{ font-size: 13px; font-weight: 500; color: {AZUL}; word-break: break-all; }}
.fonte .data {{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: {CINZA}; border-top: 1px solid {BORDA}; padding-top: 10px; }}
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


def fmt_reais(x: float) -> str:
    return "R$ " + fmt_int(x)


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
