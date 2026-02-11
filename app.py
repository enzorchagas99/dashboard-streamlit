import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Título do Dashboard
# -------------------------------
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("Dashboard Financeiro de Vendas e Repasses")

# -------------------------------
# Upload do CSV
# -------------------------------
st.sidebar.header("Upload do arquivo CSV")
uploaded_file = st.sidebar.file_uploader("Escolha o CSV", type="csv")

if uploaded_file:
    # -------------------------------
    # Leitura do CSV
    # -------------------------------
    df = pd.read_csv(uploaded_file)

    # -------------------------------
    # Filtros laterais
    # -------------------------------
    st.sidebar.header("Filtros")
    marcas = st.sidebar.multiselect("Marca", options=df["Marca"].unique(), default=df["Marca"].unique())
    unidades = st.sidebar.multiselect("Unidade", options=df["Unidade"].unique(), default=df["Unidade"].unique())
    classificacoes = st.sidebar.multiselect(
        "Classificação Receita",
        options=df["Classificação Receita"].unique(),
        default=df["Classificação Receita"].unique()
    )

    df_filtrado = df[
        (df["Marca"].isin(marcas)) &
        (df["Unidade"].isin(unidades)) &
        (df["Classificação Receita"].isin(classificacoes))
    ]

    # -------------------------------
    # Big Cards (KPIs)
    # -------------------------------
    st.header("KPIs")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Soma Valor do Item", f"R$ {df_filtrado['Valor do Item'].sum():,.2f}")
    kpi2.metric("Soma Repasse $ Escola", f"R$ {df_filtrado['Repasse $ Escola'].sum():,.2f}")
    kpi3.metric("Soma Alunos Internos", f"{int(df_filtrado['Alunos internos'].sum())}")
    kpi4.metric("Soma Alunos Externos", f"{int(df_filtrado['Alunos externos'].sum())}")

    # -------------------------------
    # Tabela detalhada
    # -------------------------------
    st.header("Tabela Detalhada")
    st.dataframe(
        df_filtrado[[
            "Marca", "Unidade", "Classificação Receita", "Nome do Item",
            "Valor do Item", "Repasse % Escola", "Repasse $ Escola",
            "Alunos internos", "Alunos externos"
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
        title="Soma do Valor do
