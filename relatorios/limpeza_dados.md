# Relatório: Limpeza dos dados

## 1. Processo de exploração

1. **Leitura do arquivo.** Verificou-se a estrutura de `data_inct_original.json`: 71 níveis do Guaíba (de 3,0 m a 10,0 m, em passos de 0,1 m), 94 bairros por nível e cinco campos por registro.

2. **Carga em formato longo.** Foi usado o código mínimo do enunciado para gerar um DataFrame com uma linha por nível e bairro. O resultado tem 6674 linhas e 7 colunas, sem valores nulos e com os tipos esperados. A parte textual está em `notebooks/exploracao/exploracao_inct.ipynb` e os gráficos em `notebooks/exploracao/exploracao_grafica_percentual_inct.ipynb`.

3. **Verificação de estrutura.** Verificou-se se todos os níveis estão presentes, se cada nível tem os mesmos 94 bairros, se há nomes duplicados ou com variações de grafia e se há chaves fora do padrão.

4. **Verificação de consistência.** Foram testadas as relações entre os campos:
   - `affected_buildings` não pode ser maior que `total_buildings`.
   - `percentage` deve ficar entre 0 e 100 e ser igual a `affected_buildings / total_buildings`.
   - `affected_population` deve ser igual a `population × percentage / 100`.
   - `total_buildings` e `population` devem ser constantes por bairro.
   - A quantidade de prédios afetados não deve diminuir conforme o nível do rio sobe.

5. **Gráficos de inspeção.** Foram gerados um gráfico de prédios afetados e outro de população afetada para cada bairro, ao longo dos níveis. Em seguida, os bairros foram agrupados em pares, com cores diferentes, e os eixos foram normalizados em percentual (% de prédios afetados e % da população afetada), em grade de dois gráficos por linha. Também foi gerada a curva da população afetada da cidade, em percentual. Os gráficos percentuais estão em `notebooks/exploracao/exploracao_grafica_percentual_inct.ipynb` e `notebooks/exploracao/exploracao_grafica_percentual_dados_processados.ipynb`. Os gráficos quantitativos (valores absolutos, um gráfico por bairro) estão em `notebooks/exploracao/exploracao_grafica_quantitativa_inct.ipynb` e `notebooks/exploracao/exploracao_grafica_quantitativa_dados_processados.ipynb`.

6. **Limpeza por script.** A limpeza é feita por `scripts/limpeza_inct.py`, a partir do arquivo original, sem alterações manuais. Ver a seção 3. A exploração dos dados limpos está em `notebooks/exploracao/exploracao_dados_processados.ipynb` (parte textual e numérica) e os gráficos em `notebooks/exploracao/exploracao_grafica_percentual_dados_processados.ipynb` (percentuais) e `notebooks/exploracao/exploracao_grafica_quantitativa_dados_processados.ipynb` (quantitativos), ambos aplicados a `dados/processados/inct_limpo.json`.

**Uso de ferramentas de IA:** o Claude (Anthropic) foi usado para escrever os scripts de verificação e de limpeza, montar parte dos notebooks, gerar o código dos gráficos e ajustar o layout. Os dados e resultados foram conferidos pela equipe de forma gráfica e numérica com base nos arquivos de origem e gráficos dos notebooks.

## 2. Problemas identificados

**2.1. Quedas no número de prédios afetados (12 casos).** A quantidade de prédios afetados diminui quando o nível do rio sobe:
- **Centro Histórico:** 2050 prédios afetados em 9,6 m, 0 em 9,7 m e 0 em 9,8 m, voltando a 2181 em 10,0 m. Em 9,7 m, o total da cidade cai em 12.258 pessoas afetadas e 1.028 prédios.
- **Rubem Berta:** 252 prédios em 8,7 m, 0 em 8,8 m e 503 em 9,5 m.
- **Lageado:** 108 prédios em 8,0 m e 0 em 8,1 m.
- **Espírito Santo:** 633 prédios em 3,4 m, 25 em 3,5 m e 2101 em 4,7 m (63% do total), com 46 em 4,6 m e 47 em 4,8 m.
- **Arquipélago:** 4685 prédios em 3,0 m, 4680 em 3,1 m e 4674 em 4,1 m (total de 4688), com alternância entre esses valores em vários níveis.

**2.2. Zeros em sequência.** Lageado registra 0 prédios afetados de 3,0 m a 4,9 m, e Rubem Berta, de 3,0 m a 6,2 m. Depois disso, os dois passam a ter valores. Os zeros em 8,1 m (Lageado) e 8,8 m (Rubem Berta) aparecem no meio de uma sequência crescente.

**2.3. Ordem diferente no nível 5,3 m.** O nível 5,3 m tem os mesmos 94 bairros dos outros níveis, mas em outra ordem: 38 posições são diferentes. A análise feita por nome de bairro não é afetada, mas qualquer leitura feita pela posição é inválida.

**2.4. Arredondamento de `percentage`.** A fonte calcula `percentage` como o teto (arredondamento para cima) de `affected_buildings / total_buildings × 100`. Por isso, `percentage` é sempre igual ou maior que o percentual exato. A população afetada, calculada como `population × percentage / 100`, herda esse excesso: a diferença em relação à conta com os prédios exatos chega a 501 pessoas em um mesmo bairro e nível. Por exemplo, em Ipanema, a 3,5 m, 53 prédios afetados de 8537 dão 0,62%, que a fonte arredonda para 1%, e a população afetada fica em 135 pessoas, contra 83 pela conta exata. **Tratamento: manter e avisar.** A regra da fonte foi mantida, sem alteração, e a diferença deve ser informada como limitação dos dados.

**Verificações sem problemas:** não foram encontrados valores negativos, prédios afetados maiores que o total, percentuais fora de 0–100, nomes de bairros duplicados após normalizar acentos e apóstrofos, nem variação de população ou de total de prédios entre níveis.

## 3. Correções aplicadas

As correções são feitas por `scripts/limpeza_inct.py`, a partir de `dados/originais/data_inct_original.json`. Para reproduzir, a partir da raiz do projeto, execute `python scripts/limpeza_inct.py`. O script gera:
- `dados/processados/inct_limpo.json`: formato longo, uma linha por nível e bairro, já ordenado.
- `dados/processados/correcoes_inct.csv`: cada valor alterado, com os vizinhos usados no cálculo.

**Ordenação.** Dentro de cada nível, os bairros são ordenados em ordem alfabética, sem diferenciar acentos nem maiúsculas. Justificativa: resolve o item 2.3.

**Métodos de correção.** São quatro métodos, aplicados a pontos diferentes:

- **Média dos vizinhos válidos.** Cada ponto corrigido recebe a média aritmética entre o valor válido mais próximo à esquerda e o valor válido mais próximo à direita, no mesmo bairro. A média é arredondada para cima quando termina em 0,5, e os pontos corrigidos não são usados como vizinhos. Aplicado a Rubem Berta, Lageado e ao pico de Espírito Santo em 4,7 m. Justificativa: são pontos isolados, cujos vizinhos são consistentes entre si.

- **Interpolação linear entre vizinhos válidos.** Aplicado ao Centro Histórico. A média daria o mesmo valor (2090) para 9,7 m e 9,8 m, formando um patamar artificial. Por isso, cada nível recebe um valor intermediário, proporcional à distância entre os vizinhos válidos, 9,6 m (2050) e 9,9 m (2130): 2077 em 9,7 m e 2103 em 9,8 m.

- **Saturação.** Aplicado ao Arquipélago: em todos os níveis, `affected_buildings` passa a ser igual a `total_buildings` (4688). Justificativa: a população afetada do bairro já é 100% em todos os níveis (ver a nota sobre o Arquipélago). Igualar os prédios afetados ao total torna os dois campos coerentes e elimina a oscilação da contagem, que variava entre 4674 e 4688 sem padrão de crescimento.

- **Substituição pelo valor seguinte ao planalto.** Aplicado a Espírito Santo de 3,0 m a 3,4 m, onde os valores (637, 637, 637, 637 e 633) formam um planalto alto que não cresce, enquanto a curva a partir de 3,5 m é suave. Cada nível do planalto recebe 25 prédios, o valor de 3,5 m, que é o menor valor imediatamente seguinte ao planalto. Não se usou média porque não há vizinho válido à esquerda de 3,0 m, e a média entre os dois regimes não representaria nenhum deles.

`percentage` e `affected_population` são recalculados com a regra da própria fonte: `percentage` é o teto de `affected_buildings / total_buildings × 100`, e `affected_population` é o teto de `population × percentage / 100`. Essa regra reproduz exatamente os valores originais em todas as linhas que não foram corrigidas.

**Valores corrigidos:**

| Bairro | Nível (m) | Original | Método | Referências | Novo |
|--------|-----------|----------|--------|-------------|------|
| Centro Histórico | 9,7 | 0 | interpolação | 9,6 m = 2050; 9,9 m = 2130 | 2077 |
| Centro Histórico | 9,8 | 0 | interpolação | 9,6 m = 2050; 9,9 m = 2130 | 2103 |
| Rubem Berta | 8,8 | 0 | média | 8,7 m = 252; 8,9 m = 285 | 269 |
| Lageado | 8,1 | 0 | média | 8,0 m = 108; 8,2 m = 110 | 109 |
| Espírito Santo | 4,7 | 2101 | média | 4,6 m = 46; 4,8 m = 47 | 47 |
| Espírito Santo | 3,0 a 3,4 | 637, 637, 637, 637, 633 | substituição | 3,5 m = 25 | 25 |
| Arquipélago | 3,0 a 10,0 (exceto 5,3) | entre 4674 e 4685 | saturação | total_buildings = 4688 | 4688 |

**Nota sobre o Arquipélago.** No arquivo original, o bairro aparece com `percentage` = 100 e `affected_population` = 6411 (a população inteira) em todos os níveis, embora a contagem de prédios afetados oscile entre 4674 e 4688. Isso acontece porque a fonte usa teto no percentual: 4674 de 4688 prédios (99,7%) aparece como 100. Depois da saturação, os três campos indicam 100% em todos os níveis. A simulação atinge o bairro inteiro já no primeiro nível, e por isso a curva é plana.

**Espírito Santo.** A substituição do planalto inicial é uma hipótese. Os dados não explicam a diferença entre o planalto de 3,0 m a 3,4 m e a curva a partir de 3,5 m.

## 4. Tratamento

| # | Problema | Tratamento | Justificativa |
|---|----------|------------|---------------|
| 1 | Quedas no número de prédios afetados | Corrigido. Centro Histórico por interpolação linear; Rubem Berta e Lageado por média; Espírito Santo por média (4,7 m) e substituição (3,0 m a 3,4 m); Arquipélago por saturação (prédios afetados = total). Não restam quedas. | Ver a seção 3. |
| 2 | Zeros em sequência | Corrigido em 9,7 m e 9,8 m (Centro Histórico), 8,8 m (Rubem Berta) e 8,1 m (Lageado). Zeros do início da curva (Lageado de 3,0 m a 4,9 m; Rubem Berta de 3,0 m a 6,2 m) mantidos. | Os zeros do início não são quedas: a curva começa em zero e sobe depois, o que é coerente com a água ainda não ter atingido o bairro. |
| 3 | Arredondamento de `percentage` (item 2.4) | Mantido e avisado. Regra do teto da fonte preservada. | Alterar a regra mudaria os valores originais de todas as linhas; a diferença é documentada como limitação. |
| 4 | Ordem diferente no nível 5,3 m | Corrigido. Registros ordenados alfabeticamente dentro de cada nível. | Ver a seção 3. |
