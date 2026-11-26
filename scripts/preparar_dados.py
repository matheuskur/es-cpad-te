"""Prepara todos os dados usados pelo dashboard, do original ao processado.

Roda, nesta ordem, os scripts de limpeza e coleta:
1. limpeza_inct.py   -> dados/processados/INCT/
2. limpeza_ibge.py   -> dados/processados/IBGE/ (baixa o ZIP de agregados do IBGE, se faltar)
3. limpeza_zenodo.py -> dados/processados/zenodo/
4. malha_bairros.py  -> dados/processados/geo/ (usa a saída do passo 2)

Para no primeiro script que falhar. Os scripts também podem ser rodados um a um.

Como executar (a partir da pasta do projeto, com o ambiente ativado):
    python scripts/preparar_dados.py
"""

import functools
import subprocess
import sys
import time
from pathlib import Path

print = functools.partial(print, flush=True)

PASTA_SCRIPTS = Path(__file__).resolve().parent
PASTA_PROJETO = PASTA_SCRIPTS.parent

ETAPAS = [
    ("limpeza_inct.py", "Limpeza dos dados do INCT"),
    ("limpeza_ibge.py", "Limpeza dos dados do IBGE"),
    ("limpeza_zenodo.py", "Limpeza dos dados do Zenodo"),
    ("malha_bairros.py", "Malha dos bairros (mapas)"),
]


def main():
    inicio_total = time.time()
    for i, (script, descricao) in enumerate(ETAPAS, start=1):
        print(f"\n[{i}/{len(ETAPAS)}] {descricao} ({script})")
        print("-" * 60)
        inicio = time.time()
        resultado = subprocess.run([sys.executable, str(PASTA_SCRIPTS / script)], cwd=PASTA_PROJETO)
        if resultado.returncode != 0:
            sys.exit(f"\nFalhou em {script} (código {resultado.returncode}). As etapas seguintes não foram executadas.")
        print(f"-> concluído em {time.time() - inicio:.1f} s")

    print(f"\nDados prontos em dados/processados/ ({time.time() - inicio_total:.1f} s).")
    print("Para abrir o dashboard: streamlit run app/app.py")


if __name__ == "__main__":
    main()
