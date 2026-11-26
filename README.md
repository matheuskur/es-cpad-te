# Projeto Enchentes — Análise de Dados do INCT SiMAI

Projeto extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS).

Repositório: https://github.com/matheuskur/es-cpad-te

## Equipe

| Nome | GitHub |
|------|--------|
| Henrique Vitor Mairesse | [hmpuc](https://github.com/hmpuc) |
| Matheus de Oliveira Kur | [matheuskur](https://github.com/matheuskur) |
| Tarciso Mota Ney da Silva | [TarcisoNey](https://github.com/TarcisoNey) |

## Dashboard

- Link público: _a definir_
- Relatório do dashboard: `relatorios/dashboard.pdf`

## Como rodar o projeto

Todos os comandos são executados a partir da raiz do projeto. É preciso ter Python 3.11 ou mais recente e acesso à internet (para o download dos agregados do IBGE e para o fundo dos mapas).

1. Clonar o repositório:

   ```bash
   git clone https://github.com/matheuskur/es-cpad-te.git
   cd es-cpad-te
   ```

2. Criar e ativar o ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. Instalar as dependências:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Preparar os dados (do original ao processado):

   ```bash
   python scripts/preparar_dados.py
   ```

   O script roda, em ordem, a limpeza do INCT, a limpeza do IBGE (baixa o ZIP de agregados, cerca de 15 MB, se ainda não existir), a limpeza do Zenodo e a geração da malha dos bairros. Ele para no primeiro erro e leva cerca de 20 segundos, mais o tempo do download na primeira vez. Os dados processados já estão versionados em `dados/processados/`, então este passo serve para reproduzir o processamento; rodá-lo gera arquivos idênticos aos do repositório. Cada etapa está descrita em [Preparação dos dados](#preparação-dos-dados).

5. Abrir o dashboard:

   ```bash
   streamlit run app/app.py
   ```

   O app abre em http://localhost:8501. Ele só lê os arquivos de `dados/processados/` e não executa os scripts de coleta e limpeza.

6. Notebooks de EDA (opcional):

   ```bash
   python -m ipykernel install --user --name=projeto-enchentes
   jupyter notebook
   ```

   Os notebooks ficam em `notebooks/exploracao/` (ver [Notebooks de exploração](#notebooks-de-exploração)).

### Organização do app

O menu fica no topo e é definido em `app/app.py` (`st.navigation`). As telas ficam em `app/paginas/` (`simulacao_inct.py` é a Tela 1 e `bases_equipe.py` é a Tela 2), a leitura dos dados processados em `app/utils/dados.py`, cores e componentes visuais em `app/utils/estilo.py` e o tema em `.streamlit/config.toml`.

## Preparação dos dados

O `scripts/preparar_dados.py` roda os quatro scripts abaixo, nesta ordem. Eles também podem ser rodados um a um.

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

### Malha dos bairros (mapas das Telas 1 e 2)

```bash
python scripts/malha_bairros.py
```

O script baixa a malha de bairros do Censo 2022 do IBGE, filtra Porto Alegre, liga cada polígono ao nome do bairro do INCT pelo `cd_bairro_ibge` de `dados/processados/IBGE/bairros_poa.csv` e salva `dados/processados/geo/bairros_poa.geojson`. Sem esse arquivo, as duas telas mostram um aviso no lugar dos mapas. Se o download falhar, baixe o `.zip` da malha no site do IBGE e passe o caminho: `python scripts/malha_bairros.py caminho/arquivo.zip`.

## Notebooks de exploração

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
│   │   ├── zenodo/       # impacto da enchente de maio/2024 na RH Guaíba
│   │   └── geo/          # malha de bairros do Censo 2022 (IBGE)
│   └── processados/      # dados limpos, separados por fonte (lidos pelo dashboard)
│       ├── INCT/
│       ├── IBGE/
│       ├── zenodo/
│       └── geo/
├── scripts/              # scripts de coleta e limpeza (preparar_dados.py roda todos)
├── notebooks/
│   └── exploracao/       # notebooks de EDA (textual e gráfica)
├── relatorios/
│   ├── base_dados.md     # fonte do relatório de levantamento de bases
│   ├── base_dados.pdf
│   ├── limpeza_dados.md  # fonte do relatório de limpeza dos dados
│   ├── limpeza_dados.pdf
│   ├── dashboard.md      # fonte do relatório do dashboard
│   ├── dashboard.pdf
│   └── img/              # capturas de tela usadas no relatório
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

### Malha de bairros (IBGE, Censo 2022)

- Arquivo: `dados/originais/geo/RS_bairros_CD2022.zip`
- Conteúdo: limites dos bairros do Rio Grande do Sul no Censo 2022; o script `scripts/malha_bairros.py` filtra Porto Alegre e liga cada polígono ao bairro do INCT pelo código do bairro do IBGE.
- Link: https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/bairros/shp/UF/RS_bairros_CD2022.zip
