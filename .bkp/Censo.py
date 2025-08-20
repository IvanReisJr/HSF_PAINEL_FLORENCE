# Data da última modificação: 2025-08-05
# Autor: @IvanReis
# Descrição: HSF - Painel Florence - Página de Censo de Pacientes

import streamlit as st
import pandas as pd
import datetime
import os
import io
import oracledb

# --- Configuração da Página ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- Funções de Conexão com o Banco (Refatoradas) ---

_ORACLE_CLIENT_INITIALIZED = False

def initialize_oracle_client():
    """
    Inicializa o cliente Oracle apenas uma vez para evitar erros.
    Esta função é chamada no início do script.
    """
    global _ORACLE_CLIENT_INITIALIZED
    if _ORACLE_CLIENT_INITIALIZED:
        return True

    # Encontra o diretório do instant client
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    diretorio_raiz_projeto = os.path.dirname(diretorio_atual)
    nome_pasta = "instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6"
    caminho_instantclient = os.path.join(diretorio_raiz_projeto, nome_pasta)

    if not os.path.exists(caminho_instantclient):
        st.error("Erro crítico: Oracle Instant Client não encontrado.")
        return False

    try:
        oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        _ORACLE_CLIENT_INITIALIZED = True
        return True
    except Exception as e_init:
        # Ignora o erro se o cliente já foi inicializado em outra página
        if "already been initialized" not in str(e_init):
            st.error(f"Erro ao inicializar o cliente Oracle: {e_init}")
            return False
        _ORACLE_CLIENT_INITIALIZED = True
        return True

# --- Funções de Carregamento de Dados (com Cache) ---

def carregar_setores():
    """Carrega os setores de internação para o filtro."""
    if not _ORACLE_CLIENT_INITIALIZED:
        st.error("Cliente Oracle não inicializado.")
        return pd.DataFrame(columns=["CD_SETOR_ATENDIMENTO", "DS_SETOR_ATENDIMENTO"])

    query = """
        SELECT CD_SETOR_ATENDIMENTO, DS_SETOR_ATENDIMENTO
        FROM SETOR_ATENDIMENTO
        WHERE CD_CLASSIF_SETOR IN (3, 4) AND IE_SITUACAO = 'A'
        ORDER BY DS_SETOR_ATENDIMENTO
    """
    try:
        conn = st.connection("oracle_db", type="sql")
        df = conn.query(query)
        df.columns = [c.upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar setores: {e}")
        return pd.DataFrame(columns=["CD_SETOR_ATENDIMENTO", "DS_SETOR_ATENDIMENTO"])

def carregar_dados(data_inicial, data_final, cd_setor):
    """Carrega os dados principais do censo com base nos filtros."""
    if not _ORACLE_CLIENT_INITIALIZED:
        st.error("Cliente Oracle não inicializado.")
        return pd.DataFrame()

    query_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query.sql")
    try:
        with open(query_file_path, "r", encoding="utf-8") as f:
            query = f.read()
    except Exception as e:
        st.error(f"Erro ao ler query.sql: {e}")
        return pd.DataFrame()

    params = {
        'DATA_INICIAL': data_inicial.strftime('%d/%m/%Y'),
        'DATA_FINAL': data_final.strftime('%d/%m/%Y'),
        'CD_SETOR_P': cd_setor
    }
    try:
        conn = st.connection("oracle_db", type="sql")
        df = conn.query(query, params=params, ttl=3600)  # Cache por 1 hora
        df.columns = [c.upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao executar a query: {e}")

def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Converte um DataFrame para um arquivo Excel (.xlsx) em memória e retorna os bytes.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='IndicadoresCenso')
    # Pega o conteúdo do buffer em memória
    processed_data = output.getvalue()
    return processed_data

# --- Funções de Lógica e Exibição (Refatoradas) ---

def calcular_indicadores(df):
    """
    Calcula os indicadores de forma modular e extensível.
    """
    indicadores = {
        'total_atendimentos': df['NR_ATENDIMENTO'].dropna().count()
    }

    config_indicadores = [
        {'nome': 'mews', 'cd': 'CD_MEWS', 'ds': 'MEWS', 'tipo': 'contagem'},
        {'nome': 'braden', 'cd': 'CD_BRADEN', 'ds': 'BRADEN', 'tipo': 'contagem'},
        {'nome': 'saps3', 'cd': 'CD_SAPSIII', 'ds': 'SAP3', 'tipo': 'contagem'},
        {'nome': 'rass', 'cd': 'CD_RASS', 'ds': 'RASS', 'tipo': 'contagem'},
        {'nome': 'glasgow', 'cd': 'CD_GLASGOW', 'ds': 'GLASGOW', 'tipo': 'contagem'},
        {'nome': 'fugulin', 'cd': 'CD_FUGULIN', 'ds': 'FUGULIN', 'tipo': 'contagem'},
        {'nome': 'martins', 'cd': 'MARTINS', 'ds': 'MARTINS', 'tipo': 'contagem'},
    ]

    for config in config_indicadores:
        nome, col_cd, col_ds, tipo = config['nome'], config['cd'], config['ds'], config['tipo']
        
        if col_cd in df.columns:
            if tipo == 'soma':
                indicadores[f'total_{nome}'] = pd.to_numeric(df[col_cd], errors='coerce').sum()
            elif tipo == 'contagem':
                indicadores[f'total_{nome}'] = df[col_cd].dropna().count()
        
        if col_ds and col_ds in df.columns:
            # Cria o DataFrame de contagem de forma robusta, nomeando os eixos diretamente.
            df_counts = df[col_ds].value_counts().rename_axis('Descrição').reset_index(name='Qtde')
            indicadores[f'contagem_{nome}'] = df_counts
            
    return indicadores

def exibir_cartoes_indicadores(indicadores):
    """
    Exibe os indicadores de forma modular e extensível com o novo layout.
    """
    # --- Linha 1: Total de Atendimentos ---
    if 'total_atendimentos' in indicadores:
        st.metric("🤒 Total de Atendimentos", int(indicadores['total_atendimentos']))
    st.divider()

    # --- Linha 2: 4 colunas de métricas ---
    metricas_linha2 = [
        ("Total de MEWS", 'total_mews'),
        ("Total de BRADEN", 'total_braden'),
        ("Total de SAP3", 'total_saps3'),
        ("Total de RASS", 'total_rass'),
    ]
    cols_linha2 = st.columns(4)
    for col, (label, key) in zip(cols_linha2, metricas_linha2):
        with col:
            if key in indicadores:
                st.metric(label, int(indicadores[key]))

    # --- Linha 3: 3 colunas de métricas ---
    metricas_linha3 = [
        ("Total de FUGULIN", 'total_fugulin'),
        ("Total de MARTINS", 'total_martins'),
        ("Total de GLASGOW", 'total_glasgow'),
    ]
    cols_linha3 = st.columns(4)
    for col, (label, key) in zip(cols_linha3, metricas_linha3):
        with col:
            if key in indicadores:
                st.metric(label, int(indicadores[key]))

    st.divider()

    # --- Linha 4: Quantidades em 3 colunas ---
    st.subheader("Distribuição por Escala")

    # CSS para forçar a largura das colunas nas tabelas de distribuição.
    # Isso garante que todas as tabelas tenham o mesmo layout fixo e proporcional.
    custom_table_css = """
    <style>
        .dist-table {
            width: 100%;
            border-collapse: collapse;
        }
        .dist-table th, .dist-table td {
            padding: 6px 8px;
        }
        .dist-table th:nth-child(1), .dist-table td:nth-child(1) { /* Coluna Descrição */
            width: 75% !important;
            text-align: left;
            word-wrap: break-word;
        }
        .dist-table th:nth-child(2), .dist-table td:nth-child(2) { /* Coluna Qtde */
            width: 25% !important;
            text-align: right;
        }
        .scrollable-grid {
            max-height: 175px; /* Altura aproximada para 4 linhas + cabeçalho */
            overflow-y: auto;  /* Adiciona scroll vertical apenas quando necessário */
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-bottom: 1rem; /* Adiciona um espaço abaixo de cada grid */
        }
    </style>
    """
    st.markdown(custom_table_css, unsafe_allow_html=True)

    layout_dataframes = [
        ("MEWS", 'contagem_mews'),
        ("BRADEN", 'contagem_braden'),
        ("SAP3", 'contagem_saps3'),
        ("RASS", 'contagem_rass'),
        ("FUGULIN", 'contagem_fugulin'),
        ("GLASGOW", 'contagem_glasgow'),
        ("MARTINS", 'contagem_martins'),
    ]

    cols_dataframes = st.columns(3)

    for i, (label, key) in enumerate(layout_dataframes):
        with cols_dataframes[i % 3]:
            # Exibe o título do grid, garantindo que ele sempre apareça.
            st.write(f"**Quantidade por {label}**")

            # Obtém o DataFrame se ele existir; caso contrário, cria um DataFrame vazio.
            if key in indicadores:
                df_dist = indicadores[key].copy()
            else:
                df_dist = pd.DataFrame(columns=['Descrição', 'Qtde'])

            # Garante que o DataFrame tenha uma altura mínima de 4 linhas para simetria visual.
            min_target_rows = 4
            rows_to_add = min_target_rows - len(df_dist)
            if rows_to_add > 0:
                # Cria linhas vazias com um valor de 'Descrição' único e invisível
                # para evitar erros ao aplicar o estilo ou converter para HTML.
                empty_rows_data = [
                    ['\u200b' * (n + 1), ''] for n in range(rows_to_add)
                ]
                empty_rows = pd.DataFrame(empty_rows_data, columns=['Descrição', 'Qtde'])
                df_dist = pd.concat([df_dist, empty_rows], ignore_index=True)

            # Trunca a descrição para textos longos.
            df_dist['Descrição'] = df_dist['Descrição'].apply(
                lambda x: (x[:35] + '...') if isinstance(x, str) and len(x) > 44 else x
            )

            # Converte para HTML sem o índice do DataFrame.
            html_table = df_dist.to_html(
                classes='dist-table',
                header=True,
                index=False,
                border=0
            )

            # Envolve a tabela em um div com a classe de scroll e a exibe.
            st.markdown(f'<div class="scrollable-grid">{html_table}</div>', unsafe_allow_html=True)

# --- Script Principal ---

# Inicializa o cliente Oracle uma única vez
initialize_oracle_client()

st.title("Indicadores de Pacientes - Censo")

# --- Filtros Principais ---
col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns([3, 2, 2, 2])

with col_filtro1:
    df_setores = carregar_setores()
    if not df_setores.empty:
        setores_dict = dict(zip(df_setores['DS_SETOR_ATENDIMENTO'], df_setores['CD_SETOR_ATENDIMENTO']))
        opcoes_setor = ["Todos"] + list(setores_dict.keys())
        setor_selecionado_ds = st.selectbox("Setor", options=opcoes_setor)

        if setor_selecionado_ds == "Todos":
            cd_setor_selecionado = '0'
        else:
            cd_setor_selecionado = str(setores_dict[setor_selecionado_ds])
    else:
        st.warning("Setores não carregados.")
        setor_selecionado_ds = st.selectbox("Setor", options=["Todos"], disabled=True)
        cd_setor_selecionado = '0'

with col_filtro2:
    data_inicial = st.date_input("Data inicial", value=datetime.date.today())

with col_filtro3:
    data_final = st.date_input("Data final", value=datetime.date.today(), min_value=data_inicial)

with col_filtro4:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar dados", type="primary", use_container_width=True)

# --- Lógica de Exibição ---
if buscar:
    with st.spinner("Buscando dados no banco... Por favor, aguarde."):
        # A função carregar_dados agora é cacheada pelo st.connection
        df_resultado = carregar_dados(data_inicial, data_final, cd_setor_selecionado)

    if df_resultado is None:
        # Erro já foi exibido dentro da função carregar_dados
        pass
    elif not df_resultado.empty:
        
        indicadores = calcular_indicadores(df_resultado)
        exibir_cartoes_indicadores(indicadores)
        st.divider() # Adiciona um espaçamento visual antes da seção de download

        # Prepara o DataFrame para exibição e download
        colunas_para_remover = [
            'CD_SETOR_ATENDIMENTO', 'CD_MEWS', 'CD_BRADEN',
            'CD_MORSE', 'CD_SAPSIII', 'CD_RASS', 'CD_GLASGOW','CD_FUGULIN'
        ]
        df_para_exibir = df_resultado.drop(columns=colunas_para_remover, errors='ignore')
        df_para_exibir = df_para_exibir.sort_values(by=['ENTRADA', 'LEITO'])

        # --- Botão de Download para Excel ---
        excel_bytes = dataframe_to_excel_bytes(df_para_exibir)
        st.download_button(
            label="📥 Baixar dados em Excel",
            data=excel_bytes,
            file_name="Indicadores_de_Pacientes_Censo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        with st.expander("Ver Detalhes dos Pacientes"):
            st.dataframe(df_para_exibir, use_container_width=True)

    else: # Se a busca foi feita mas não retornou dados
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
else: # Se nenhuma busca foi feita ainda
    st.info("Selecione os filtros acima e clique em 'Buscar dados'.")
