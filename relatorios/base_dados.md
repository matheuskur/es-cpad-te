# Relatório: Levantamento de bases

Data: 08/11/2026

Este relatório descreve as bases escolhidas para o projeto, o que cada uma contém, como elas se conectam e o que ainda está pendente. As contagens foram feitas diretamente nos arquivos em `dados/originais/`.

## 1. Objetivo do levantamento

Cruzar os níveis de inundação dos dados do INCT SiMAI para o Guaíba com a população e a renda dos bairros de Porto Alegre. Para isso, são necessárias três coisas: os dados de inundação do INCT, a renda da população e uma ponte entre os bairros do INCT e as unidades do IBGE.

## 2. Bases escolhidas

| # | Base | Arquivo | Unidade de análise | Papel no projeto |
|---|------|---------|--------------------|------------------|
| 1 | Dados do INCT SiMAI | `INCT/data_inct_original.json` | nível do Guaíba × bairro | Variável de inundação (edificações e pessoas afetadas) |
| 2 | Tabela 8.3 do Censo 2022 (renda domiciliar per capita) | `IBGE/Tab8_3.xlsx` | área de ponderação | Renda média e mediana |
| 3 | Composição das áreas de ponderação | `IBGE/composicao_areas_ponderacao_IBGE.xlsx` | setor censitário → área de ponderação | Ponte entre setores e áreas de renda |
| 4 | Dicionário dos agregados por setor censitário | `IBGE/dicionario_agregados_setores_censitarios_20260520.xlsx` | variável | Documentação das variáveis do IBGE (ex.: `V0001`, total de pessoas) |
| 5 | Lista de tabelas de resultados gerais da amostra | `IBGE/lista_tabelas_resultados_gerais_amostra_areas_ponderacao.pdf` | tabela | Catálogo que confirma o título e o tema da Tabela 8.3 |
| 6 | Agregados básicos por setor censitário | ZIP baixado por `scripts/limpeza_ibge.py` (cerca de 15 MB, fora do git) | setor censitário → bairro | Ponte entre setores e bairros de Porto Alegre |
| 7 | Análise da Área Diretamente Afetada (ADA) da RH Guaíba | `zenodo/analise_ada_rhguaiba_municipios.csv` | município | Dados reais do evento de maio/2024 para validação empírica e contexto regional |

## 3. Detalhamento das bases

### 3.1 Dados do INCT SiMAI (`INCT/data_inct_original.json`)

- **Formato:** JSON aninhado, organizado como nível → bairro → métricas.
- **Níveis:** 71 chaves, de `3_0m` a `10_0m`, com passo de 0,1 m. Cada nível é uma cota do Guaíba (conforme a nota do notebook de exploração).
- **Bairros:** 94 por nível, todos com o mesmo conjunto de nomes em cada um dos 71 níveis.
- **Registros:** 6.674 linhas após transformar o JSON em formato longo (`notebooks/exploracao/exploracao_inct.ipynb`).
- **Variáveis:**
  - `affected_buildings`: edificações afetadas;
  - `total_buildings`: total de edificações;
  - `percentage`: percentual de edificações afetadas;
  - `population`: população;
  - `affected_population`: população afetada.
- **Qualidade básica:** nenhum valor nulo, nenhuma duplicata de (nível, bairro), nenhum bairro com mais edificações ou pessoas afetadas do que o total.
- **Totais estáveis:** `total_buildings` e `population` não mudam entre os níveis para o mesmo bairro. Somados, dão 486.389 edificações e 1.332.845 pessoas.
- **Regra do `percentage`:** o valor é `teto(affected_buildings / total_buildings × 100)` em todas as 6.674 linhas. Um arredondamento comum divergiria em 1.295 linhas, então o critério deve ser documentado.
- **Impacto no nível de 10 m:** 101.211 edificações afetadas (20,8% do total) e 274.993 pessoas afetadas (20,6% da população).

**Achados que precisam de confirmação com a equipe do INCT:**

- O comportamento não é monotônico em alguns bairros: a quantidade de edificações afetadas cai ao subir o nível em 5 bairros (Arquipélago, com 6 quedas; Espírito Santo, com 3; Centro Histórico, Lageado e Rubem Berta, com 1 cada).
- A população afetada cai no total de 264.338 (nível 9,6 m) para 252.080 (nível 9,7 m). Isso ocorre em 4 bairros (Espírito Santo, Centro Histórico, Lageado e Rubem Berta).
- Não é possível dizer, só pelos dados, se isso é uma característica da base ou um erro de processamento.

**Documentação da fonte:**

- O link da página Flood do INCT está no `README.md`.
- Segundo o enunciado, `total_buildings` vem do OpenStreetMap e `population`, do Censo IBGE 2022. A população de cada bairro bate exatamente com a soma dos setores censitários do IBGE (ver `relatorios/limpeza_dados.md`, seção 5).

### 3.2 Tabela 8.3 do Censo 2022 (`IBGE/Tab8_3.xlsx`)

- **Conteúdo:** valor do rendimento domiciliar mensal per capita, médio e mediano, dos moradores em domicílios particulares permanentes ocupados. Exclui moradores cuja condição era pensionista, empregado(a) doméstico(a) ou parente de empregado(a) doméstico(a).
- **Recorte:** a planilha cobre o Brasil e tem 5.570 municípios. Porto Alegre (código 4314902) aparece em 46 áreas de ponderação.
- **Colunas:** pessoas (total, homens e mulheres), renda média (total, homens e mulheres) e renda mediana (total, homens e mulheres). Antes dos dados, há duas linhas de título e duas de cabeçalho.
- **Porto Alegre:**
  - 1.321.927 pessoas, no universo da tabela;
  - renda média por área entre R$ 1.025,84 (Restinga Velha e Pitinga) e R$ 10.133,89 (Mont Serrat e Bela Vista);
  - renda mediana por área entre R$ 882,40 (Restinga Velha e Pitinga) e R$ 7.250,00 (Mont Serrat e Bela Vista).
- **Diferença de população:** a soma da tabela é 10.918 pessoas (0,8%) menor que o total de 1.332.845 do JSON. A diferença é compatível com o universo excluído acima, mas a equipe deve confirmar.
- **Unidade:** a renda é por área de ponderação, e não por bairro. Cada área reúne um ou mais bairros, e o nome da área os lista (ex.: "Vila Assunção, Tristeza, Vila Conceição, Pedra Redonda, Sétimo Céu e Jardim Isabel").

### 3.3 Composição das áreas de ponderação (`IBGE/composicao_areas_ponderacao_IBGE.xlsx`)

- **Colunas:** `Setor`, `Código do Município`, `Área de Ponderação` e `Nome do Município`.
- **Tamanho:** 468.097 setores, em 5.570 municípios.
- **Porto Alegre:** 2.744 setores em 46 áreas de ponderação. As 46 áreas são exatamente as mesmas da Tabela 8.3, sem divergência em nenhum dos dois lados.
- **Limpeza necessária:** o cabeçalho da última coluna está escrito "Nome do Municíipio", com o erro de digitação.

### 3.4 Dicionário dos agregados por setor censitário

- **Abas:** `Dicionário Básico`, `Siglas Básico`, `Dicionário não PCT`, `Dicionário PCT - Indígenas` e `Dicionário PCT - Quilombolas`.
- **Uso:** documenta as variáveis dos agregados. Por exemplo, `V0001` é o total de pessoas, e `V0007` é o total de domicílios particulares ocupados.
- O arquivo é só documentação. Não contém os dados dos setores.

### 3.5 Lista de tabelas (PDF)

- **Conteúdo:** catálogo das tabelas de resultados gerais da amostra por área de ponderação, organizado por tema (características dos domicílios, educação, deficiência, religião, fecundidade, migração, trabalho, rendimento etc.).
- **Confirmação:** o PDF confirma o título da Tabela 8.3. As tabelas 8.1 e 8.2, também de rendimento, não fazem parte deste levantamento.
- **Fonte:** IBGE (Censo 2022, resultados gerais da amostra por área de ponderação).

### 3.6 Agregados básicos por setor censitário

- **Coleta:** baixado automaticamente por `scripts/limpeza_ibge.py`, a partir do link no `README.md`, e guardado em `dados/originais/IBGE/agregados/` (fora do git, por ser grande).
- **Formato:** CSV separado por `;`, codificação latin-1, uma linha por setor censitário do Brasil.
- **Porto Alegre:** 2.744 setores em 94 bairros, os mesmos 94 do INCT. A população somada (`v0001`) é 1.332.845, igual à do JSON do INCT.
- É a base que liga os setores aos bairros de Porto Alegre.

### 3.7 Análise da Área Diretamente Afetada (ADA) da RH Guaíba (`zenodo/analise_ada_rhguaiba_municipios.csv`)

- **Origem:** Dados da análise da Área Diretamente Afetada (ADA) pelas inundações de maio de 2024 na Região Hidrográfica do Guaíba, disponibilizados via Zenodo (versão v0.4, registro [Zenodo 11177244](https://zenodo.org/records/11177244?preview_file=analise_ada_rhguaiba_municipios.csv)).
- **Formato:** CSV com 139 registros (um por município) e 26 colunas.
- **Cobertura regional:** cobre 139 municípios da RH do Guaíba, totalizando 632.669 pessoas e 301.738 domicílios diretamente atingidos durante a cheia de maio de 2024 (10,9% da população da bacia).
- **Porto Alegre:**
  - A população total de referência registrada (`Pessoas_2022`: 1.332.845) é exatamente idêntica à soma dos setores do IBGE e ao total do JSON do INCT, assegurando perfeita coerência demográfica entre as fontes.
  - Pessoas afetadas: 151.141 (11,3% da população municipal).
  - Domicílios afetados: 85.368 (12,4% dos 687.679 domicílios).
  - Área afetada no município: 123,58 km² (24,95% da área total) e 37,19 km² em área urbana (21,19% da malha urbana).
  - Infraestrutura viária e estruturas: 519 km de vias afetadas, 84.523 estruturas atingidas e 17,34 km² de área construída afetada.
  - Equipamentos atingidos: 262 de saúde, 231 de ensino, 298 estabelecimentos religiosos e 185 domicílios coletivos.
- **Papel no projeto:** Fornece o contraponto e contexto regional do desastre de maio de 2024. Enquanto os dados do INCT trazem diferentes cotas do Guaíba (3,0 m a 10,0 m) em nível de bairro para Porto Alegre, a base do Zenodo permite contextualizar o impacto observado tanto para Porto Alegre quanto em comparação com os municípios vizinhos da bacia hidrográfica (ex.: Canoas, Eldorado do Sul e São Leopoldo).

## 4. Como as bases se conectam

```
                       Zenodo (RH Guaíba)
                   [Evento real de Maio/2024]
                               │
               (Validação macro regional e municipal)
                               │
                               ▼
Dados do INCT (94 bairros) ◄───┴───► Porto Alegre (151.141 afetados)
        │  bairro → setor censitário   [Agregados básicos]
        ▼
Setor censitário (2.744 em Porto Alegre)
        │  setor → área de ponderação  [Composição]
        ▼
Área de ponderação (46 em Porto Alegre)
        │  área → renda                [Tabela 8.3]
        ▼
Renda média e mediana por área
```

O cruzamento tem duas limitações. A primeira é que 46 áreas de ponderação são menos que 94 bairros, então bairros da mesma área vão receber o mesmo valor de renda. A segunda é que a renda é um agregado da área, e não do bairro. A decisão adotada está em `relatorios/limpeza_dados.md`, seção 5: bairros em uma área recebem a renda dessa área, e bairros em duas áreas recebem a média ponderada pela população dos setores.