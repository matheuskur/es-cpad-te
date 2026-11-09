# Projeto Enchentes — Análise de Dados do INCT SiMAI

Projeto extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS).

## Equipe

- Nome completo — matrícula — GitHub

## Dashboard

- Link público: _a definir_

## Como rodar

1. Criar e ativar o ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

2. Instalar as dependências:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Registrar o kernel do Jupyter (para os notebooks de EDA):

   ```bash
   python -m ipykernel install --user --name=projeto-enchentes
   ```

4. Iniciar o Jupyter Notebook (opcional):

   ```bash
   jupyter notebook
   ```

### Limpeza dos dados do INCT

A partir da raiz do projeto, com o ambiente ativado:

```bash
python scripts/limpeza_inct.py
```

O script lê `dados/originais/INCT/data_inct_original.json` e gera `dados/processados/INCT/inct_limpo.json` (formato longo, ordenado) e `dados/processados/INCT/correcoes_inct.csv` (cada valor alterado, com os vizinhos usados). As regras estão descritas em `relatorios/limpeza_dados.md`.

### Notebooks de exploração

Em `notebooks/exploracao/`:
- `exploracao_inct.ipynb` e `exploracao_dados_processados.ipynb`: parte textual e numérica (formato, estrutura e primeiras linhas).
- `exploracao_grafica_percentual_*.ipynb`: gráficos em percentual.
- `exploracao_grafica_quantitativa_*.ipynb`: gráficos com valores absolutos, um por bairro.

Os sufixos `_inct` e `_dados_processados` indicam os dados originais e os processados.

Os scripts de coleta e limpeza ficam em `scripts/`, o código do dashboard em `app/`, e os relatórios em `relatorios/`.

## Estrutura

```
.
├── README.md
├── requirements.txt
├── dados/
│   ├── originais/        # dados como vieram, separados por fonte
│   │   ├── INCT/         # simulação do INCT SiMAI
│   │   └── IBGE/         # tabelas e composições do Censo 2022
│   └── processados/      # dados limpos, separados por fonte
│       ├── INCT/
│       └── IBGE/
├── scripts/              # scripts de coleta e limpeza
├── notebooks/
│   └── exploracao/       # notebooks de EDA (textual e gráfica)
├── relatorios/
│   ├── base_dados.md
│   ├── limpeza_dados.md
│   └── dashboard.md
└── app/                  # código do dashboard
```

## Fontes dos dados

### Simulação do INCT SiMAI

- Arquivo: `dados/originais/INCT/data_inct_original.json` (originalmente `data.json`)
- Origem: página Flood — INCT SiMAI, http://vhlab.com.br/INCT/floods/

### Renda por pessoa (IBGE, Censo 2022)

- Tabela 8.3 (`dados/originais/IBGE/Tab8_3.xlsx`): dentro do ZIP `tabelas_xlsx.zip`
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Areas_de_Ponderacao/tabelas_xlsx.zip
- Explicação das áreas de ponderação:
  https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/47848-areas-de-ponderacao.html
- Lista de tabelas (`dados/originais/IBGE/lista_tabelas_resultados_gerais_amostra_areas_ponderacao.pdf`): fonte: IBGE, Censo 2022 (resultados gerais da amostra por área de ponderação)

### Correspondência entre áreas e bairros (IBGE)

- Agregados básicos por setor censitário (código e nome do bairro, setor e população `v0001`). O ZIP não é versionado no repositório por ser grande (cerca de 15 MB); baixe pelo link:
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip
- Composição das áreas de ponderação (`dados/originais/IBGE/composicao_areas_ponderacao_IBGE.xlsx`), que relaciona cada setor à sua área:
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Documentacao/%C3%81reas%20de%20pondera%C3%A7%C3%A3o/Composi%C3%A7%C3%A3o%20das%20%C3%81reas%20de%20Pondera%C3%A7%C3%A3o.xlsx
- Dicionário dos agregados (`dados/originais/IBGE/dicionario_agregados_setores_censitarios_20260520.xlsx`):
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx

