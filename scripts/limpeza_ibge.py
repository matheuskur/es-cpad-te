"""Limpeza dos dados do IBGE (Censo 2022) para Porto Alegre.

Fontes (dados/originais/IBGE/):
- Tab8_3.xlsx: renda por área de ponderação (versionado).
- composicao_areas_ponderacao_IBGE.xlsx: setor -> área de ponderação (versionado).
- Agregados por setor censitário (básico, BR): baixado do FTP do IBGE se não existir
  localmente, extraído em dados/originais/IBGE/agregados/ (fora do git).

Saídas (dados/processados/IBGE/):
- areas_ponderacao_poa.csv: Tabela 8.3 filtrada para Porto Alegre.
- setores_areas_poa.csv: setor -> área de ponderação, Porto Alegre.
- setores_bairros_poa.csv: setor -> bairro e população (v0001), Porto Alegre.
- bairros_poa.csv: os 94 bairros do INCT ligados ao IBGE, com população e renda.
- bairros_renda_ponderada_detalhe.csv: pesos por área dos bairros em mais de uma área.

Uso (a partir da raiz do projeto):
    python scripts/limpeza_ibge.py
"""

import json
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
ORIGINAIS = RAIZ / "dados" / "originais" / "IBGE"
PASTA_AGREGADOS = ORIGINAIS / "agregados"
ZIP_AGREGADOS = PASTA_AGREGADOS / "Agregados_por_setores_basico_BR_20260520.zip"
MEMBRO_AGREGADOS = "Agregados_por_setores_basico_BR.csv"
URL_AGREGADOS = (
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/"
    "Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip"
)
INCT_JSON = RAIZ / "dados" / "originais" / "INCT" / "data_inct_original.json"
SAIDA = RAIZ / "dados" / "processados" / "IBGE"

TAB83 = ORIGINAIS / "Tab8_3.xlsx"
COMPOSICAO = ORIGINAIS / "composicao_areas_ponderacao_IBGE.xlsx"

COD_PORTO_ALEGRE = 4314902
LINHAS_CABECALHO = 4  # duas de título e duas de cabeçalho

# Nome do bairro no INCT -> nome do mesmo bairro no IBGE, quando a grafia difere
ALIAS = {
    "Mont'Serrat": "Mont'Serrat",
    "Passo D'Areia": "Passo da Areia",
    "Menino Deus": "Menino-Deus",
}


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação (apóstrofo e hífen viram nada)."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    limpo = re.sub(r"[^a-z0-9 ]", "", sem_acento.replace("-", " "))
    return " ".join(limpo.split())


def carregar_inct():
    """Devolve {bairro: população} para os 94 bairros do INCT."""
    with open(INCT_JSON, encoding="utf-8") as f:
        raw = json.load(f)
    primeiro = raw[next(iter(raw))]
    return {bairro: valores["population"] for bairro, valores in primeiro.items()}


# ---------------------------------------------------------------- Tabela 8.3 e composição

def ler_tab83():
    colunas = [
        "codigo_municipio", "nome_municipio", "codigo_area", "nome_area",
        "pessoas_total", "pessoas_homens", "pessoas_mulheres",
        "renda_media_total", "renda_media_homens", "renda_media_mulheres",
        "renda_mediana_total", "renda_mediana_homens", "renda_mediana_mulheres",
    ]
    df = pd.read_excel(TAB83, header=None, skiprows=LINHAS_CABECALHO, names=colunas, dtype=object)
    df = df.dropna(subset=["codigo_area"])
    df = df[df["codigo_municipio"] == COD_PORTO_ALEGRE].copy()
    df["codigo_area"] = df["codigo_area"].astype("int64")
    for c in colunas[4:]:
        df[c] = pd.to_numeric(df[c])
    return df.reset_index(drop=True)


def ler_composicao(areas_validas):
    df = pd.read_excel(COMPOSICAO, dtype=str)
    df.columns = ["setor", "codigo_municipio", "codigo_area", "nome_municipio"]  # corrige "Municíipio"
    df = df[df["codigo_municipio"].astype(int) == COD_PORTO_ALEGRE].copy()
    df["codigo_area"] = df["codigo_area"].astype("int64")
    fora = set(df["codigo_area"]) - set(areas_validas)
    assert not fora, f"áreas de setores sem linha na Tabela 8.3: {fora}"
    return df[["setor", "codigo_area"]].reset_index(drop=True)


# ---------------------------------------------------------------- agregados por setor

def baixar_agregados():
    """Baixa o ZIP do IBGE se ainda não existir localmente."""
    PASTA_AGREGADOS.mkdir(parents=True, exist_ok=True)
    if ZIP_AGREGADOS.exists() and zipfile.is_zipfile(ZIP_AGREGADOS):
        return
    print(f"Baixando {URL_AGREGADOS}")
    tmp = ZIP_AGREGADOS.with_suffix(".part")
    with requests.get(URL_AGREGADOS, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for bloco in r.iter_content(chunk_size=1 << 20):
                f.write(bloco)
    if not zipfile.is_zipfile(tmp):
        tmp.unlink()
        raise RuntimeError("o arquivo baixado não é um ZIP válido")
    tmp.replace(ZIP_AGREGADOS)


def extrair_agregados():
    """Extrai o CSV do ZIP, se ainda não estiver extraído."""
    destino = PASTA_AGREGADOS / MEMBRO_AGREGADOS
    if not destino.exists():
        with zipfile.ZipFile(ZIP_AGREGADOS) as z:
            z.extract(MEMBRO_AGREGADOS, PASTA_AGREGADOS)
    return destino


def ler_setores_poa(csv_path):
    """Lê só as colunas necessárias e filtra Porto Alegre."""
    df = pd.read_csv(
        csv_path, sep=";", encoding="latin-1", dtype=str,
        usecols=["CD_SETOR", "CD_MUN", "CD_BAIRRO", "NM_BAIRRO", "v0001"],
    )
    df = df[df["CD_MUN"] == str(COD_PORTO_ALEGRE)].copy()
    df["populacao"] = pd.to_numeric(df["v0001"], errors="raise")
    return df.rename(columns={
        "CD_SETOR": "setor", "CD_BAIRRO": "cd_bairro", "NM_BAIRRO": "nome_bairro",
    })[["setor", "cd_bairro", "nome_bairro", "populacao"]].reset_index(drop=True)


# ---------------------------------------------------------------- ligação bairro <-> área

def renda_ponderada(setores, setores_areas, areas, cd_bairro):
    """Renda média e mediana de um bairro em duas ou mais áreas, ponderadas pela população
    dos setores do bairro em cada área. A mediana ponderada é aproximada (média das medianas)."""
    s = setores[setores["cd_bairro"] == cd_bairro].merge(setores_areas, on="setor")
    det = s.groupby("codigo_area", as_index=False).agg(populacao=("populacao", "sum"))
    det = det.merge(
        areas[["codigo_area", "nome_area", "renda_media_total", "renda_mediana_total"]], on="codigo_area"
    )
    det["peso"] = det["populacao"] / det["populacao"].sum()
    media = float((det["peso"] * det["renda_media_total"]).sum())
    mediana = float((det["peso"] * det["renda_mediana_total"]).sum())
    return media, mediana, det


def ligar_bairros(setores, setores_areas, areas, populacao_inct):
    detalhes = []
    ibge = (
        setores.groupby(["cd_bairro", "nome_bairro"], as_index=False)
        .agg(setores=("setor", "count"), populacao_ibge=("populacao", "sum"))
    )
    ibge["chave"] = ibge["nome_bairro"].map(normalizar)

    areas_do_bairro = (
        setores.merge(setores_areas, on="setor")
        .groupby("cd_bairro")["codigo_area"]
        .apply(lambda s: sorted(set(s)))
        .to_dict()
    )
    areas_indexadas = areas.set_index("codigo_area")

    linhas = []
    for bairro, pop_inct in populacao_inct.items():
        chave = normalizar(ALIAS.get(bairro, bairro))
        candidatos = ibge[ibge["chave"] == chave]
        linha = {
            "bairro_inct": bairro,
            "populacao_inct": pop_inct,
            "status": "sem_correspondencia",
            "cd_bairro_ibge": None, "nome_bairro_ibge": None,
            "setores": None, "populacao_ibge": None,
            "areas": None, "n_areas": None,
            "codigo_area": None, "nome_area": None,
            "renda_media_total": None, "renda_mediana_total": None,
            "metodo_renda": None,
        }
        if len(candidatos) == 1:
            c = candidatos.iloc[0]
            codigos = areas_do_bairro.get(c["cd_bairro"], [])
            linha.update({
                "status": "ok",
                "cd_bairro_ibge": c["cd_bairro"],
                "nome_bairro_ibge": c["nome_bairro"],
                "setores": int(c["setores"]),
                "populacao_ibge": int(c["populacao_ibge"]),
                "areas": "; ".join(str(x) for x in codigos),
                "n_areas": len(codigos),
            })
            if len(codigos) == 1:
                a = areas_indexadas.loc[codigos[0]]
                linha.update({
                    "codigo_area": int(codigos[0]),
                    "nome_area": a["nome_area"],
                    "renda_media_total": a["renda_media_total"],
                    "renda_mediana_total": a["renda_mediana_total"],
                    "metodo_renda": "área de ponderação",
                })
            else:
                media, mediana, det = renda_ponderada(setores, setores_areas, areas, c["cd_bairro"])
                linha.update({
                    "status": "ok_media_ponderada",
                    "renda_media_total": media,
                    "renda_mediana_total": mediana,
                    "metodo_renda": "média ponderada pela população dos setores em cada área",
                })
                detalhes.append(det.assign(bairro_inct=bairro))
        elif len(candidatos) > 1:
            linha["status"] = "ambiguo"
        linhas.append(linha)
    return pd.DataFrame(linhas), (pd.concat(detalhes, ignore_index=True) if detalhes else pd.DataFrame())


# ---------------------------------------------------------------- principal

def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    populacao_inct = carregar_inct()

    baixar_agregados()
    csv_agregados = extrair_agregados()
    setores = ler_setores_poa(csv_agregados)

    areas = ler_tab83()
    composicao = ler_composicao(areas["codigo_area"])

    areas.to_csv(SAIDA / "areas_ponderacao_poa.csv", index=False, encoding="utf-8")
    composicao.to_csv(SAIDA / "setores_areas_poa.csv", index=False, encoding="utf-8")
    setores.to_csv(SAIDA / "setores_bairros_poa.csv", index=False, encoding="utf-8")

    ligacao, detalhe_renda = ligar_bairros(setores, composicao, areas, populacao_inct)
    ligacao.to_csv(SAIDA / "bairros_poa.csv", index=False, encoding="utf-8")
    detalhe_renda.to_csv(SAIDA / "bairros_renda_ponderada_detalhe.csv", index=False, encoding="utf-8")

    antigo = SAIDA / "bairros_areas_poa.csv"  # ligação antiga, por nomes das áreas
    if antigo.exists():
        antigo.unlink()

    print(f"Setores em Porto Alegre: {len(setores)} (composição: {len(composicao)})")
    print(f"Bairros do IBGE em Porto Alegre: {setores['cd_bairro'].nunique()}")
    print(f"População IBGE (setores): {int(setores['populacao'].sum())} | INCT (94 bairros): {sum(populacao_inct.values())}")
    print("Status da ligação:")
    print(ligacao["status"].value_counts().to_string())
    for r in ligacao[ligacao["status"] != "ok"].itertuples():
        print(f"  {r.bairro_inct}: {r.status}")
    diferentes = ligacao[(ligacao["status"].str.startswith("ok")) & (ligacao["populacao_ibge"] != ligacao["populacao_inct"])]
    print(f"Bairros com população diferente entre IBGE e INCT: {len(diferentes)}")


if __name__ == "__main__":
    main()
