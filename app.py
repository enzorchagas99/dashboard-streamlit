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
    for col in ["valor_do_item", "repasse_valor_escola"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Percentual
    if "repasse_perc_escola" in df.columns:
        df["repasse_perc_escola"] = pd.to_numeric(df["repasse_perc_escola"], errors="coerce")

    # Alunos: n/A → 0, valores como inteiro
    for col in ["aluno_interno", "aluno_externo"]:
        if col in df.columns:
            df[col] = df[col].replace("n/A", 0)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # -------------------------------
    # Filtros suspensos
    # -------------------------------
    st.sidebar.header("Filtros")
    marcas = st.sidebar.multiselect("Marca", options=df["marca"].dropna().unique(), default=df["marca"].dropna().unique())
    unidades = st.sidebar.multiselect("Unidade", options=df["unidade"].dropna().unique(), default=df["unidade"].dropna().unique())
    classificacoes = st.sidebar.multiselect("Classificação Receita", options=df["classificacao_receita"].dropna().unique(), default=df["classificacao_receita"].dropna().unique())

    # Aplicar filtros
    df_filtrado = df.copy()
    df_filtrado = df_filtrado[df_filtrado["marca"].isin(marcas)]
    df_filtrado = df_filtrado[df_filtrado["unidade"].isin(unidades)]
    df_filtrado = df_filtrado[df_filtrado["classificacao_receita"].isin(classificacoes)]

    # -------------------------------
    # Big Cards (KPIs)
    # -------------------------------
    st.header("KPIs")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Soma Valor do Item", f"R$ {df_filtrado['valor_do_item'].sum():,.0f}".replace(",", ".") if "valor_do_item" in df_filtrado else "0")
    kpi2.metric("Soma Repasse $ Escola", f"R$ {df_filtrado['repasse_valor_escola'].sum():,.0f}".replace(",", ".") if "repasse_valor_escola" in df_filtrado else "0")
    kpi3.metric("Alunos Internos", f"{df_filtrado['aluno_interno'][df_filtrado['aluno_interno']==1].sum():,}".replace(",", ".") if "aluno_interno" in df_filtrado else "0")
    kpi4.metric("Alunos Externos", f"{df_filtrado['aluno_externo'][df_filtrado['aluno_externo']==1].sum():,}".replace(",", ".") if "aluno_externo" in df_filtrado else "0")

    # -------------------------------
    # Tabela detalhada
    # -------------------------------
    st.header("Tabela Detalhada")
    display_cols = [c for c in [
        "marca", "unidade", "classificacao_receita", "nome_do_item",
        "valor_do_item", "repasse_perc_escola", "repasse_valor_escola",
        "aluno_interno", "aluno_externo"
    ] if c in df_filtrado.columns]

    # Substituir NaN por 0 em alunos
    df_filtrado[["aluno_interno","aluno_externo"]] = df_filtrado[["aluno_interno","aluno_externo"]].fillna(0)

    # Resetar índice para remover coluna extra
    df_filtrado = df_filtrado.reset_index(drop=True)
    st.dataframe(df_filtrado[display_cols], use_container_width=True)

    # -------------------------------
    # Formatação da tabela
    # -------------------------------
    # Financeiro
    for col in ["valor_do_item","repasse_valor_escola"]:
        if col in df_filtrado.columns:
            df_filtrado[col] = df_filtrado[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    # Percentual
    if "repasse_perc_escola" in df_filtrado.columns:
        df_filtrado["repasse_perc_escola"] = df_filtrado["repasse_perc_escola"].apply(lambda x: f"{x:.1f}%")

    # -------------------------------
    # Gráficos interativos
    # -------------------------------
    st.header("Gráficos")

    # Gráfico por Marca
    if "marca" in df_filtrado.columns and "repasse_valor_escola" in df_filtrado.columns:
        fig_marca = px.bar(
            df_filtrado.groupby("marca")["repasse_valor_escola"].sum().reset_index(),
            x="marca",
            y="repasse_valor_escola",
            title="Repasse $ Escola por Marca",
            text_auto=".2s"
        )
        st.plotly_chart(fig_marca, use_container_width=True)

    # Gráfico por Unidade
    if "unidade" in df_filtrado.columns and "repasse_valor_escola" in df_filtrado.columns:
        fig_unidade = px.bar(
            df_filtrado.groupby("unidade")["repasse_valor_escola"].sum().reset_index(),
            x="unidade",
            y="repasse_valor_escola",
            title="Repasse $ Escola por Unidade",
            text_auto=".2s"
        )
        st.plotly_chart(fig_unidade, use_container_width=True)

    # Gráfico por Classificação Receita
    if "classificacao_receita" in df_filtrado.columns and "repasse_valor_escola" in df_filtrado.columns:
        fig_classificacao = px.bar(
            df_filtrado.groupby("classificacao_receita")["repasse_valor_escola"].sum().reset_index(),
            x="classificacao_receita",
            y="repasse_valor_escola",
            title="Repasse $ Escola por Classificação Receita",
            text_auto=".2s"
        )
        st.plotly_chart(fig_classificacao, use_container_width=True)

else:
    st.info("Por favor, faça upload do arquivo CSV para visualizar o dashboard.")

