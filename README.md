# Projeto Enchentes — Análise de Dados do INCT SiMAI

Projeto extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS).

## Equipe

| Nome | GitHub |
|------|--------|
| Henrique Vitor Mairesse | [hmpuc](https://github.com/hmpuc) |
| Matheus de Oliveira Kur | [matheuskur](https://github.com/matheuskur) |
| Tarciso Mota Ney da Silva | [TarcisoNey](https://github.com/TarcisoNey) |

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

### Limpeza dos dados do IBGE

```bash
python scripts/limpeza_ibge.py
```

O script baixa do FTP do IBGE o ZIP de agregados por setor censitário (cerca de 15 MB), se ele ainda não existir em `dados/originais/IBGE/agregados/`. Depois, extrai o CSV, filtra Porto Alegre e gera em `dados/processados/IBGE/` a Tabela 8.3, a composição de setores, a população por setor e bairro, e a ligação entre os 94 bairros do INCT e o IBGE. As regras estão em `relatorios/limpeza_dados.md`, seção 5.

### Preparação dos dados do Zenodo (ADA RH Guaíba)

```bash
python scripts/limpeza_zenodo.py
```

O script limpa e padroniza `dados/originais/zenodo/analise_ada_rhguaiba_municipios.csv`, corrigindo tipos numéricos, cabeçalhos e pontos de milhar, gerando o arquivo tratado em `dados/processados/zenodo/analise_ada_rhguaiba_municipios.csv`. As regras estão descritas em `relatorios/limpeza_dados.md`, seção 6.

### Notebooks de exploração

Em `notebooks/exploracao/`:
- `exploracao_inct.ipynb` e `exploracao_dados_processados.ipynb`: parte textual e numérica (formato, estrutura e primeiras linhas).
- `exploracao_grafica_percentual_*.ipynb`: gráficos em percentual.
- `exploracao_grafica_quantitativa_*.ipynb`: gráficos com valores absolutos, um por bairro.
- `exploracao_ibge.ipynb`: verificação dos dados processados do IBGE (ligação dos bairros, população e renda).
- `exploracao_zenodo.ipynb`: exploração descritiva e gráfica dos dados da ADA RH Guaíba (Maio/2024).

Os sufixos `_inct` e `_dados_processados` indicam os dados originais e os processados.

Os scripts de coleta e limpeza ficam em `scripts/`, o código do dashboard em `app/`, e os relatórios em `relatorios/`.

## Estrutura

```
.
├── README.md
├── requirements.txt
├── dados/
│   ├── originais/        # dados como vieram, separados por fonte
│   │   ├── INCT/         # dados do INCT SiMAI
│   │   ├── IBGE/         # tabelas e composições do Censo 2022
│   │   └── zenodo/       # impacto da enchente de maio/2024 na RH Guaíba
│   └── processados/      # dados limpos, separados por fonte
│       ├── INCT/
│       ├── IBGE/
│       └── zenodo/
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

### Dados do INCT SiMAI

- Arquivo: `dados/originais/INCT/data_inct_original.json` (originalmente `data.json`)
- Origem: página Flood — INCT SiMAI, http://vhlab.com.br/INCT/floods/

### Renda por pessoa (IBGE, Censo 2022)

- Tabela 8.3 (`dados/originais/IBGE/Tab8_3.xlsx`): dentro do ZIP `tabelas_xlsx.zip`
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Areas_de_Ponderacao/tabelas_xlsx.zip
- Explicação das áreas de ponderação:
  https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/47848-areas-de-ponderacao.html
- Lista de tabelas (`dados/originais/IBGE/lista_tabelas_resultados_gerais_amostra_areas_ponderacao.pdf`): fonte: IBGE, Censo 2022 (resultados gerais da amostra por área de ponderação)

### Correspondência entre áreas e bairros (IBGE)

- Agregados básicos por setor censitário (código e nome do bairro, setor e população `v0001`). O ZIP não é versionado no repositório por ser grande (cerca de 15 MB). O script `scripts/limpeza_ibge.py` baixa pelo link abaixo, se o arquivo não existir em `dados/originais/IBGE/agregados/`:
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip
- Composição das áreas de ponderação (`dados/originais/IBGE/composicao_areas_ponderacao_IBGE.xlsx`), que relaciona cada setor à sua área:
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Microdados_e_Areas_de_Ponderacao/Documentacao/%C3%81reas%20de%20pondera%C3%A7%C3%A3o/Composi%C3%A7%C3%A3o%20das%20%C3%81reas%20de%20Pondera%C3%A7%C3%A3o.xlsx
- Dicionário dos agregados (`dados/originais/IBGE/dicionario_agregados_setores_censitarios_20260520.xlsx`):
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx

### Análise da Área Diretamente Afetada (ADA) da RH Guaíba (Zenodo)

- Arquivo: `dados/originais/zenodo/analise_ada_rhguaiba_municipios.csv`
- Versão: v0.4
- Conteúdo: Dados municipais consolidados do impacto das inundações de maio de 2024 na Região Hidrográfica do Guaíba (139 municípios), abrangendo população e domicílios afetados, áreas urbanas e rurais inundadas, vias atingidas e equipamentos públicos.
- Link: https://zenodo.org/records/11177244?preview_file=analise_ada_rhguaiba_municipios.csv

