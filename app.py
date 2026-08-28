from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sobrecusto em Contratos — TCE-ES", layout="wide")

CAMINHO_DADOS = Path(__file__).parent.parent / "data" / "processed" / "contratos_tratados.csv"

# Paleta: hue único sequencial (ciano) para magnitude, sem cores categóricas
# arbitrárias — segue a régua de "sequential is the safe default". Tons
# calibrados para contraste em fundo escuro (mais escuro = menor magnitude,
# mais brilhante = maior magnitude).
RAMPA_SEQUENCIAL = [
    "#12283f", "#153a5c", "#155e75", "#0e7490",
    "#0891b2", "#06b6d4", "#22d3ee", "#5eead4",
]
COR_DESTAQUE = "#22d3ee"
COR_ALERTA = "#f87171"
COR_SUPERFICIE = "rgba(0, 0, 0, 0)"  # transparente: o gráfico herda o fundo do card
COR_TEXTO_GRAFICO = "#d8e3fb"
COR_GRADE = "rgba(216, 227, 251, 0.08)"
COR_LINHA_BASE = "#45536b"

# --- Tema visual (fonte + cards em glass panel) ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        [data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 0.5rem;
            padding: 1rem 1.25rem;
            backdrop-filter: blur(6px);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #8b96ab;
        }
        [data-testid="stMetricValue"] {
            font-weight: 700;
        }

        [data-testid="stVerticalBlockBorderWrapper"] > div,
        div[data-testid="stExpander"] {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 0.5rem;
        }

        h1, h2, h3 { letter-spacing: -0.01em; }
        hr { border-color: rgba(255, 255, 255, 0.08) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    return pd.read_csv(CAMINHO_DADOS)


if not CAMINHO_DADOS.exists():
    st.error(
        f"Arquivo não encontrado: {CAMINHO_DADOS}\n\n"
        "Rode o notebook `notebooks/01_exploracao.ipynb` até a seção "
        "'9. Salvar base tratada' antes de abrir este app."
    )
    st.stop()

df = carregar_dados()

st.title("Sobrecusto em Contratos Públicos — TCE-ES")
st.caption(
    "Protótipo inicial de exploração. Base: contratos únicos "
    "(`ChaveInstrumento`) com percentual de variação entre valor inicial e "
    "valor atual. Nenhum piso/filtro foi aplicado sobre os valores — "
    "outliers extremos aparecem propositalmente para investigação futura."
)

# --- Filtros ---
st.sidebar.header("Filtros")

modalidades = sorted(df["ModalidadeLicitacao"].dropna().unique())
modalidades_selecionadas = st.sidebar.multiselect(
    "Modalidade de licitação", modalidades, default=[]
)

busca = st.sidebar.text_input("Buscar fornecedor ou órgão")

faixa_sobrecusto = st.sidebar.slider(
    "Faixa de percentual de sobrecusto exibida nos gráficos (%)",
    min_value=-100.0,
    max_value=2000.0,
    value=(-50.0, 200.0),
    step=10.0,
    help="Só afeta o histograma e o ranking — a tabela sempre mostra tudo.",
)

dados = df.copy()
if modalidades_selecionadas:
    dados = dados[dados["ModalidadeLicitacao"].isin(modalidades_selecionadas)]
if busca:
    termo = busca.strip().lower()
    dados = dados[
        dados["NomeContratado"].str.lower().str.contains(termo, na=False)
        | dados["NomeUnidadeGestoraReferencia"].str.lower().str.contains(termo, na=False)
    ]

dados_na_faixa = dados[dados["percentual_sobrecusto"].between(*faixa_sobrecusto)]

st.sidebar.caption(
    f"{len(dados):,} contrato(s) no filtro atual — "
    f"{len(dados_na_faixa):,} dentro da faixa de sobrecusto selecionada."
)

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Contratos no filtro", f"{len(dados):,}")
col2.metric("Sobrecusto médio", f"{dados['percentual_sobrecusto'].mean():,.1f}%")
col3.metric("Sobrecusto mediano", f"{dados['percentual_sobrecusto'].median():,.1f}%")
col4.metric(
    "Contratos com sobrecusto > 0",
    f"{(dados['percentual_sobrecusto'] > 0).mean() * 100:,.1f}%",
)

st.divider()

# --- Distribuição ---
st.subheader("Distribuição do percentual de sobrecusto")
st.caption(
    "Recorte visual pela faixa selecionada na barra lateral — os valores "
    "extremos continuam nos dados e na tabela abaixo."
)

fig_hist = px.histogram(
    dados_na_faixa,
    x="percentual_sobrecusto",
    nbins=60,
    color_discrete_sequence=[COR_DESTAQUE],
)
fig_hist.update_layout(
    xaxis_title="% de variação em relação ao valor inicial",
    yaxis_title="Quantidade de contratos",
    bargap=0.05,
    showlegend=False,
    plot_bgcolor=COR_SUPERFICIE,
    paper_bgcolor=COR_SUPERFICIE,
    font_color=COR_TEXTO_GRAFICO,
    xaxis=dict(gridcolor=COR_GRADE, zerolinecolor=COR_GRADE),
    yaxis=dict(gridcolor=COR_GRADE, zerolinecolor=COR_GRADE),
)
fig_hist.add_vline(x=0, line_dash="dash", line_color=COR_LINHA_BASE)
st.plotly_chart(fig_hist, width="stretch")

st.divider()

# --- Ranking de fornecedores ---
st.subheader("Fornecedores com maior sobrecusto médio")
st.caption(
    "Considera fornecedores com pelo menos 3 contratos no filtro atual, "
    "dentro da faixa de sobrecusto selecionada."
)

ranking = (
    dados_na_faixa.groupby("NomeContratado")
    .agg(
        qtd_contratos=("ChaveInstrumento", "nunique"),
        sobrecusto_medio=("percentual_sobrecusto", "mean"),
    )
    .query("qtd_contratos >= 3")
    .sort_values("sobrecusto_medio", ascending=False)
    .head(15)
    .reset_index()
)

if ranking.empty:
    st.info("Nenhum fornecedor com 3+ contratos no filtro atual.")
else:
    fig_bar = px.bar(
        ranking.sort_values("sobrecusto_medio"),
        x="sobrecusto_medio",
        y="NomeContratado",
        orientation="h",
        color="sobrecusto_medio",
        color_continuous_scale=RAMPA_SEQUENCIAL,
        text="sobrecusto_medio",
    )
    fig_bar.update_traces(texttemplate="%{text:,.0f}%", textposition="outside")
    fig_bar.update_layout(
        xaxis_title="Sobrecusto médio (%)",
        yaxis_title="",
        coloraxis_showscale=False,
        plot_bgcolor=COR_SUPERFICIE,
        paper_bgcolor=COR_SUPERFICIE,
        font_color=COR_TEXTO_GRAFICO,
        xaxis=dict(gridcolor=COR_GRADE),
        yaxis=dict(gridcolor=COR_GRADE),
        margin=dict(l=0, r=60),
    )
    st.plotly_chart(fig_bar, width="stretch")

st.divider()

# --- Tabela ---
st.subheader("Contratos (tabela completa do filtro)")
st.dataframe(
    dados.sort_values("percentual_sobrecusto", ascending=False),
    width="stretch",
    hide_index=True,
)