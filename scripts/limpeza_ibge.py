"""Limpeza dos dados do IBGE (Censo 2022) para Porto Alegre.

O script liga cada um dos 94 bairros do INCT a um bairro do IBGE e calcula a renda
de cada bairro a partir das áreas de ponderação (Tabela 8.3).

Arquivos usados (pasta dados/originais/IBGE/):
- Tab8_3.xlsx: renda por área de ponderação.
- composicao_areas_ponderacao_IBGE.xlsx: a qual área pertence cada setor.
- agregados por setor (ZIP do IBGE): a qual bairro pertence cada setor.
  Se o ZIP não existir, o script baixa do site do IBGE.

Arquivos gerados (pasta dados/processados/IBGE/):
- areas_ponderacao_poa.csv: Tabela 8.3 só com Porto Alegre.
- setores_areas_poa.csv: setor e área de ponderação.
- setores_bairros_poa.csv: setor, bairro e população.
- bairros_poa.csv: os 94 bairros do INCT, com população e renda.
- bairros_renda_ponderada_detalhe.csv: pesos das áreas dos bairros que estão em duas áreas.

Como executar (a partir da pasta do projeto):
    python scripts/limpeza_ibge.py
"""

import json
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# Onde estão os arquivos
# ---------------------------------------------------------------------------
PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_IBGE = PASTA_PROJETO / "dados" / "originais" / "IBGE"
PASTA_AGREGADOS = PASTA_IBGE / "agregados"
ZIP_AGREGADOS = PASTA_AGREGADOS / "Agregados_por_setores_basico_BR_20260520.zip"
CSV_AGREGADOS = PASTA_AGREGADOS / "Agregados_por_setores_basico_BR.csv"
URL_AGREGADOS = (
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/"
    "Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip"
)
ARQUIVO_TABELA_83 = PASTA_IBGE / "Tab8_3.xlsx"
ARQUIVO_COMPOSICAO = PASTA_IBGE / "composicao_areas_ponderacao_IBGE.xlsx"
ARQUIVO_INCT = PASTA_PROJETO / "dados" / "originais" / "INCT" / "data_inct_original.json"
PASTA_SAIDA = PASTA_PROJETO / "dados" / "processados" / "IBGE"

CODIGO_PORTO_ALEGRE = "4314902"
LINHAS_DE_CABECALHO_DA_TABELA = 4  # duas de título e duas de cabeçalho

# Alguns bairros têm grafia diferente no INCT e no IBGE: nome no INCT -> nome no IBGE
NOMES_DIFERENTES = {
    "Passo D'Areia": "Passo da Areia",
    "Menino Deus": "Menino-Deus",
}

# Colunas do arquivo bairros_poa.csv, nessa ordem
COLUNAS_DOS_BAIRROS = [
    "bairro_inct", "populacao_inct", "status", "cd_bairro_ibge", "nome_bairro_ibge",
    "setores", "populacao_ibge", "areas", "n_areas", "codigo_area", "nome_area",
    "renda_media_total", "renda_mediana_total", "metodo_renda",
]


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def nome_para_comparar(nome):
    """Deixa o nome de um bairro pronto para comparação.

    Tira acentos, passa para minúsculas e troca hífen e apóstrofo por espaço ou nada.
    Ex.: 'Menino-Deus' e 'menino deus' viram o mesmo texto.
    """
    texto = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().replace("-", " ").replace("'", "")
    return " ".join(texto.split())


# ---------------------------------------------------------------------------
# Leitura dos arquivos
# ---------------------------------------------------------------------------

def baixar_agregados():
    """Baixa o ZIP de agregados do IBGE, se ele ainda não estiver no computador."""
    if ZIP_AGREGADOS.exists():
        return
    PASTA_AGREGADOS.mkdir(parents=True, exist_ok=True)
    print("Baixando o ZIP de agregados do IBGE (cerca de 15 MB)...")
    resposta = requests.get(URL_AGREGADOS, timeout=300)
    resposta.raise_for_status()
    ZIP_AGREGADOS.write_bytes(resposta.content)


def extrair_agregados():
    """Extrai o CSV de dentro do ZIP, se ele ainda não estiver extraído."""
    if not CSV_AGREGADOS.exists():
        with zipfile.ZipFile(ZIP_AGREGADOS) as arquivo_zip:
            arquivo_zip.extract(CSV_AGREGADOS.name, PASTA_AGREGADOS)


def ler_inct():
    """Devolve um dicionário: nome do bairro -> população (INCT)."""
    with open(ARQUIVO_INCT, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    primeiro_nivel = dados["3_0m"]
    return {bairro: valores["population"] for bairro, valores in primeiro_nivel.items()}


def ler_tabela_83():
    """Lê a Tabela 8.3 e devolve só as áreas de Porto Alegre."""
    nomes_das_colunas = [
        "codigo_municipio", "nome_municipio", "codigo_area", "nome_area",
        "pessoas_total", "pessoas_homens", "pessoas_mulheres",
        "renda_media_total", "renda_media_homens", "renda_media_mulheres",
        "renda_mediana_total", "renda_mediana_homens", "renda_mediana_mulheres",
    ]
    tabela = pd.read_excel(
        ARQUIVO_TABELA_83, header=None, skiprows=LINHAS_DE_CABECALHO_DA_TABELA,
        names=nomes_das_colunas, dtype=object,
    )
    tabela = tabela.dropna(subset=["codigo_area"])
    tabela = tabela[tabela["codigo_municipio"] == int(CODIGO_PORTO_ALEGRE)].copy()

    tabela["codigo_area"] = tabela["codigo_area"].astype("int64")
    for coluna in nomes_das_colunas[4:]:
        tabela[coluna] = pd.to_numeric(tabela[coluna])
    return tabela.reset_index(drop=True)


def ler_setores_e_areas():
    """Lê a composição: qual área de ponderação tem cada setor de Porto Alegre."""
    composicao = pd.read_excel(ARQUIVO_COMPOSICAO, dtype=str)
    # A coluna do nome do município vem com erro de digitação na planilha; não é usada
    composicao.columns = ["setor", "codigo_municipio", "codigo_area", "nome_municipio"]
    composicao = composicao[composicao["codigo_municipio"] == CODIGO_PORTO_ALEGRE].copy()
    composicao["codigo_area"] = composicao["codigo_area"].astype("int64")
    return composicao[["setor", "codigo_area"]].reset_index(drop=True)


def ler_setores_com_bairro():
    """Lê o CSV de agregados e devolve os setores de Porto Alegre, com bairro e população."""
    tabela = pd.read_csv(
        CSV_AGREGADOS, sep=";", encoding="latin-1", dtype=str,
        usecols=["CD_SETOR", "CD_MUN", "CD_BAIRRO", "NM_BAIRRO", "v0001"],
    )
    tabela = tabela[tabela["CD_MUN"] == CODIGO_PORTO_ALEGRE].copy()
    tabela["populacao"] = pd.to_numeric(tabela["v0001"])

    setores = tabela.rename(columns={
        "CD_SETOR": "setor", "CD_BAIRRO": "cd_bairro", "NM_BAIRRO": "nome_bairro",
    })
    return setores[["setor", "cd_bairro", "nome_bairro", "populacao"]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Renda dos bairros
# ---------------------------------------------------------------------------

def renda_de_duas_areas(setores, setores_areas, tabela_83, cd_bairro):
    """Calcula a renda de um bairro que está em mais de uma área.

    Cada área pesa de acordo com a população dos setores do bairro que estão nela.
    Devolve: (renda média, renda mediana aproximada, tabela com os pesos).
    """
    setores_do_bairro = setores[setores["cd_bairro"] == cd_bairro]
    juntos = setores_do_bairro.merge(setores_areas, on="setor")
    populacao_por_area = juntos.groupby("codigo_area")["populacao"].sum()
    total = populacao_por_area.sum()

    renda_media = 0.0
    renda_mediana = 0.0
    detalhe = []
    for codigo_area, populacao in populacao_por_area.items():
        area = tabela_83[tabela_83["codigo_area"] == codigo_area].iloc[0]
        peso = populacao / total
        renda_media += peso * area["renda_media_total"]
        renda_mediana += peso * area["renda_mediana_total"]
        detalhe.append({
            "codigo_area": codigo_area,
            "populacao": populacao,
            "nome_area": area["nome_area"],
            "renda_media_total": area["renda_media_total"],
            "renda_mediana_total": area["renda_mediana_total"],
            "peso": peso,
        })
    return renda_media, renda_mediana, pd.DataFrame(detalhe)


# ---------------------------------------------------------------------------
# Ligação entre os bairros do INCT e os bairros do IBGE
# ---------------------------------------------------------------------------

def ligar_bairros(populacao_inct, setores, setores_areas, tabela_83):
    """Cria uma linha para cada bairro do INCT, com a ligação ao IBGE e a renda."""
    # Lista dos bairros do IBGE, com a população somada dos setores de cada um
    bairros_ibge = setores.groupby(["cd_bairro", "nome_bairro"], as_index=False).agg(
        setores=("setor", "count"), populacao_ibge=("populacao", "sum"),
    )
    bairros_ibge["nome_comparar"] = bairros_ibge["nome_bairro"].apply(nome_para_comparar)

    # Áreas de ponderação de cada bairro do IBGE, a partir dos seus setores
    setores_com_area = setores.merge(setores_areas, on="setor")

    linhas = []
    detalhes = []
    for bairro_inct, populacao in populacao_inct.items():
        nome_no_ibge = NOMES_DIFERENTES.get(bairro_inct, bairro_inct)
        encontrados = bairros_ibge[bairros_ibge["nome_comparar"] == nome_para_comparar(nome_no_ibge)]

        linha = {coluna: None for coluna in COLUNAS_DOS_BAIRROS}
        linha["bairro_inct"] = bairro_inct
        linha["populacao_inct"] = populacao
        linha["status"] = "sem_correspondencia"

        if len(encontrados) > 1:
            linha["status"] = "ambiguo"
            linhas.append(linha)
            continue
        if len(encontrados) == 0:
            linhas.append(linha)
            continue

        bairro = encontrados.iloc[0]
        cd_bairro = bairro["cd_bairro"]
        areas_do_bairro = sorted(
            setores_com_area[setores_com_area["cd_bairro"] == cd_bairro]["codigo_area"].unique()
        )

        linha["status"] = "ok"
        linha["cd_bairro_ibge"] = cd_bairro
        linha["nome_bairro_ibge"] = bairro["nome_bairro"]
        linha["setores"] = int(bairro["setores"])
        linha["populacao_ibge"] = int(bairro["populacao_ibge"])
        linha["areas"] = "; ".join(str(area) for area in areas_do_bairro)
        linha["n_areas"] = len(areas_do_bairro)

        if len(areas_do_bairro) == 1:
            # Caso comum: o bairro está em uma só área, então recebe a renda dela
            area = tabela_83[tabela_83["codigo_area"] == areas_do_bairro[0]].iloc[0]
            linha["codigo_area"] = str(int(area["codigo_area"]))
            linha["nome_area"] = area["nome_area"]
            linha["renda_media_total"] = area["renda_media_total"]
            linha["renda_mediana_total"] = area["renda_mediana_total"]
            linha["metodo_renda"] = "área de ponderação"
        else:
            # Bairro em duas ou mais áreas: média das áreas, ponderada pela população
            media, mediana, detalhe = renda_de_duas_areas(setores, setores_areas, tabela_83, cd_bairro)
            linha["status"] = "ok_media_ponderada"
            linha["renda_media_total"] = media
            linha["renda_mediana_total"] = mediana
            linha["metodo_renda"] = "média ponderada pela população dos setores em cada área"
            detalhes.append(detalhe.assign(bairro_inct=bairro_inct))

        linhas.append(linha)

    tabela_bairros = pd.DataFrame(linhas, columns=COLUNAS_DOS_BAIRROS)
    if detalhes:
        tabela_detalhe = pd.concat(detalhes, ignore_index=True)
    else:
        tabela_detalhe = pd.DataFrame()
    return tabela_bairros, tabela_detalhe


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    # 1) Dados do IBGE para Porto Alegre
    baixar_agregados()
    extrair_agregados()
    setores = ler_setores_com_bairro()
    tabela_83 = ler_tabela_83()
    setores_areas = ler_setores_e_areas()

    tabela_83.to_csv(PASTA_SAIDA / "areas_ponderacao_poa.csv", index=False, encoding="utf-8")
    setores_areas.to_csv(PASTA_SAIDA / "setores_areas_poa.csv", index=False, encoding="utf-8")
    setores.to_csv(PASTA_SAIDA / "setores_bairros_poa.csv", index=False, encoding="utf-8")

    # 2) Ligação com os bairros do INCT
    populacao_inct = ler_inct()
    bairros, detalhe = ligar_bairros(populacao_inct, setores, setores_areas, tabela_83)
    bairros.to_csv(PASTA_SAIDA / "bairros_poa.csv", index=False, encoding="utf-8")
    detalhe.to_csv(PASTA_SAIDA / "bairros_renda_ponderada_detalhe.csv", index=False, encoding="utf-8")

    # 3) Resumo na tela
    print(f"Setores de Porto Alegre: {len(setores)}")
    print(f"Bairros do IBGE: {setores['cd_bairro'].nunique()}")
    print(f"População dos setores: {int(setores['populacao'].sum())}")
    print("Situação da ligação:")
    print(bairros["status"].value_counts().to_string())


if __name__ == "__main__":
    main()
