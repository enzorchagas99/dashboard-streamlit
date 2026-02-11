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
    # Tenta ler CSV com separador padrão ou ; (Excel)
    try:
        df = pd.read_csv(uploaded_file)
    except:
        df = pd.read_csv(uploaded_file, sep=";")

    # -------------------------------
    # Normalizar nomes de colunas
    # -------------------------------
    df.columns = df.columns.str.strip()              # remove espaços
    df.columns = df.columns.str.lower()             # transforma tudo em minúscula
    df.columns = df.columns.str.replace("\n", "")   # remove quebras de linha
    df.columns = df.columns.str.replace(" ", "_")   # transforma espaços em underline

    # -------------------------------
    # Mapear nomes esperados
    # -------------------------------
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

    # Renomear colunas do df para padronizar
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # -------------------------------
    # Converter colunas numéricas
    # -------------------------------
    num_cols = ["valor_do_item", "repasse_valor_escola", "aluno_interno", "aluno_externo"]
    for col in num_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("R$", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------------
    # Filtros laterais
    # -------------------------------
    st.sidebar.header("Filtros")
    if "marca" in df.columns:
        marcas = st.sidebar.multiselect("Marca", options=df["marca"].unique(), default=df["marca"].unique())
    else:
        marcas = []

    if "unidade" in df.columns:
        unidades = st.sidebar.multiselect("Unidade", options=df["unidade"].unique(), default=df["unidade"].unique())
    else:
        unidades = []

    if "classificacao_receita" in df.columns:
        classificacoes = st.sidebar.multiselect(
            "Classificação Receita",
            options=df["classificacao_receita"].unique(),
            default=df["classificacao_receita"].unique()
        )
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

    kpi1.metric("Soma Valor do Item", f"R$ {df_filtrado['valor_do_item'].sum():,.2f}" if 'valor_do_item' in df_filtrado else "0")
    kpi2.metric("Soma Repasse $ Escola", f"R$ {df_filtrado['repasse_valor_escola'].sum():,.2f}" if 'repasse_valor_escola' in df_filtrado else "0")
    kpi3.metric("Soma Alunos Internos", f"{int(df_filtrado['aluno_interno'].sum())}" if 'aluno_interno' in df_filtrado else "0")
    kpi4.metric("Soma Alunos Externos", f"{int(df_filtrado['aluno_externo'].sum())}" if 'aluno_externo' in df_filtrado else "0")

    # -------------------------------
    # Tabela detalhada
    # -------------------------------
    st.header("Tabela Detalhada")
    display_cols = [c for c in [
        "marca", "unidade", "classificacao_receita", "nome_do_item",
        "valor_do_item", "repasse_perc_escola", "repasse_valor_escola",
        "aluno_interno", "aluno_externo"
    ] if c in df_filtrado.columns]

    st.dataframe(df_filtrado[display_cols])

    # -------------------------------
    # Gráficos interativos
    # -------------------------------
    st.header("Gráficos")

    # Gráfico 1: Valor do Item por Unidade
    if "unidade" in df_filtrado.columns and "valor_do_item" in df_filtrado.columns:
        fig1 = px.bar(
            df_filtrado.groupby("unidade")["valor_do_item"].sum().reset_index(),
            x="unidade",
            y="valor_do_item",
            title="Soma do Valor do Item por Unidade",
            text_auto=".2s"
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Repasse $ Escola por Classificação Receita
    if "classificacao_receita" in df_filtrado.columns and "repasse_valor_escola" in df_filtrado.columns:
        fig2 = px.bar(
            df_filtrado.groupby("classificacao_receita")["repasse_valor_escola"].sum().reset_index(),
            x="classificacao_receita",
            y="repasse_valor_escola",
            title="Soma do Repasse $ Escola por Classificação Receita",
            text_auto=".2s"
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Por favor, faça upload do arquivo CSV para visualizar o dashboard.")
