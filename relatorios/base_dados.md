# Relatório: Levantamento de bases

Data: 08/11/2026

Este relatório descreve as bases escolhidas para o projeto, o que cada uma contém, como elas se conectam e o que ainda está pendente. As contagens foram feitas diretamente nos arquivos em `dados/originais/`.

## 1. Objetivo do levantamento

Cruzar os níveis de inundação simulados pelo INCT SiMAI para o Guaíba com a população e a renda dos bairros de Porto Alegre. Para isso, são necessárias três coisas: a simulação, a renda da população e uma ponte entre os bairros da simulação e as unidades do IBGE.

## 2. Bases escolhidas

| # | Base | Arquivo | Unidade de análise | Papel no projeto |
|---|------|---------|--------------------|------------------|
| 1 | Simulação do INCT SiMAI | `data_inct_original.json` | nível do Guaíba × bairro | Variável de inundação (edificações e pessoas afetadas) |
| 2 | Tabela 8.3 do Censo 2022 (renda domiciliar per capita) | `Tab8_3.xlsx` | área de ponderação | Renda média e mediana |
| 3 | Composição das áreas de ponderação | `composicao_areas_ponderacao_IBGE.xlsx` | setor censitário → área de ponderação | Ponte entre setores e áreas de renda |
| 4 | Dicionário dos agregados por setor censitário | `dicionario_agregados_setores_censitarios_20260520.xlsx` | variável | Documentação das variáveis do IBGE (ex.: `V0001`, total de pessoas) |
| 5 | Lista de tabelas de resultados gerais da amostra | `lista_tabelas_resultados_gerais_amostra_areas_ponderacao.pdf` | tabela | Catálogo que confirma o título e o tema da Tabela 8.3 |
| 6 | Agregados básicos por setor censitário | ZIP não versionado (cerca de 15 MB) | setor censitário → bairro | Ponte entre setores e bairros de Porto Alegre |

## 3. Detalhamento das bases

### 3.1 Simulação do INCT SiMAI (`data_inct_original.json`)

- **Formato:** JSON aninhado, organizado como nível → bairro → métricas.
- **Níveis:** 71 chaves, de `3_0m` a `10_0m`, com passo de 0,1 m. Cada nível é uma cota do Guaíba (conforme a nota do notebook de exploração).
- **Bairros:** 94 por nível, todos com o mesmo conjunto de nomes em cada um dos 71 níveis.
- **Registros:** 6.674 linhas após transformar o JSON em formato longo (`notebooks/exploracao_inct.ipynb`).
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
- Não é possível dizer, só pelos dados, se isso é uma propriedade do modelo ou um erro de processamento.

**Lacunas de documentação:**

- O link da fonte (`README.md`, "link a preencher") e a data de coleta ("a preencher") ainda não foram informados.
- A origem de `population` e `total_buildings` não está descrita. Não se sabe se vêm do Censo 2022 ou de outra base.

### 3.2 Tabela 8.3 do Censo 2022 (`Tab8_3.xlsx`)

- **Conteúdo:** valor do rendimento domiciliar mensal per capita, médio e mediano, dos moradores em domicílios particulares permanentes ocupados. Exclui moradores cuja condição era pensionista, empregado(a) doméstico(a) ou parente de empregado(a) doméstico(a).
- **Recorte:** a planilha cobre o Brasil e tem 5.570 municípios. Porto Alegre (código 4314902) aparece em 46 áreas de ponderação.
- **Colunas:** pessoas (total, homens e mulheres), renda média (total, homens e mulheres) e renda mediana (total, homens e mulheres). Antes dos dados, há duas linhas de título e duas de cabeçalho.
- **Porto Alegre:**
  - 1.321.927 pessoas, no universo da tabela;
  - renda média por área entre R$ 7.581 (Santana) e R$ 20.846 (Mário Quintana);
  - renda mediana por área entre R$ 1.060,64 e R$ 10.513,96.
- **Diferença de população:** a soma da tabela é 10.918 pessoas (0,8%) menor que o total de 1.332.845 do JSON. A diferença é compatível com o universo excluído acima, mas a equipe deve confirmar.
- **Unidade:** a renda é por área de ponderação, e não por bairro. Cada área reúne um ou mais bairros, e o nome da área os lista (ex.: "Vila Assunção, Tristeza, Vila Conceição, Pedra Redonda, Sétimo Céu e Jardim Isabel").

### 3.3 Composição das áreas de ponderação (`composicao_areas_ponderacao_IBGE.xlsx`)

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

### 3.6 Agregados básicos por setor censitário (pendente)

- Ainda não está no repositório. Está no link indicado no `README.md`.
- É a única base que liga os setores aos bairros de Porto Alegre. Sem ela, a renda não pode ser associada aos 94 bairros da simulação.
- Esta análise não abriu o arquivo. Os nomes dos bairros nele precisam ser comparados com os 94 nomes do JSON.

## 4. Como as bases se conectam

```
Simulação INCT (94 bairros)
        │  bairro → setor censitário   [Agregados básicos: pendente]
        ▼
Setor censitário (2.744 em Porto Alegre)
        │  setor → área de ponderação  [Composição]
        ▼
Área de ponderação (46 em Porto Alegre)
        │  área → renda                [Tabela 8.3]
        ▼
Renda média e mediana por área
```

O cruzamento tem duas limitações. A primeira é que 46 áreas de ponderação são menos que 94 bairros, então bairros da mesma área vão receber o mesmo valor de renda. A segunda é que a renda é um agregado da área, e não do bairro. Por isso, a agregação precisa de uma decisão da equipe, por exemplo uma média ponderada pela população.