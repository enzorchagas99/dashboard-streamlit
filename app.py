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
    # Ler CSV
    try:
        df = pd.read_csv(uploaded_file)
    except:
        df = pd.read_csv(uploaded_file, sep=";")

    # -------------------------------
    # Normalizar nomes de colunas
    # -------------------------------
    df.columns = df.columns.str.strip().str.lower().str.replace("\n","").str.replace(" ","_")

    col_map = {
        "marca": "marca",
        "unidade": "unidade",
        "classificação_receita": "classificacao_receita",
        "nome_do_item": "nome_do_item",
        "valor_do_item": "valor_do_item",
        "repasse_%_escola": "repasse_perc_escola",
        "repasse_$_escola": "repasse_valor_escola",
        "aluno_interno": "aluno_interno",
        "aluno_externo": "aluno_externo"
    }
    df = df.rename(columns={k: v for k,v in col_map.items() if k in df.columns})

    # -------------------------------
    # Converter colunas numéricas
    # -------------------------------
    # Financeiro
    if "valor_do_item" in df.columns:
        df["valor_do_item"] = df["valor_do_item"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["valor_do_item"] = pd.to_numeric(df["valor_do_item"], errors="coerce")

    if "repasse_valor_escola" in df.columns:
        df["repasse_valor_escola"] = df["repasse_valor_escola"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["repasse_valor_escola"] = pd.to_numeric(df["repasse_valor_escola"], errors="coerce")

    # Porcentagem
    if "repasse_perc_escola" in df.columns:
        df["repasse_perc_escola"] = pd.to_numeric(df["repasse_perc_escola"], errors="coerce")

    # Alunos: transformar n/A em 0
    for col in ["aluno_interno", "aluno_externo"]:
        if col in df.columns:
            df[col] = df[col].replace("n/A", 0)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------------
    # Filtros laterais (listas suspensas sem valores vazios)
    # -------------------------------
    st.sidebar.header("Filtros")
    if "marca" in df.columns:
        marcas = st.sidebar.multiselect("Marca", options=df["marca"].dropna().unique(), default=df["marca"].dropna().unique())
    else:
        marcas = []

    if "unidade" in df.columns:
        unidades = st.sidebar.multiselect("Unidade", options=df["unidade"].dropna().unique(), default=df["unidade"].dropna().unique())
    else:
        unidades = []

    if "classificacao_receita" in df.columns:
        classificacoes = st.sidebar.multiselect("Classificação Receita", options=df["classificacao_receita"].dropna().unique(), default=df["classificacao_receita"].dropna().unique())
    else:
        classificacoes = []

    # Aplicar filtros
    df_filtrado = df.copy()
    if marcas: df_filtrado = df_filtrado[df_filtrado["marca"].isin(marcas)]
    if unidades: df_filtrado = df_filtrado[df_filtrado["unidade"].isin(unidades)]
    if classificacoes: df_filtrado = df_filtrado[df_filtrado["classificacao_receita"].isin(classificacoes)]

    # -------------------------------
    # Big Cards (KPIs)
    # -------------------------------
    st.header("KPIs")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Soma Valor do Item", f"R$ {df_filtrado['valor_do_item'].sum():,.0f}".replace(",", ".") if "valor_do_item" in df_filtrado else "0")
    kpi2.metric("Soma Repasse $ Escola", f"R$ {df_filtrado['repasse_valor_escola'].sum():,.0f}".replace(",", ".") if "repasse_valor_escola" in df_filtrado else "0")
    kpi3.metric("Soma Alunos Internos", f"{df_filtrado['aluno_interno'][df_filtrado['aluno_interno']==1].sum()}" if "aluno_interno" in df_filtrado else "0")
    kpi4.metric("Soma Alunos Externos", f"{df_filtrado['aluno_externo'][df_filtrado['aluno_externo']==1].sum()}" if "aluno_externo" in df_filtrado else "0")

    # -------------------------------
    # Tabela detalhada
    # -------------------------------
    st.header("Tabela Detalhada")
    display_cols = [c for c in [
        "marca", "unidade", "classificacao_receita", "nome_do_item",
        "valor_do_item", "repasse_perc_escola", "repasse_valor_escola",
        "aluno_interno", "aluno_externo"
    ] if c in df_filtrado.columns]

    # Substituir NaN por 0 nas colunas de aluno
    df_filtrado[["aluno_interno", "aluno_externo"]] = df_filtrado[["aluno_interno", "aluno_externo"]].fillna(0)

    st.dataframe(df_filtrado[display_cols].reset_index(drop=True), use_container_width=True)

    # Formatar números financeiros e percentuais na tabela
    for col in ["valor_do_item", "repasse_valor_escola"]:
        if col in df_filtrado.columns:
            df_filtrado[col] = df_filtrado[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    if "repasse_perc_escola" in df_filtrado.columns:
        df_filtrado["repasse_perc_escola"] = df_filtrado["repasse_perc_escola"].apply(lambda x: f"{x:.1f}%")

    # -------------------------------
    # Gráficos interativos
    # -------------------------------
    st.header("Gráficos")

    # Gráfico 1: Valor do Item por Marca
    if "marca" in df_filtrado.columns and "valor_do_item" in df_filtrado.columns:
        fig_marca = px.bar(
            df_filtrado.groupby("marca")["valor_do_item"].sum().reset_index(),
            x="marca",
            y="valor_do_item",
            title="Soma do Valor do Item por Marca",
            text_auto=".2s"
        )
        st.plotly_chart(fig_marca, use_container_width=True)

    # Gráfico 2: Valor do Item por Unidade
    if "unidade" in df_filtrado.columns and "valor_do_item" in df_filtrado.columns:
        fig_unidade = px.bar(
            df_filtrado.groupby("unidade")["valor_do_item"].sum().reset_index(),
            x="unidade",
            y="valor_do_item",
            title="Soma do Valor do Item por Unidade",
            text_auto=".2s"
        )
        st.plotly_chart(fig_unidade, use_container_width=True)

else:
    st.info("Por favor, faça upload do arquivo CSV para visualizar o dashboard.")
