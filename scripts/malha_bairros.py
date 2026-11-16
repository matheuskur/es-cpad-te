"""Gera a malha (GeoJSON) dos bairros de Porto Alegre para o mapa da Tela 1.

Baixa a malha de bairros do Censo 2022 do IBGE, filtra Porto Alegre (4314902), liga cada
bairro ao nome usado pelo INCT por meio de dados/processados/IBGE/bairros_poa.csv
(coluna cd_bairro_ibge) e salva dados/processados/geo/bairros_poa.geojson.

Uso, a partir da raiz do projeto:
    python scripts/malha_bairros.py
    python scripts/malha_bairros.py caminho/para/arquivo.zip   # se já tiver baixado a malha

Se o download falhar, baixe manualmente a malha de bairros do Censo 2022 do RS (ou do Brasil)
em https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html
e passe o .zip como argumento.
"""
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
DESTINO_ZIP = RAIZ / "dados" / "originais" / "geo"
SAIDA = RAIZ / "dados" / "processados" / "geo" / "bairros_poa.geojson"
LIGACAO = RAIZ / "dados" / "processados" / "IBGE" / "bairros_poa.csv"
COD_POA = "4314902"

BASE = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
    "malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/bairros/shp/"
)
URLS = [BASE + "UF/RS_bairros_CD2022.zip", BASE + "BR/BR_bairros_CD2022.zip"]


def baixar() -> Path:
    DESTINO_ZIP.mkdir(parents=True, exist_ok=True)
    for url in URLS:
        arquivo = DESTINO_ZIP / url.rsplit("/", 1)[1]
        if arquivo.exists():
            return arquivo
        print(f"Baixando {url} ...")
        try:
            r = requests.get(url, timeout=300)
            r.raise_for_status()
        except requests.RequestException as erro:
            print(f"  falhou: {erro}")
            continue
        arquivo.write_bytes(r.content)
        return arquivo
    sys.exit("Não foi possível baixar a malha. Baixe o .zip manualmente e passe o caminho como argumento.")


def main() -> None:
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else baixar()
    malha = gpd.read_file(f"zip://{zip_path}")
    malha.columns = [c.upper() if c != "geometry" else c for c in malha.columns]
    malha = malha[malha["CD_MUN"].astype(str) == COD_POA].copy()
    if malha.empty:
        sys.exit("A malha não tem bairros de Porto Alegre (CD_MUN 4314902).")

    ligacao = pd.read_csv(LIGACAO, dtype={"cd_bairro_ibge": str})[["bairro_inct", "cd_bairro_ibge"]]
    malha["CD_BAIRRO"] = malha["CD_BAIRRO"].astype(str)
    malha = malha.merge(ligacao, left_on="CD_BAIRRO", right_on="cd_bairro_ibge", how="inner")
    faltando = set(ligacao["bairro_inct"]) - set(malha["bairro_inct"])
    if faltando:
        print(f"Aviso: {len(faltando)} bairros do INCT sem polígono: {sorted(faltando)}")

    malha = malha.rename(columns={"bairro_inct": "bairro"})[["bairro", "CD_BAIRRO", "geometry"]]
    malha = malha.to_crs(4326)
    malha["geometry"] = malha.geometry.simplify(0.0002, preserve_topology=True)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    malha.to_file(SAIDA, driver="GeoJSON")
    print(f"Salvo {SAIDA.relative_to(RAIZ)} com {len(malha)} bairros.")


if __name__ == "__main__":
    main()
