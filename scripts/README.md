# TCC — Predição de Sobrecusto em Licitações (ES)

Protótipo de coleta, estruturação e análise de dados abertos do TCE-ES
sobre contratações públicas do Estado do Espírito Santo.

## Estrutura

```
prototipo/
├── data/
│   ├── raw/               # CSVs baixados, sem tratamento
│   └── processed/         # base tratada, gerada pelo notebook
├── scripts/
│   ├── 01_download_dados.py
│   ├── app.py               # protótipo de visualização (Streamlit)
│   └── README.md
├── notebooks/              # análises exploratórias (Jupyter)
└── requirements.txt
```

## Como rodar (Windows)

```bat
cd TCC\prototipo
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\01_download_dados.py
```

## Visualização (Streamlit)

Requer que `data/processed/contratos_tratados.csv` já exista — gerado pela
seção "9. Salvar base tratada" do notebook `notebooks/01_exploracao.ipynb`.

```bat
cd TCC\prototipo
venv\Scripts\activate
streamlit run scripts\app.py
```

Abre em `http://localhost:8501`. Protótipo inicial: KPIs, distribuição do
percentual de sobrecusto, ranking de fornecedores e tabela filtrável — sem
piso/filtro sobre outliers, propositalmente (ver notebook, seção 6).

## Fonte dos dados

Portal de Dados Abertos do Governo do Espírito Santo (CKAN):
https://dados.es.gov.br/dataset/tcees-contratacoes

Dataset: **[TCEES] Contratações - Controle Externo**
(dados sobre licitações e contratos de todos os órgãos estaduais e
municipais fiscalizados pelo TCE-ES — não confundir com o dataset de
compras administrativas do próprio Tribunal).

## Próximos passos

1. Rodar `01_download_dados.py` e conferir as colunas impressas no console
2. Completar as URLs dos demais recursos em `RECURSOS` (Instrumentos
   contratuais, Contratações, Itens por ano)
3. Modelar o schema relacional (fornecedores, contratos, aditivos)
4. Escrever script de carga (ETL) para MySQL
