# Copia o df_consolidado real (sem TOTAL na base)
df_display = df_consolidado.copy()

# Cria linha de TOTAL para estilo
total_values = {
    "marca": "TOTAL",
    "unidade": "",
    "classificacao_receita": "",
    "nome_do_item": "",
    "valor_do_item": df_display["valor_do_item"].sum(),
    "repasse_valor_escola": df_display["repasse_valor_escola"].sum(),
    "repasse_perc_escola": df_display["repasse_perc_escola"].mean(),
    "aluno_interno": df_display["aluno_interno"].sum(),
    "aluno_externo": df_display["aluno_externo"].sum()
}
df_total = pd.DataFrame([total_values])

# Concatena só para visual, mas vamos estilizar
df_display_total = pd.concat([df_display, df_total], ignore_index=True)

# Formatação financeira e percentual
for col in ["valor_do_item","repasse_valor_escola"]:
    df_display_total[col] = df_display_total[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
df_display_total["repasse_perc_escola"] = df_display_total["repasse_perc_escola"].apply(lambda x: f"{x:.1f}%")

# Estilo: deixar linha TOTAL em negrito e fundo cinza
def highlight_total(row):
    if row["marca"] == "TOTAL":
        return ['font-weight: bold; background-color: #d3d3d3']*len(row)
    else:
        return ['']*len(row)

st.dataframe(df_display_total.style.apply(highlight_total, axis=1), use_container_width=True)
