#30/07/2025
#@IvanReis  
#HSF - PAINEL FLORENCE - CENSO

import streamlit as st
import pandas as pd
import datetime
import os
import oracledb

st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Censo")

def encontrar_diretorio_instantclient(nome_pasta="instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6"):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    diretorio_raiz_projeto = os.path.dirname(diretorio_atual)
    caminho_instantclient = os.path.join(diretorio_raiz_projeto, nome_pasta)
    if os.path.exists(caminho_instantclient):
        return caminho_instantclient
    else:
        return None

def conectar_banco_seguro():
    caminho_instantclient = encontrar_diretorio_instantclient()
    if not caminho_instantclient:
        st.error("Erro crítico: Oracle Instant Client não encontrado.")
        return None
    try:
        oracledb.init_oracle_client(lib_dir=caminho_instantclient)
    except Exception as e_init:
        if "already been initialized" not in str(e_init):
            st.error("Erro ao inicializar o cliente Oracle. Verifique a configuração.")
            return None
    try:
        connection = oracledb.connect(
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            dsn=st.secrets["database"]["dsn"]
        )
        return connection
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def carregar_dados(data_inicial, data_final):
    df = pd.DataFrame()
    connection = conectar_banco_seguro()
    if not connection:
        return df
    query_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query.sql")
    try:
        with open(query_file_path, "r", encoding="utf-8") as f:
            query = f.read()
    except Exception as e:
        st.error(f"Erro ao ler query.sql: {e}")
        return df
    params = {'DATA_INICIAL': data_inicial.strftime('%d/%m/%Y'), 'DATA_FINAL': data_final.strftime('%d/%m/%Y')}
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
    except Exception as e:
        st.error(f"Erro ao executar a query: {e}")
    return df

def calcular_indicadores(df):
    indicadores = {}
    indicadores['total_atendimentos'] = df['NR_ATENDIMENTO'].dropna().nunique()
    indicadores['total_mews'] = pd.to_numeric(df['CD_MEWS'], errors='coerce').sum()
    indicadores['contagem_mews'] = df['DS_MEWS'].value_counts()
    indicadores['total_braden'] = pd.to_numeric(df['CD_BRADEN'], errors='coerce').sum()
    indicadores['contagem_braden'] = df['DS_BRADEN'].value_counts()
    indicadores['total_saps3'] = pd.to_numeric(df['CD_SAPSIII'], errors='coerce').sum()
    indicadores['contagem_saps3'] = df['DS_SAPSIII'].value_counts()
    indicadores['total_rass'] = pd.to_numeric(df['CD_RASS'], errors='coerce').sum()
    indicadores['contagem_rass'] = df['DS_RASS'].value_counts()
    indicadores['total_fugulin'] = df['CD_FUGULIN'].dropna().count()
    indicadores['contagem_fugulin'] = df['FUGULIN'].value_counts()
    indicadores['total_martins'] = df['MARTINS'].dropna().count()
    indicadores['total_glasgow'] = pd.to_numeric(df['CD_GLASGOW'], errors='coerce').sum()
    indicadores['contagem_glasgow'] = df['DS_GLASGOW'].value_counts()
    return indicadores

def exibir_cartoes_indicadores(indicadores):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Atendimentos", int(indicadores['total_atendimentos']))
        st.metric("Total de MEWS", int(indicadores['total_mews']))
        st.metric("Total de BRADEN", int(indicadores['total_braden']))
        st.metric("Total de SAPS3", int(indicadores['total_saps3']))
        st.metric("Total de RASS", int(indicadores['total_rass']))
    with col2:
        st.metric("Total de FUGULIN", int(indicadores['total_fugulin']))
        st.metric("Total de MARTINS", int(indicadores['total_martins']))
        st.metric("Total de GLASGOW", int(indicadores['total_glasgow']))
    with col3:
        st.write("Quantidade por DS_MEWS:")
        st.dataframe(indicadores['contagem_mews'])
        st.write("Quantidade por DS_BRADEN:")
        st.dataframe(indicadores['contagem_braden'])
        st.write("Quantidade por DS_SAPSIII:")
        st.dataframe(indicadores['contagem_saps3'])
        st.write("Quantidade por DS_RASS:")
        st.dataframe(indicadores['contagem_rass'])
        st.write("Quantidade por FUGULIN:")
        st.dataframe(indicadores['contagem_fugulin'])
        st.write("Quantidade por DS_GLASGOW:")
        st.dataframe(indicadores['contagem_glasgow'])

# Interface principal
st.title("Indicadores de Pacientes - Censo")

with st.sidebar:
    data_inicial = st.date_input("Data inicial", value=datetime.date.today())
    data_final = st.date_input("Data final", value=datetime.date.today())
    buscar = st.button("Buscar dados")

if 'buscar' in locals() and buscar:
    df = carregar_dados(data_inicial, data_final)
    if not df.empty:
        indicadores = calcular_indicadores(df)
        exibir_cartoes_indicadores(indicadores)
        st.subheader("Detalhes dos Pacientes")
        st.dataframe(df)
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")