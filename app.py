import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("Dashboard Financeiro de Vendas e Repasses")

# -------------------------------
# Upload do CSV
# -------------------------------
st.sidebar.header("Upload do arquivo CSV")
uploaded_file = st.sidebar.file_uploader("Escolha o CSV", type="csv")

if uploaded_file:
    # Ler CSV (tenta separador padrão, senão sep=";")
    try:
        df = pd.read_csv(uploaded_file)
    except:
        df = pd.read_csv(uploaded_file, sep=";")

    # -------------------------------
    # Normalizar nomes de colunas
    # -------------------------------
    df.columns = df.columns.str.strip()          # remove espaços extras
    df.columns = df.columns.str.replace("\n", "") # remove quebras de linha

    # -------------------------------
    # Conversão de colunas numéricas
    # -------------------------------
    colunas_numericas = ["Valor do Item", "Repasse $ Escola", "Aluno Interno", "Aluno Externo"]

    for col in colunas_numericas:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("R$", "", regex=False)    # remove símbolo de moeda
            .str.replace(".", "", regex=False)     # remove ponto de milhar
            .str.replace(",", ".", regex=False)    # vírgula -> ponto decimal
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")  # valores inválidos viram NaN

    # -------------------------------
    # Filtros laterais
    # -------------------------------
    st.sidebar.header("Filtros")
    marcas = st.sidebar.multiselect("Marca", options=df["Marca"].unique(), default=df["Marca"].unique())
    unidades = st.sidebar.multiselect("Unidade", options=df["Unidade"].unique(), default=df["Unidade"].unique())
    classificacoes = st.sidebar.multiselect(
        "Classificação receita",
        options=df["Classificação receita"].unique(),
        default=df["Classificação receita"].unique()
    )

    df_filtrado = df[
        (df["Marca"].isin(marcas)) &
        (df["Unidade"].isin(unidades)) &
        (df["Classificação receita"].isin(classificacoes))
    ]

    # -------------------------------
    # Big Cards (KPIs)
    # -------------------------------
    st.header("KPIs")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Soma Valor do Item", f"R$ {df_filtrado['Valor do Item'].sum():,.2f}")
    kpi2.metric("Soma Repasse $ Escola", f"R$ {df_filtrado['Repasse $ Escola'].sum():,.2f}")
    kpi3.metric("Soma Alunos Internos", f"{int(df_filtrado['Aluno Interno'].sum())}")
    kpi4.metric("Soma Alunos Externos", f"{int(df_filtrado['Aluno Externo'].sum())}")

    # -------------------------------
    # Tabela detalhada
    # -------------------------------
    st.header("Tabela Detalhada")
    st.dataframe(
        df_filtrado[[
            "Marca", "Unidade", "Classificação receita", "Nome do Item",
            "Valor do Item", "Repasse % Escola", "Repasse $ Escola",
            "Aluno Interno", "Aluno Externo"
        ]]
    )

    # -------------------------------
    # Gráficos interativos
    # -------------------------------
    st.header("Gráficos")

    # Gráfico 1: Valor do Item por Unidade
    fig1 = px.bar(
        df_filtrado.groupby("Unidade")["Valor do Item"].sum().reset_index(),
        x="Unidade",
        y="Valor do Item",
        title="Soma do Valor do Item por Unidade",
        text_auto=".2s"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Repasse $ Escola por Classificação receita
    fig2 = px.bar(
        df_filtrado.groupby("Classificação receita")["Repasse $ Escola"].sum().reset_index(),
        x="Classificação receita",
        y="Repasse $ Escola",
        title="Soma do Repasse $ Escola por Classificação receita",
        text_auto=".2s"
    )
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Por favor, faça upload do arquivo CSV para visualizar o dashboard.")
