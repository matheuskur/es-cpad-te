"""Limpeza dos dados do INCT SiMAI.

Lê dados/originais/data_inct_original.json e gera:
- dados/processados/inct_limpo.json: formato longo (uma linha por nível e bairro),
  ordenado por nível e, dentro de cada nível, por ordem alfabética do bairro.
- dados/processados/correcoes_inct.csv: registro de cada valor alterado.

Uso (a partir da raiz do projeto):
    python scripts/limpeza_inct.py
"""

import csv
import json
import math
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGINAL = RAIZ / "dados" / "originais" / "data_inct_original.json"
SAIDA_JSON = RAIZ / "dados" / "processados" / "inct_limpo.json"
SAIDA_LOG = RAIZ / "dados" / "processados" / "correcoes_inct.csv"

# Método 1: média dos valores válidos mais próximos à esquerda e à direita.
# Chave: (bairro, nível em m) -> tipo de problema.
CORRECOES_MEDIA = {
    ("Rubem Berta", 8.8): "zero no meio de sequência crescente",
    ("Lageado", 8.1): "zero no meio de sequência crescente",
    ("Espírito Santo", 4.7): "pico isolado, seguido de queda",
}

# Método 2: interpolação linear entre os valores válidos mais próximos à esquerda e à direita.
# Usada no Centro Histórico para evitar um patamar artificial entre 9,7 m e 9,8 m.
CORRECOES_INTERPOLACAO = {
    ("Centro Histórico", 9.7): "zero no meio de sequência crescente",
    ("Centro Histórico", 9.8): "zero no meio de sequência crescente",
}

# Método 3: substituição pelo valor de um nível de referência.
# O planalto inicial de Espírito Santo (3,0 m a 3,4 m) é substituído pelo menor valor
# imediatamente seguinte a ele, que está em 3,5 m.
SUBSTITUICOES = [
    {
        "bairro": "Espírito Santo",
        "niveis": [3.0, 3.1, 3.2, 3.3, 3.4],
        "referencia_m": 3.5,
        "problema": "planalto inicial alto, sem crescimento, seguido de queda",
    },
]

# Método 4: saturação. Em todos os níveis, prédios afetados = total de prédios do bairro.
# Arquipélago: a população afetada já é 100% em todos os níveis, então os prédios afetados
# também passam a ser 100%, eliminando a oscilação da contagem (4674 a 4688).
SATURADOS = {
    "Arquipélago": "oscilação da contagem com população afetada sempre em 100%",
}


def chave_alfabetica(nome):
    """Ordena sem diferenciar acentos nem maiúsculas (ex.: 'Árvore' entre 'Arvoredo' e 'Azenha')."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.lower(), nome


def carregar():
    with open(ORIGINAL, encoding="utf-8") as f:
        raw = json.load(f)
    registros = [
        {"nivel_m": round(float(nivel.removesuffix("m").replace("_", ".")), 1), "bairro": bairro, **valores}
        for nivel, bairros in raw.items()
        for bairro, valores in bairros.items()
    ]
    registros.sort(key=lambda r: (r["nivel_m"], chave_alfabetica(r["bairro"])))
    return registros


def arredondar(x):
    """Arredonda para o inteiro mais próximo; em ,5 arredonda para cima."""
    return math.floor(x + 0.5)


def corrigir(registros):
    """Aplica as correções e devolve o registro de alterações."""
    indice = {(r["bairro"], r["nivel_m"]): r for r in registros}
    log = []

    # Níveis corrigidos por bairro: não entram como vizinhos válidos
    marcados_por_bairro = {}
    for bairro, nivel in {**CORRECOES_MEDIA, **CORRECOES_INTERPOLACAO}:
        marcados_por_bairro.setdefault(bairro, set()).add(nivel)

    def vizinhos_validos(bairro, nivel):
        validos = sorted(
            r["nivel_m"] for r in registros
            if r["bairro"] == bairro and r["nivel_m"] not in marcados_por_bairro[bairro]
        )
        esquerda = max(n for n in validos if n < nivel)
        direita = min(n for n in validos if n > nivel)
        return esquerda, direita

    # Método 1: média dos vizinhos válidos
    for (bairro, nivel), tipo in CORRECOES_MEDIA.items():
        esquerda, direita = vizinhos_validos(bairro, nivel)
        valor_esq = indice[(bairro, esquerda)]["affected_buildings"]
        valor_dir = indice[(bairro, direita)]["affected_buildings"]

        ponto = indice[(bairro, nivel)]
        original = ponto["affected_buildings"]
        novo = arredondar((valor_esq + valor_dir) / 2)
        ponto["affected_buildings"] = novo

        log.append({
            "nivel_m": nivel,
            "bairro": bairro,
            "problema": tipo,
            "metodo": "média dos vizinhos válidos",
            "affected_buildings_original": original,
            "affected_buildings_novo": novo,
            "referencias": f"{esquerda} m = {valor_esq}; {direita} m = {valor_dir}",
        })

    # Método 2: interpolação linear entre os vizinhos válidos
    for (bairro, nivel), tipo in CORRECOES_INTERPOLACAO.items():
        esquerda, direita = vizinhos_validos(bairro, nivel)
        valor_esq = indice[(bairro, esquerda)]["affected_buildings"]
        valor_dir = indice[(bairro, direita)]["affected_buildings"]

        ponto = indice[(bairro, nivel)]
        original = ponto["affected_buildings"]
        frac = (nivel - esquerda) / (direita - esquerda)
        novo = arredondar(valor_esq + (valor_dir - valor_esq) * frac)
        ponto["affected_buildings"] = novo

        log.append({
            "nivel_m": nivel,
            "bairro": bairro,
            "problema": tipo,
            "metodo": "interpolação linear entre vizinhos válidos",
            "affected_buildings_original": original,
            "affected_buildings_novo": novo,
            "referencias": f"{esquerda} m = {valor_esq}; {direita} m = {valor_dir}",
        })

    # Método 3: substituição pelo valor de um nível de referência
    for sub in SUBSTITUICOES:
        bairro = sub["bairro"]
        ref = sub["referencia_m"]
        valor_ref = indice[(bairro, ref)]["affected_buildings"]
        for nivel in sub["niveis"]:
            ponto = indice[(bairro, nivel)]
            original = ponto["affected_buildings"]
            ponto["affected_buildings"] = valor_ref
            log.append({
                "nivel_m": nivel,
                "bairro": bairro,
                "problema": sub["problema"],
                "metodo": f"substituído pelo valor de {ref} m",
                "affected_buildings_original": original,
                "affected_buildings_novo": valor_ref,
                "referencias": f"{ref} m = {valor_ref}",
            })

    # Método 4: saturação (prédios afetados = total de prédios)
    for r in registros:
        if r["bairro"] in SATURADOS and r["affected_buildings"] != r["total_buildings"]:
            original = r["affected_buildings"]
            r["affected_buildings"] = r["total_buildings"]
            log.append({
                "nivel_m": r["nivel_m"],
                "bairro": r["bairro"],
                "problema": SATURADOS[r["bairro"]],
                "metodo": "prédios afetados igualados ao total de prédios",
                "affected_buildings_original": original,
                "affected_buildings_novo": r["total_buildings"],
                "referencias": f"total_buildings = {r['total_buildings']}",
            })
    return log


def recalcular_derivados(registros):
    """Recalcula percentage e affected_population com a mesma regra usada pela fonte (teto)."""
    for r in registros:
        r["percentage"] = math.ceil(r["affected_buildings"] / r["total_buildings"] * 100)
        r["affected_population"] = math.ceil(r["population"] * r["percentage"] / 100)


def validar(registros):
    assert len(registros) == 6674, len(registros)
    assert len({(r["nivel_m"], r["bairro"]) for r in registros}) == len(registros), "duplicatas"
    for r in registros:
        assert 0 <= r["affected_buildings"] <= r["total_buildings"], r
        assert 0 <= r["percentage"] <= 100, r

    # Quedas restantes por bairro
    quedas = {}
    por_bairro = {}
    for r in registros:
        por_bairro.setdefault(r["bairro"], []).append(r)
    for bairro, pontos in por_bairro.items():
        pontos.sort(key=lambda r: r["nivel_m"])
        n = sum(1 for a, b in zip(pontos, pontos[1:]) if b["affected_buildings"] < a["affected_buildings"])
        if n:
            quedas[bairro] = n
    return quedas


def salvar(registros, log):
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SAIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    with open(SAIDA_LOG, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(log[0].keys()))
        escritor.writeheader()
        escritor.writerows(log)


def main():
    registros = carregar()
    log = corrigir(registros)
    recalcular_derivados(registros)
    quedas_restantes = validar(registros)
    salvar(registros, log)

    print(f"Registros: {len(registros)}")
    print(f"Valores corrigidos: {len(log)}")
    for item in log:
        print(f"  {item['bairro']} {item['nivel_m']} m: "
              f"{item['affected_buildings_original']} -> {item['affected_buildings_novo']} ({item['metodo']})")
    print(f"Quedas restantes por bairro: {quedas_restantes}")
    print(f"Saídas: {SAIDA_JSON} e {SAIDA_LOG}")


if __name__ == "__main__":
    main()
