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
    # Conversão de colunas
    # -------------------------------
    # Financeiro
    for col in ["valor_do_item","repasse_valor_escola"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Percentual
    if "repasse_perc_escola" in df.columns:
        df["repasse_perc_escola"] = pd.to_numeric(df["repasse_perc_escola"], errors="coerce")

    # Alunos: n/A → 0, valores inteiros
    for col in ["aluno_interno","aluno_externo"]:
        if col in df.columns:
            df[col] = df[col].replace("n/A", 0)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # -------------------------------
    # Filtros
    # -------------------------------
    st.sidebar.header("Filtros")
    marcas = st.sidebar.multiselect("Marca", options=df["marca"].dropna().unique(), default=df["marca"].dropna().unique())
    unidades = st.sidebar.multiselect("Unidade", options=df["unidade"].dropna().unique(), default=df["unidade"].dropna().unique())
    classificacoes = st.sidebar.multiselect("Classificação Receita", options=df["classificacao_receita"].dropna().unique(), default=df["classificacao_receita"].dropna().unique())

    df_filtrado = df[df["marca"].isin(marcas) & df["unidade"].isin(unidades) & df["classificacao_receita"].isin(classificacoes)]

    # -------------------------------
    # Consolidação da tabela
    # -------------------------------
    group_cols = ["marca","unidade","classificacao_receita","nome_do_item"]

    agg_dict = {}
    if "valor_do_item" in df_filtrado.columns:
        agg_dict["valor_do_item"] = "sum"
    if "repasse_valor_escola" in df_filtrado.columns:
        agg_dict["repasse_valor_escola"] = "sum"
    if "repasse_perc_escola" in df_filtrado.columns:
        agg_dict["repasse_perc_escola"] = "mean"  # média percentual
    if "aluno_interno" in df_filtrado.columns:
        agg_dict["aluno_interno"] = lambda x: (x==1).sum()
    if "aluno_externo" in df_filtrado.columns:
        agg_dict["aluno_externo"] = lambda x: (x==1).sum()

    df_consolidado = df_filtrado.groupby(group_cols).agg(agg_dict).reset_index()

    # -------------------------------
    # Big Cards (KPIs)
    # -------------------------------
    st.header("KPIs")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Soma Valor do Item", f"R$ {df_consolidado['valor_do_item'].sum():,.0f}".replace(",", "."))
    kpi2.metric("Soma Repasse $ Escola", f"R$ {df_consolidado['repasse_valor_escola'].sum():,.0f}".replace(",", "."))
    kpi3.metric("Alunos Internos", f"{df_consolidado['aluno_interno'].sum():,}".replace(",", "."))
    kpi4.metric("Alunos Externos", f"{df_consolidado['aluno_externo'].sum():,}".replace(",", "."))

    # -------------------------------
    # Tabela detalhada consolidada
    # -------------------------------
    st.header("Tabela Consolidada")
    df_display = df_consolidado.copy()

    # Formatação
    for col in ["valor_do_item","repasse_valor_escola"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    if "repasse_perc_escola" in df_display.columns:
        df_display["repasse_perc_escola"] = df_display["repasse_perc_escola"].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "0.0%")

    st.dataframe(df_display, use_container_width=True)

    # -------------------------------
    # Gráficos consolidados
    # -------------------------------
    st.header("Gráficos")

    # Repasse $ Escola por Marca
    if "marca" in df_consolidado.columns:
        fig_marca = px.bar(
            df_consolidado.groupby("marca")["repasse_valor_escola"].sum().reset_index(),
            x="marca", y="repasse_valor_escola",
            title="Repasse $ Escola por Marca",
            text_auto=".2s"
        )
        st.plotly_chart(fig_marca, use_container_width=True)

    # Repasse $ Escola por Unidade
    if "unidade" in df_consolidado.columns:
        fig_unidade = px.bar(
            df_consolidado.groupby("unidade")["repasse_valor_escola"].sum().reset_index(),
            x="unidade", y="repasse_valor_escola",
            title="Repasse $ Escola por Unidade",
            text_auto=".2s"
        )
        st.plotly_chart(fig_unidade, use_container_width=True)

    # Repasse $ Escola por Classificação Receita
    if "classificacao_receita" in df_consolidado.columns:
        fig_class = px.bar(
            df_consolidado.groupby("classificacao_receita")["repasse_valor_escola"].sum().reset_index(),
            x="classificacao_receita", y="repasse_valor_escola",
            title="Repasse $ Escola por Classificação Receita",
            text_auto=".2s"
        )
        st.plotly_chart(fig_class, use_container_width=True)

else:
    st.info("Por favor, faça upload do arquivo CSV para visualizar o dashboard.")
