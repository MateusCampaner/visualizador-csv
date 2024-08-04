import pandas as pd
import streamlit as st
import base64
import sqlite3
import pyperclip

st.set_page_config(page_title='Visualizador de CSVs', page_icon='📝')

st.sidebar.header("📝 Visualizador de CSVs")

def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() 
    href = f'<a href="data:file/csv;base64,{b64}" download="dados_filtrados.csv">Download do CSV</a>'
    return href

pagina = st.sidebar.selectbox(
    "Escolha",
    ('Visualizar CSV', 'Consulta SQL em CSVs')
)


if pagina == "Visualizar CSV":
    st.header("📊 Visualizar CSV")

    st.subheader('Upload de CSV')
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.write("Dados do arquivo CSV:")

        selected_columns = st.multiselect(
            'Selecione as colunas para exibir',
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        if selected_columns:
            df_filtered = df[selected_columns]
            st.write(df_filtered)

            st.session_state['df_filtered'] = df_filtered

        st.write("Selecione uma coluna para visualizar mais informações:")
        coluna_selecionada = st.selectbox(
            "Escolha uma coluna",
            options=df.columns.tolist()
        )

        if coluna_selecionada:

            valores_unicos = df[coluna_selecionada].unique()
            st.write(f"Valores únicos de '{coluna_selecionada}':")
            st.write(valores_unicos)

            quantidade_valores_unicos = df[coluna_selecionada].nunique()
            st.write(f"Quantidade de valores únicos em '{coluna_selecionada}': {quantidade_valores_unicos}")

            quantidade_linhas = df.shape[0]
            st.write(f"Quantidade total de linhas no DataFrame: {quantidade_linhas}")

            valores_unicos_str = ', '.join(map(str, valores_unicos))

        if st.button("Copiar valores únicos para a área de transferência"):
            pyperclip.copy(valores_unicos_str)
            st.write("Valores únicos copiados para a área de transferência!")

if pagina == "Consulta SQL em CSVs":

    st.title("Consulta SQL em CSVs")

    def load_csv(file):
        df = pd.read_csv(file)
        return df

    def execute_sql_query(dfs, query):
        with sqlite3.connect(":memory:") as conn:
            for i, df in enumerate(dfs):
                df.to_sql(f'data{i+1}', conn, index=False, if_exists='replace')
            result = pd.read_sql_query(query, conn)
        return result

    uploaded_files = st.file_uploader("Escolha até 3 arquivos CSV", type="csv", accept_multiple_files=True)

    if uploaded_files:
        dfs = [load_csv(file) for file in uploaded_files]
        for i, df in enumerate(dfs):
            st.write(f"Dados do CSV {i+1} carregado:")
            st.write(df)
        
        query = st.text_area(height=300, label="Consulta SQL")
        
        if st.button("Executar Consulta"):
            try:
                result = execute_sql_query(dfs, query)
                st.write("Resultado da consulta:")
                st.write(result)

                valores_str = result.to_csv(index=False)  

                if st.button("Copiar dados para a área de transferência"):
                    pyperclip.copy(valores_str)
                    st.write("Dados copiados para a área de transferência!")
                    
            except Exception as e:
                st.error(f"Erro ao executar a consulta: {e}")

            

