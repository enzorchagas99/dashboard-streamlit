import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Meu Dashboard")

st.write("Faça o upload do seu arquivo CSV abaixo:")
uploaded_file = st.file_uploader("Escolha o CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Visualização dos dados")
    st.dataframe(df)

    st.subheader("Exemplo de gráfico")
    if not df.empty:
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            fig = px.histogram(df, x=numeric_cols[0])
            st.plotly_chart(fig)
        else:
            st.write("Sem colunas numéricas para plotar gráfico")
