# Data da última modificação: 2025-04-15
# Autor: @IvanReis
# Descrição: HSF - Painel Florence - Página de Censo de Pacientes

import datetime
import os
import sys

import pandas as pd
import streamlit as st

# Adiciona o diretório raiz para importar utils_florence
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils_florence import (apply_florence_ui, calcular_indicadores,
                   ensure_oracle_initialized, export_to_excel)

# --- Configuração da Página ---
# st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Aplica o Design System Florence
apply_florence_ui()

# --- Funções de Carregamento de Dados ---

def carregar_setores():
    """Carrega os setores de internação para o filtro."""
    query = """
        SELECT CD_SETOR_ATENDIMENTO, DS_SETOR_ATENDIMENTO
        FROM SETOR_ATENDIMENTO
        WHERE CD_CLASSIF_SETOR IN (3, 4) AND IE_SITUACAO = 'A'
        ORDER BY DS_SETOR_ATENDIMENTO
    """
    try:
        conn = st.connection("oracle_db", type="sql")
        df = conn.query(query, ttl=3600)
        df.columns = [c.upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar setores: {e}")
        return pd.DataFrame(columns=["CD_SETOR_ATENDIMENTO", "DS_SETOR_ATENDIMENTO"])


def carregar_dados(data_inicial, data_final, lista_cd_setor):
    """Carrega os dados principais do censo com base nos filtros."""
    query_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "querys", "query_censo_florence.sql")
    try:
        with open(query_file_path, "r", encoding="utf-8") as f:
            query = f.read()
    except Exception as e:
        st.error(f"Erro ao ler query.sql: {e}")
        return pd.DataFrame()

    params = {
        'DATA_INICIAL': data_inicial.strftime('%d/%m/%Y'),
        'DATA_FINAL': data_final.strftime('%d/%m/%Y')
    }

    if lista_cd_setor:
        bind_vars = [f":sector_{i}" for i in range(len(lista_cd_setor))]
        for i, sector_code in enumerate(lista_cd_setor):
            params[f"sector_{i}"] = int(sector_code)
        in_clause = f"AND POR.CD_SETOR_ATENDIMENTO IN ({', '.join(bind_vars)})"
        query = query.replace("/*{{FILTER_SETOR}}*/", in_clause)
    else:
        query = query.replace("/*{{FILTER_SETOR}}*/", "")

    try:
        conn = st.connection("oracle_db", type="sql")
        df = conn.query(query, params=params, ttl=300, show_spinner=False)
        df.columns = [c.upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao executar a query: {e}")


def metric_card(label, value):
    """Exibe métrica dentro de um container com borda (estilizado via CSS como Glass)"""
    with st.container(border=True):
        st.metric(label, value)


def exibir_cartoes_indicadores(indicadores):
    """Exibe indicadores com layout premium e Glassmorphism."""
    
    # --- Linha 1: Foco Principal ---
    col_main, _ = st.columns([1, 2])
    with col_main:
        if 'total_atendimentos' in indicadores:
            metric_card("🤒 Total de Atendimentos", int(indicadores['total_atendimentos']))

    # --- Linha 2: Métricas Secundárias ---
    metricas_cards = [
        ("Total MEWS", 'total_mews'), ("Total Braden", 'total_braden'),
        ("Total SAP3", 'total_saps3'), ("Total Fugulin", 'total_fugulin'),
        ("Total RASS", 'total_rass'), ("Total Martins", 'total_martins'),
        ("Total Glasgow", 'total_glasgow')
    ]
    
    st.markdown("### 📊 Escalas Clínicas")
    cols = st.columns(4)
    for i, (label, key) in enumerate(metricas_cards):
        with cols[i % 4]:
            if key in indicadores:
                metric_card(label, int(indicadores[key]))

    # --- Pacientes sem Classificação ---
    st.markdown("### ⚠️ Lacunas de Classificação")
    metricas_vazias = [
        ("Sem MEWS", 'sem_classificacao_mews'), ("Sem Braden", 'sem_classificacao_braden'),
        ("Sem SAPS3", 'sem_classificacao_saps3'), ("Sem Fugulin", 'sem_classificacao_fugulin'),
        ("Sem RASS", 'sem_classificacao_rass'), ("Sem Martins", 'sem_classificacao_martins'),
        ("Sem Glasgow", 'sem_classificacao_glasgow'),
    ]
    cols_v = st.columns(4)
    for i, (label, key) in enumerate(metricas_vazias):
        with cols_v[i % 4]:
            if key in indicadores:
                metric_card(label, int(indicadores[key]))

    # --- Distribuição por Escala ---
    st.markdown("---")
    st.subheader("📋 Detalhamento das Escalas")

    layout_dataframes = [
        ("MEWS", 'contagem_mews'), ("BRADEN", 'contagem_braden'),
        ("SAP3", 'contagem_saps3'), ("RASS", 'contagem_rass'),
        ("MARTINS", 'contagem_martins'), ("GLASGOW", 'contagem_glasgow'),
        ("FUGULIN", 'contagem_fugulin')
    ]

    for i in range(0, len(layout_dataframes), 3):
        chunk = layout_dataframes[i:i+3]
        cols_df = st.columns(3)
        for j, (label, key) in enumerate(chunk):
            with cols_df[j]:
                st.write(f"Quantidade por {label}")
                if key in indicadores:
                    df_dist = indicadores[key].copy()
                    df_dist.columns = ['Descrição', 'Qtde']
                    df_dist['Descrição'] = df_dist['Descrição'].apply(lambda x: (str(x)[:40] + '...') if len(str(x)) > 40 else x)
                    st.dataframe(df_dist, hide_index=True, use_container_width=True, height=200)


# --- Script Principal ---
ensure_oracle_initialized()

st.title("🏥 Gestão de Censo e Escalas")

# --- Filtros ---
with st.container(border=True):
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        data_i = st.date_input("De:", value=datetime.date.today())
    with c2:
        data_f = st.date_input("Até:", value=datetime.date.today())
    with c3:
        buscar = st.button("🚀 Atualizar Dashboard", type="primary", use_container_width=True)
    
    df_setores = carregar_setores()
    if not df_setores.empty:
        setores_dict = dict(zip(df_setores['DS_SETOR_ATENDIMENTO'], df_setores['CD_SETOR_ATENDIMENTO']))
        sel_ds = st.multiselect("Setores Alfabetizados:", options=list(setores_dict.keys()))
        ids_setores = [setores_dict[ds] for ds in sel_ds]
    else:
        ids_setores = []


# --- Exibição ---
if buscar:
    if data_f < data_i:
        st.error("Intervalo de datas inválido.")
    else:
        with st.spinner("Sincronizando com TASY..."):
            df_res = carregar_dados(data_i, data_f, ids_setores)
        
        if df_res is not None and not df_res.empty:
            indicadores = calcular_indicadores(df_res)
            exibir_cartoes_indicadores(indicadores)
            
            st.markdown("---")
            col_exp, col_dl = st.columns([3, 1])
            with col_dl:
                excel = export_to_excel(df_res.drop(columns=['NR_ATENDIMENTO'], errors='ignore'))
                st.download_button("📥 Exportar Relatório", excel, "censo_florence.xlsx", width="stretch")
            
            with st.expander("🔍 Visualizar Base de Dados Completa"):
                st.dataframe(df_res, width="stretch")
        else:
            st.warning("Nenhum dado retornado para os critérios.")
else:
    st.info("Aguardando seleção de filtros para gerar indicadores.")
