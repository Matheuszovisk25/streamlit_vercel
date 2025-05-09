import streamlit as st
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Dados da Embrapa", layout="wide")
st.title("Dados da Embrapa - API no Vercel")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def buscar_dados(api_url: str, chave_dados: str):
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        try:
            json_data = response.json()
            fonte = json_data.get("fonte", "desconhecida")
            dados = json_data[chave_dados]
            return pd.DataFrame(dados), fonte
        except Exception as e:
            st.error(f"Erro ao processar os dados: {e}")
    else:
        st.error(f"Erro ao acessar os dados: {response.status_code}")
        st.code(response.text)


def exibir_downloads(df: pd.DataFrame, nome_base: str):
    st.markdown("Baixar os dados:")
    col1, col2, col3 = st.columns(3)

    with col1:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
        st.download_button(
            label="Baixar Excel",
            data=excel_buffer.getvalue(),
            file_name=f"{nome_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar CSV",
            data=csv_data,
            file_name=f"{nome_base}.csv",
            mime="text/csv"
        )

    with col3:
        json_data = df.to_json(orient="records", indent=2).encode("utf-8")
        st.download_button(
            label="Baixar JSON",
            data=json_data,
            file_name=f"{nome_base}.json",
            mime="application/json"
        )

def mostrar_dados_por_ano(titulo: str, rota: str, prefixo_chave: str, ano_min=1970, ano_max=2023):
    st.subheader(titulo)
    key_ano = f"input_{rota.replace('/', '_')}"
    ano = int(st.number_input("Informe o ano:", min_value=ano_min, max_value=ano_max, step=1, value=ano_max, key=key_ano))
    url = f"https://vercel-teste-9yev.onrender.com/{rota}?ano={ano}"
    chave = f"{prefixo_chave} - {ano}"
    resultado = buscar_dados(url, chave)

    if resultado:
        df, fonte = resultado
        st.info(f"📡 Fonte dos dados: **{fonte.upper()}**")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
        exibir_downloads(df, f"{rota}_{ano}")
        return df

menu = st.sidebar.selectbox("Selecione uma categoria de dados", [
    "Produção",
    "Comercialização",
    "Processamento",
    "Importação",
    "Exportação"
])


if menu == "Produção":
    df = mostrar_dados_por_ano("Produção de Vinhos EMBRAPA", "producao", "Producao Vinhos Embrapa")
    df["Quantidade"] = (
        df["Quantidade"]
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',','.', regex=False)
    )
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")


    df_titulos = df[df["Produto"].str.isupper()]
    fig = px.bar(
        df_titulos.sort_values("Quantidade", ascending=True), 
        x="Quantidade", 
        y="Produto", 
        title = "Categorias mais produzidas",
        orientation="h",
        labels={"Produto": "Categoria", "Quantidade": "Quantidade Produzida"},
        text_auto=".5s",
        color="Quantidade",  
        color_continuous_scale="Purples"
        )
    
    fig.update_layout(
        xaxis_tickangle=-20,
        coloraxis_showscale=False
        )
    
    fig2 = px.line
    
    st.plotly_chart(fig)

  


elif menu == "Comercialização":
    mostrar_dados_por_ano("Comercialização de Vinhos EMBRAPA", "comercializacao", "Comercializacao de vinhos")
    
elif menu == "Processamento":
    mostrar_dados_por_ano("Processamento Viníferas EMBRAPA", "processamento/viniferas", "Processamento de viniferas")
    mostrar_dados_por_ano("Processamento Americanas EMBRAPA", "processamento/americanas", "Processamento americanas e hibridas")
    mostrar_dados_por_ano("Processamento Uvas de Mesa", "processamento/uvas_de_mesa", "Processamento uvas de mesa")

elif menu == "Importação":
    mostrar_dados_por_ano("Importação Vinhos de Mesa", "importacao/vinhos_de_mesa", "Importacao vinhos de mesa", ano_max=2024)
    mostrar_dados_por_ano("Importação Espumantes", "importacao/espumantes", "Importacao espumantes", ano_max=2024)
    mostrar_dados_por_ano("Importação Uvas Frescas", "importacao/uvas_frescas", "Importacao uvas frescas", ano_max=2024)
    mostrar_dados_por_ano("Importação Uvas Passas", "importacao/uvas_passas", "Importacao uvas passas", ano_max=2024)
    mostrar_dados_por_ano("Importação Suco de Uva", "importacao/suco_de_uvas", "Importacao suco de uva", ano_max=2024)

elif menu == "Exportação":
    mostrar_dados_por_ano("Exportação Vinho de Mesa", "exportacao/vinho_de_mesa", "Exportacao vinho de mesa", ano_max=2024)
    mostrar_dados_por_ano("Exportação Espumantes", "exportacao/espumantes", "Exportacao espumantes", ano_max=2024)
    mostrar_dados_por_ano("Exportação Uvas Frescas", "exportacao/uvas_frescas", "Exportacao uvas frescas", ano_max=2024)
    mostrar_dados_por_ano("Exportação Suco de Uva", "exportacao/suco_de_uva", "Exportacao suco de uva", ano_max=2024)
