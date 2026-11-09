"""Limpeza e preparação dos dados do Zenodo (ADA RH Guaíba).

Lê o CSV original, padroniza as colunas (snake_case), corrige o erro de digitação do cabeçalho,
restaura a escala inteira correta para as colunas com pontos de milhar exportados como float,
e preserva colunas vazias estritamente sem valor (para conversão automática para null/NaN).

Arquivo de entrada:
- dados/originais/zenodo/analise_ada_rhguaiba_municipios.csv

Arquivo de saída:
- dados/processados/zenodo/analise_ada_rhguaiba_municipios.csv

Como executar (a partir da pasta do projeto):
    python scripts/limpeza_zenodo.py
"""

import csv
from pathlib import Path


# ---------------------------------------------------------------------------
# Onde estão os arquivos
# ---------------------------------------------------------------------------
PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_ORIGINAIS = PASTA_PROJETO / "dados" / "originais" / "zenodo"
PASTA_PROCESSADOS = PASTA_PROJETO / "dados" / "processados" / "zenodo"

NOME_ARQUIVO = "analise_ada_rhguaiba_municipios.csv"
ARQUIVO_ORIGEM = PASTA_ORIGINAIS / NOME_ARQUIVO
ARQUIVO_DESTINO = PASTA_PROCESSADOS / NOME_ARQUIVO

# Mapeamento e padronização dos nomes das colunas (snake_case e correção de typo)
MAPA_COLUNAS = {
    "CD_MUN": "cd_mun",
    "NM_MUN": "nm_mun",
    "Pessoas_afetadas": "pessoas_afetadas",
    "Domicilios_afetados": "domicilios_afetados",
    "Pessoas_%": "pessoas_pct",
    "Domicilios_%": "domicilios_pct",
    "Pessoas_2022": "pessoas_2022",
    "Domicilios_2022": "domicilios_2022",
    "Vias_Diretamente_Afetadas_m": "vias_diretamente_afetadas_m",
    "Vias_Diretamente_Afetadas_km": "vias_diretamente_afetadas_km",
    "Area_Municpio_m2": "area_municipio_m2",  # Corrige typo da fonte original
    "Area_Urbana_m2": "area_urbana_m2",
    "Area_NaoUrbana_m2": "area_nao_urbana_m2",
    "Area_Diretamente_Afetada_Municipio_m2": "area_diretamente_afetada_municipio_m2",
    "Area_Diretamente_Afetada_Municipio_%": "area_diretamente_afetada_municipio_pct",
    "Area_Diretamente_Afetada_Urbana_m2": "area_diretamente_afetada_urbana_m2",
    "Area_Diretamente_Afetada_Urbana_%": "area_diretamente_afetada_urbana_pct",
    "Estruturas_Afetadas_nro": "estruturas_afetadas_nro",
    "Area_Construida_Afetada_m2": "area_construida_afetada_m2",
    "Domicilios_Particulares_Afetados_Diretamente": "domicilios_particulares_afetados_diretamente",
    "Domicilios_Coletivos_Afetados_Diretamente": "domicilios_coletivos_afetados_diretamente",
    "Estabelecim_Agropecuario_Afetados_Diretamente": "estabelecim_agropecuario_afetados_diretamente",
    "Estabelecim_Ensino_Afetados_Diretamente": "estabelecim_ensino_afetados_diretamente",
    "Estabelecim_Saude_Afetados_Diretamente": "estabelecim_saude_afetados_diretamente",
    "Edificacao_Construcao_Afetados_Diretamente": "edificacao_construcao_afetados_diretamente",
    "Estabelecim_Religiosos_Afetados_Diretamente": "estabelecim_religiosos_afetados_diretamente",
}

COLUNAS_FLOAT = {
    "pessoas_pct",
    "domicilios_pct",
    "vias_diretamente_afetadas_km",
    "area_diretamente_afetada_municipio_pct",
    "area_diretamente_afetada_urbana_pct",
}


def limpar_valor(coluna: str, valor: str | None) -> str:
    """Limpa e normaliza um valor. Se ausente/nulo, retorna string vazia (sem nada)."""
    if valor is None:
        return ""

    valor = valor.strip().strip('"')
    if valor == "" or valor.lower() in ("nan", "null"):
        return ""

    # Correção do ponto de milhar exportado como decimal (ex.: '63.788' -> 63788, '34.4' -> 34400)
    if coluna in (
        "domicilios_particulares_afetados_diretamente",
        "edificacao_construcao_afetados_diretamente",
    ):
        if "." in valor:
            return str(int(round(float(valor) * 1000)))
        return str(int(valor))

    # Colunas com valores decimais/percentuais
    if coluna in COLUNAS_FLOAT:
        return str(float(valor))

    # Identificadores e nomes
    if coluna in ("cd_mun", "nm_mun"):
        return valor

    # Demais colunas numéricas (inteiros)
    return str(int(float(valor)))


def limpar_zenodo():
    if not ARQUIVO_ORIGEM.exists():
        raise FileNotFoundError(f"Arquivo original não encontrado: {ARQUIVO_ORIGEM}")

    PASTA_PROCESSADOS.mkdir(parents=True, exist_ok=True)

    with open(ARQUIVO_ORIGEM, "r", encoding="utf-8") as f_in:
        leitor = csv.DictReader(f_in)
        linhas_limpas = []
        for linha in leitor:
            registro_limpo = {}
            for col_orig, col_dest in MAPA_COLUNAS.items():
                registro_limpo[col_dest] = limpar_valor(col_dest, linha.get(col_orig))
            linhas_limpas.append(registro_limpo)

    colunas_saida = list(MAPA_COLUNAS.values())
    with open(ARQUIVO_DESTINO, "w", encoding="utf-8", newline="") as f_out:
        escritor = csv.DictWriter(f_out, fieldnames=colunas_saida)
        escritor.writeheader()
        escritor.writerows(linhas_limpas)

    print("Limpeza dos dados do Zenodo concluída com sucesso!")
    print(f"- Origem:  {ARQUIVO_ORIGEM}")
    print(f"- Destino: {ARQUIVO_DESTINO}")
    print(f"- Total de municípios processados: {len(linhas_limpas)}")
    print(f"- Total de colunas: {len(colunas_saida)}")


def main():
    limpar_zenodo()


if __name__ == "__main__":
    main()
