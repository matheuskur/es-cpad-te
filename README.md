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

Os scripts de coleta e limpeza ficam em `scripts/`, o código do dashboard em `app/`, e os relatórios em `relatorios/`.

## Estrutura

```
projeto-enchentes/
├── README.md
├── requirements.txt
├── dados/
│   ├── originais/        # dados como vieram (ou instruções de download, se forem grandes)
│   └── processados/      # dados limpos usados pelo dashboard
├── scripts/              # scripts de coleta e limpeza
├── notebooks/            # EDA
├── relatorios/
│   ├── base_dados.md
│   ├── limpeza_dados.md
│   └── dashboard.md
└── app/                  # código do dashboard
```

## Fontes dos dados

- Simulação do INCT SiMAI (`data.json`): _a preencher_
- Bases externas sobre enchentes no RS: _a preencher_
