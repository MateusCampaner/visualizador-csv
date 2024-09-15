import pandas as pd
import streamlit as st
import sqlite3
import gdown

st.set_page_config(page_title='Visualizador de Arquivos', page_icon='📝')

st.sidebar.header("📝 Visualizador de Arquivos")

if st.sidebar.button('Visualizar Arquivos'):
    st.session_state.page = 'Visualizar Arquivos'

if st.sidebar.button('Ler do Google Drive'):
    st.session_state.page = 'Ler do Google Drive'

if st.sidebar.button('Consulta SQL em CSVs'):
    st.session_state.page = 'Consulta SQL em CSVs'

if 'page' not in st.session_state:
    st.session_state.page = 'Visualizar Arquivos'

def display_data(df, page_size=100000):
    num_pages = len(df) // page_size + 1
    page = st.slider('Selecione a página', 1, num_pages, 1)
    start = (page - 1) * page_size
    end = start + page_size
    st.write(df[start:end])

if 'page' in st.session_state and st.session_state.page == "Visualizar Arquivos":
    st.header("📊 Visualizar Arquivo")

    st.subheader('Upload de Arquivo')
    st.text("Extensões permitidas: CSV, XLSX")
    uploaded_file = st.file_uploader("Escolha um arquivo", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            
            if df.empty:
                st.warning("O arquivo está vazio ou não contém dados válidos.")
            else:
                st.write("Colunas do arquivo:")
                selected_columns = st.multiselect(
                    'Selecione as colunas para exibir',
                    options=df.columns.tolist(),
                    default=df.columns.tolist()
                )

                st.write("Dados do arquivo:")
                if selected_columns:
                    df_filtered = df[selected_columns]
                    st.session_state['df_filtered'] = df_filtered
                    st.write(df_filtered)

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
                    quantidade_linhas = df.shape[0]

                    qtd_unicos, qtd_linhas = st.columns(2)
                    qtd_unicos.metric(label=f"Quantidade de valores únicos em {coluna_selecionada}", value=quantidade_valores_unicos)
                    qtd_linhas.metric(label="Quantidade total de linhas no DataFrame", value=quantidade_linhas)

                    valores_unicos_str = ', '.join(map(str, valores_unicos))

                    st.text_area("Copie o texto abaixo:", value=valores_unicos_str)

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
            

elif st.session_state.page == "Ler do Google Drive":
    st.header("📂 Ler Arquivo do Google Drive")

    st.subheader('Insira o link do arquivo do Google Drive')
    drive_link = st.text_input("Link do Google Drive", placeholder="https://drive.google.com/file/d/FILE_ID/view?usp=sharing")

    if drive_link:
        try:
            file_id = None
            if 'id=' in drive_link:
                file_id = drive_link.split('id=')[-1]
            elif '/d/' in drive_link:
                file_id = drive_link.split('/d/')[-1].split('/')[0]

            if file_id:
                url = f'https://drive.google.com/uc?id={file_id}'
                output = 'file_from_drive.csv'
                
                gdown.download(url, output, quiet=False)

                df = pd.read_csv(output)
                st.write("Dados do arquivo:")

                selected_columns = st.multiselect(
                    'Selecione as colunas para exibir',
                    options=df.columns.tolist(),
                    default=df.columns.tolist()
                )

                if selected_columns:
                    df_filtered = df[selected_columns]
                    display_data(df_filtered)

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
                    quantidade_linhas = df.shape[0]

                    qtd_unicos, qtd_linhas = st.columns(2)
                    qtd_unicos.metric(label=f"Quantidade de valores únicos em {coluna_selecionada}", value=quantidade_valores_unicos)
                    qtd_linhas.metric(label="Quantidade total de linhas no DataFrame", value=quantidade_linhas)

                    valores_unicos_str = ', '.join(map(str, valores_unicos))

                    st.text_area("Copie o texto abaixo:", value=valores_unicos_str)
            else:
                st.error("Link inválido. Por favor, insira um link correto do Google Drive.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo do Google Drive: {e}")

elif st.session_state.page == "Consulta SQL em CSVs":
    st.header("🎲 Consulta SQL em CSVs")
    st.subheader('Upload de Arquivo')
    st.text("Extensões permitidas: CSV, XLSX")

    def load_file(file):
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            st.error("Formato de arquivo não suportado!")
            return None
        return df

    def execute_sql_query(dfs, query):
        with sqlite3.connect(":memory:") as conn:
            for i, df in enumerate(dfs):
                df.to_sql(f'data{i+1}', conn, index=False, if_exists='replace')
            result = pd.read_sql_query(query, conn)
        return result

    uploaded_files = st.file_uploader("Escolha seus arquivos CSV ou XLSX", type=["csv", "xlsx"], accept_multiple_files=True)

    if uploaded_files:
        dfs = []
        for file in uploaded_files:
            df = load_file(file)
            if df is not None:
                dfs.append(df)
                st.write(f"Dados do arquivo {file.name} carregado:")

        query = st.text_area("Consulta SQL", height=300)

        if st.button("Executar Consulta"):
            try:
                result = execute_sql_query(dfs, query)
                st.write("Resultado da consulta:")
                st.write(result)

                valores_str = result.to_csv(index=False)

                st.text_area("Copie o texto abaixo:", value=valores_unicos_str)
                    
            except Exception as e:
                st.error(f"Erro ao executar a consulta: {e}")
