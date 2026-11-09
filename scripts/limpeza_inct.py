"""Limpeza dos dados do INCT SiMAI.

Lê o JSON original e grava:
- dados/processados/INCT/inct_limpo.json: uma linha por nível e bairro, ordenada.
- dados/processados/INCT/correcoes_inct.csv: cada valor alterado e o motivo.

Como executar (a partir da pasta do projeto):
    python scripts/limpeza_inct.py
"""

import csv
import json
import math
import unicodedata
from pathlib import Path


# ---------------------------------------------------------------------------
# Onde estão os arquivos
# ---------------------------------------------------------------------------
PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_ORIGINAL = PASTA_PROJETO / "dados" / "originais" / "INCT" / "data_inct_original.json"
ARQUIVO_LIMPO = PASTA_PROJETO / "dados" / "processados" / "INCT" / "inct_limpo.json"
ARQUIVO_CORRECOES = PASTA_PROJETO / "dados" / "processados" / "INCT" / "correcoes_inct.csv"


# ---------------------------------------------------------------------------
# Quais valores corrigir, e como
# ---------------------------------------------------------------------------

# 1) Média dos vizinhos: o valor vira a média do valor válido mais próximo
#    à esquerda e do valor válido mais próximo à direita.
#    Formato: (bairro, nível em m): motivo
PONTOS_PELA_MEDIA = {
    ("Rubem Berta", 8.8): "zero no meio de sequência crescente",
    ("Lageado", 8.1): "zero no meio de sequência crescente",
    ("Espírito Santo", 4.7): "pico isolado, seguido de queda",
}

# 2) Interpolação: o valor fica no meio do caminho entre os vizinhos válidos,
#    de forma proporcional à distância. Evita que dois níveis fiquem iguais.
PONTOS_POR_INTERPOLACAO = {
    ("Centro Histórico", 9.7): "zero no meio de sequência crescente",
    ("Centro Histórico", 9.8): "zero no meio de sequência crescente",
}

# 3) Substituição: o planalto inicial do Espírito Santo recebe o valor do nível 3,5 m.
PLANALTO = {
    "bairro": "Espírito Santo",
    "niveis": [3.0, 3.1, 3.2, 3.3, 3.4],
    "nivel_de_referencia": 3.5,
    "motivo": "planalto inicial alto, sem crescimento, seguido de queda",
}

# 4) Saturação: em todos os níveis, prédios afetados = total de prédios.
BAIRRO_SATURADO = "Arquipélago"
MOTIVO_SATURADO = "oscilação da contagem com população afetada sempre em 100%"


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def sem_acentos(texto):
    """Tira os acentos de um texto. Ex.: 'Arquipélago' -> 'Arquipelago'."""
    texto = unicodedata.normalize("NFKD", texto)
    return texto.encode("ascii", "ignore").decode("ascii")


def arredondar_meio_para_cima(numero):
    """Arredonda para o inteiro mais próximo. Quando termina em ,5, sobe. Ex.: 268,5 -> 269."""
    return math.floor(numero + 0.5)


def ler_dados_originais():
    """Lê o JSON original e devolve uma lista de registros, um por nível e bairro."""
    with open(ARQUIVO_ORIGINAL, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    registros = []
    for nivel_texto, bairros in dados.items():
        # "3_0m" vira 3.0
        nivel = float(nivel_texto.removesuffix("m").replace("_", "."))
        for bairro, valores in bairros.items():
            registro = {"nivel_m": round(nivel, 1), "bairro": bairro}
            registro.update(valores)
            registros.append(registro)

    # Ordena por nível e, dentro do nível, por nome do bairro (sem acentos)
    registros.sort(key=lambda r: (r["nivel_m"], sem_acentos(r["bairro"]).lower()))
    return registros


def achar_registro(registros, bairro, nivel):
    """Devolve o registro de um bairro em um nível."""
    for registro in registros:
        if registro["bairro"] == bairro and registro["nivel_m"] == nivel:
            return registro
    raise ValueError(f"não encontrei {bairro} em {nivel} m")


def achar_vizinhos_validos(registros, bairro, nivel, niveis_corrigidos):
    """Devolve (nível à esquerda, nível à direita) mais próximos que não foram corrigidos."""
    niveis_do_bairro = [
        r["nivel_m"] for r in registros
        if r["bairro"] == bairro and r["nivel_m"] not in niveis_corrigidos
    ]
    esquerda = max(n for n in niveis_do_bairro if n < nivel)
    direita = min(n for n in niveis_do_bairro if n > nivel)
    return esquerda, direita


def nova_linha_de_log(bairro, nivel, problema, metodo, original, novo, referencias):
    """Cria uma linha para o arquivo de correções."""
    return {
        "nivel_m": nivel,
        "bairro": bairro,
        "problema": problema,
        "metodo": metodo,
        "affected_buildings_original": original,
        "affected_buildings_novo": novo,
        "referencias": referencias,
    }


# ---------------------------------------------------------------------------
# Correções
# ---------------------------------------------------------------------------

def corrigir(registros):
    """Aplica as correções nos registros e devolve a lista de alterações."""
    log = []

    # Níveis que serão corrigidos, por bairro. Eles não podem ser vizinhos válidos.
    corrigidos_por_bairro = {}
    for bairro, nivel in list(PONTOS_PELA_MEDIA) + list(PONTOS_POR_INTERPOLACAO):
        corrigidos_por_bairro.setdefault(bairro, set()).add(nivel)

    # --- 1) Média dos vizinhos ---
    for (bairro, nivel), motivo in PONTOS_PELA_MEDIA.items():
        niveis_corrigidos = corrigidos_por_bairro[bairro]
        esquerda, direita = achar_vizinhos_validos(registros, bairro, nivel, niveis_corrigidos)
        valor_esquerda = achar_registro(registros, bairro, esquerda)["affected_buildings"]
        valor_direita = achar_registro(registros, bairro, direita)["affected_buildings"]

        registro = achar_registro(registros, bairro, nivel)
        original = registro["affected_buildings"]
        novo = arredondar_meio_para_cima((valor_esquerda + valor_direita) / 2)
        registro["affected_buildings"] = novo

        log.append(nova_linha_de_log(
            bairro, nivel, motivo, "média dos vizinhos válidos", original, novo,
            f"{esquerda} m = {valor_esquerda}; {direita} m = {valor_direita}",
        ))

    # --- 2) Interpolação ---
    for (bairro, nivel), motivo in PONTOS_POR_INTERPOLACAO.items():
        niveis_corrigidos = corrigidos_por_bairro[bairro]
        esquerda, direita = achar_vizinhos_validos(registros, bairro, nivel, niveis_corrigidos)
        valor_esquerda = achar_registro(registros, bairro, esquerda)["affected_buildings"]
        valor_direita = achar_registro(registros, bairro, direita)["affected_buildings"]

        # Parte do caminho entre os vizinhos: 0 no vizinho da esquerda, 1 no da direita
        parte = (nivel - esquerda) / (direita - esquerda)
        novo = arredondar_meio_para_cima(valor_esquerda + (valor_direita - valor_esquerda) * parte)

        registro = achar_registro(registros, bairro, nivel)
        original = registro["affected_buildings"]
        registro["affected_buildings"] = novo

        log.append(nova_linha_de_log(
            bairro, nivel, motivo, "interpolação linear entre vizinhos válidos", original, novo,
            f"{esquerda} m = {valor_esquerda}; {direita} m = {valor_direita}",
        ))

    # --- 3) Substituição do planalto ---
    valor_referencia = achar_registro(
        registros, PLANALTO["bairro"], PLANALTO["nivel_de_referencia"]
    )["affected_buildings"]
    for nivel in PLANALTO["niveis"]:
        registro = achar_registro(registros, PLANALTO["bairro"], nivel)
        original = registro["affected_buildings"]
        registro["affected_buildings"] = valor_referencia

        log.append(nova_linha_de_log(
            PLANALTO["bairro"], nivel, PLANALTO["motivo"],
            f"substituído pelo valor de {PLANALTO['nivel_de_referencia']} m",
            original, valor_referencia,
            f"{PLANALTO['nivel_de_referencia']} m = {valor_referencia}",
        ))

    # --- 4) Saturação: prédios afetados = total de prédios ---
    for registro in registros:
        if registro["bairro"] != BAIRRO_SATURADO:
            continue
        if registro["affected_buildings"] == registro["total_buildings"]:
            continue

        original = registro["affected_buildings"]
        registro["affected_buildings"] = registro["total_buildings"]
        log.append(nova_linha_de_log(
            BAIRRO_SATURADO, registro["nivel_m"], MOTIVO_SATURADO,
            "prédios afetados igualados ao total de prédios",
            original, registro["total_buildings"],
            f"total_buildings = {registro['total_buildings']}",
        ))

    return log


def recalcular_percentual_e_populacao(registros):
    """Recalcula percentage e affected_population pela mesma regra usada na fonte.

    percentage = teto de (prédios afetados / total de prédios * 100)
    affected_population = teto de (população * percentage / 100)
    """
    for registro in registros:
        percentual = registro["affected_buildings"] / registro["total_buildings"] * 100
        registro["percentage"] = math.ceil(percentual)
        registro["affected_population"] = math.ceil(
            registro["population"] * registro["percentage"] / 100
        )


def verificar(registros):
    """Confere se os dados fazem sentido. Se algo estiver errado, o script para aqui."""
    assert len(registros) == 6674, "deveriam existir 6674 registros"
    for registro in registros:
        assert 0 <= registro["affected_buildings"] <= registro["total_buildings"]
        assert 0 <= registro["percentage"] <= 100


def contar_quedas(registros):
    """Conta quantas vezes a quantidade de prédios afetados cai de um nível para o seguinte."""
    quedas = {}
    for bairro in sorted({r["bairro"] for r in registros}):
        pontos = sorted(
            (r for r in registros if r["bairro"] == bairro), key=lambda r: r["nivel_m"]
        )
        contagem = 0
        for anterior, atual in zip(pontos, pontos[1:]):
            if atual["affected_buildings"] < anterior["affected_buildings"]:
                contagem += 1
        if contagem > 0:
            quedas[bairro] = contagem
    return quedas


def salvar(registros, log):
    """Grava o JSON limpo e o arquivo de correções."""
    ARQUIVO_LIMPO.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_LIMPO, "w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)

    with open(ARQUIVO_CORRECOES, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(log[0].keys()))
        escritor.writeheader()
        escritor.writerows(log)


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    registros = ler_dados_originais()
    log = corrigir(registros)
    recalcular_percentual_e_populacao(registros)
    verificar(registros)
    salvar(registros, log)

    print(f"Registros: {len(registros)}")
    print(f"Valores corrigidos: {len(log)}")
    for item in log:
        print(f"  {item['bairro']} {item['nivel_m']} m: "
              f"{item['affected_buildings_original']} -> {item['affected_buildings_novo']} "
              f"({item['metodo']})")
    print(f"Quedas restantes: {contar_quedas(registros)}")
    print(f"Arquivos gerados: {ARQUIVO_LIMPO} e {ARQUIVO_CORRECOES}")


if __name__ == "__main__":
    main()
