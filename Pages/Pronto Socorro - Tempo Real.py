#11/12/2024
#@PLima
#HSF - PAINEL LABORATORIO

import streamlit as st
import pandas as pd
import os
import oracledb
import time
import datetime

#Configurando pagina para exibicao em modo WIDE:
st.set_page_config(layout="wide",initial_sidebar_state="collapsed",page_title="Pronto Socorro")

def agora():
    agora = datetime.datetime.now()
    agora = agora.strftime("%Y-%m-%d %H-%M-%S")
    return str(agora)

#apontamento para usar o Think Mod
def encontrar_diretorio_instantclient(nome_pasta="instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6"):
  # Obtém o diretório do script atual
  diretorio_atual = os.path.dirname(os.path.abspath(__file__))
  # Sobe um nível para o diretório raiz do projeto, onde a pasta do Instant Client está
  diretorio_raiz_projeto = os.path.dirname(diretorio_atual)

  # Constrói o caminho completo para a pasta do Instant Client
  caminho_instantclient = os.path.join(diretorio_raiz_projeto, nome_pasta)

  # Verifica se a pasta existe
  if os.path.exists(caminho_instantclient):
    return caminho_instantclient
  else:
    return None

_oracle_client_initialized_ps = False

def initialize_oracle_client_if_needed():
    global _oracle_client_initialized_ps
    if _oracle_client_initialized_ps:
        return True

    caminho_instantclient = encontrar_diretorio_instantclient()
    if not caminho_instantclient:
        print(f"{agora()} - Erro crítico: Oracle Instant Client não encontrado (Pronto Socorro). Não será possível conectar ao banco.")
        st.error("Oracle Instant Client não encontrado. A aplicação pode não funcionar corretamente.")
        return False
    
    try:
        print(f"{agora()} - Tentando inicializar Oracle Instant Client (Pronto Socorro) com lib_dir: {caminho_instantclient}")
        oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        print(f"{agora()} - Oracle Instant Client inicializado com sucesso (Pronto Socorro).")
        _oracle_client_initialized_ps = True
        return True
    except oracledb.DatabaseError as e:
        # DPY-0002: Oracle Client library has already been initialized.
        if "DPY-0002" in str(e) or "already initialized" in str(e).lower():
            print(f"{agora()} - Oracle Instant Client já havia sido inicializado (Pronto Socorro).")
            _oracle_client_initialized_ps = True
            return True
        else:
            print(f"{agora()} - Erro de banco de dados ao tentar inicializar Oracle Instant Client (Pronto Socorro): {e}")
            st.error(f"Erro DB ao inicializar Oracle Client (Pronto Socorro): {e}")
            return False
    except Exception as e_gen:
        print(f"{agora()} - Erro genérico ao tentar inicializar Oracle Instant Client (Pronto Socorro): {e_gen}")
        st.error(f"Erro genérico ao inicializar Oracle Client (Pronto Socorro): {e_gen}")
        return False

def conectar_banco_seguro_ps():
    """Centraliza a lógica de conexão com o banco para o Pronto Socorro, usando st.secrets."""
    if not _oracle_client_initialized_ps:
        st.error("Erro crítico: Oracle Instant Client não pôde ser inicializado (PS).")
        return None

    try:
        if "database" not in st.secrets or not all(k in st.secrets["database"] for k in ["user", "password", "dsn"]):
            st.error("As credenciais do banco de dados não estão configuradas em .streamlit/secrets.toml")
            return None

        connection = oracledb.connect(
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            dsn=st.secrets["database"]["dsn"]
        )
        return connection
    except oracledb.Error as e:
        st.error(f"Erro ao conectar ao banco de dados (PS): {e}")
        print(f"{agora()} - Erro OracleDB ao conectar (PS): {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao conectar ao banco de dados (PS): {e}")
        print(f"{agora()} - Erro inesperado ao conectar (PS): {e}")
        return None

# Chamar a inicialização no escopo global do script da página
initialize_oracle_client_if_needed()

def carregar_query(nome_arquivo):
    """Lê um arquivo .sql e retorna seu conteúdo como uma string."""
    # Constrói o caminho para o arquivo SQL no mesmo diretório do script Python
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo_sql = os.path.join(caminho_script, nome_arquivo)
    try:
        with open(caminho_arquivo_sql, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Arquivo de query não encontrado: {nome_arquivo}")
        print(f"{agora()} - Erro crítico: Arquivo de query não encontrado em {caminho_arquivo_sql}")
        return None

#@st.cache_data # Considere remover @st.cache_data se a função faz I/O de banco e precisa de dados frescos
def prescr_exames(cd_setor):
    df = pd.DataFrame() # Inicializa df como DataFrame vazio

    connection = conectar_banco_seguro_ps()
    if not connection:
        print(f"{agora()} - Conexão com o banco de dados falhou. Query não será executada (Pronto Socorro).")
        return df

    query = carregar_query('query_prescr_exames_tempo_real.sql')
    if not query:
        return df # Retorna df vazio se a query não pôde ser carregada

    try:
        with connection:
            with connection.cursor() as cursor:
                # A query é carregada do arquivo 'query_prescr_exames.sql'
                cursor.execute(query,[cd_setor])
                results = cursor.fetchall()
                
                if results:
                    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])                    
                else:
                    print(f"{agora()} - Nenhum resultado retornado pela query de prescrições (Pronto Socorro). Retornando DataFrame vazio.")
                
                print(f"{agora()} - DataFrame de prescrições preenchido com {df.shape[0]} linhas (Pronto Socorro).")

    except oracledb.Error as ora_err:
        print(f"{agora()} - Erro OracleDB em prescr_exames (Pronto Socorro):\n{ora_err}")
        st.error(f"Erro de banco de dados ao buscar exames (PS): {ora_err}")

    except Exception as erro:
        print(f"Erro Inexperado em prescr_exames (PS):\n{erro}")
        st.error(f"Ocorreu um erro inesperado ao buscar exames (PS): {erro}")
    
    return df   

#======================================================== MAIN #========================================================
# Caminho da sua imagem (ajuste conforme a sua estrutura de pastas)
logo_path = 'HSF_LOGO_-_1228x949_001.png'

def style_row_by_time(row):
    """
    Aplica estilo a uma linha do DataFrame com base na data de coleta.
    - Amarelo: Se a coleta foi realizada.
    - Vermelho: Se a coleta foi realizada há mais de 20 minutos.
    """
    # Define a cor padrão (sem estilo)
    style = [''] * len(row)
    
    # Tenta converter a data de coleta, que está como string
    coleta_time = pd.to_datetime(row['COLETA'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Se a data de coleta for inválida (NaT), não aplica estilo
    if pd.isna(coleta_time):
        return style
        
    # Regra 1: Se tem data de coleta, pinta de amarelo suave
    style = ['background-color: #FFF3CD'] * len(row) 
    
    # Regra 2: Se passaram mais de 20 minutos, pinta de vermelho suave
    if (datetime.datetime.now() - coleta_time).total_seconds() > 1200: # 20 minutos = 1200 segundos
        style = ['background-color: #F8D7DA'] * len(row) 
        
    return style

def mostrar_pagina_pronto_socorro():
    try:
        print(f'{agora()} - =============== Pronto Socorro - Tempo Real - Lógica Principal ===============\n')
        #st.logo(logo_path,size="large")
        while True:
            df = pd.DataFrame() # Inicializar como DataFrame vazio
            # Adiciona o spinner enquanto os dados são carregados
            with st.spinner('Aguarde, atualizando os dados do Pronto Socorro...'):
                if _oracle_client_initialized_ps: # Somente tenta buscar dados se o cliente inicializou
                    df_temp = prescr_exames('171') 
                    if df_temp is not None and not df_temp.empty:
                        df = df_temp.copy()
            
            # Após o spinner, verifica o resultado e exibe mensagens se necessário
            if not _oracle_client_initialized_ps:
                st.error("Oracle Client não pôde ser inicializado. Não é possível buscar dados.")
            elif df.empty: # Se o client inicializou mas a query não retornou dados
                st.warning("Não foram retornados dados de exames para o Pronto Socorro no período.")

            if not df.empty:
                print(f"{agora()} - df (amostra):\n{df.sample()}")
            else:
                print(f"{agora()} - df está vazio. Não é possível mostrar amostra.")

            print(f"{agora()} - TAMANHO DO DF: {df.shape}")

            #Substitui os espancos em branco por hifen:
            df = df = df.fillna('-')

            # Converter colunas de tempo para numérico para cálculos
            cols_tempo_para_converter = ['T_A', 'T_B', 'T_C', 'T_D', 'T_E']
            for col_t in cols_tempo_para_converter:
                if col_t in df.columns:
                    df[col_t] = pd.to_numeric(df[col_t], errors='coerce')

            #Removendo a virgula do atendimento
            if 'NR_ATENDIMENTO' in df.columns:
                df['NR_ATENDIMENTO'] = df['NR_ATENDIMENTO'].apply(lambda x: "{:.0f}".format(x) if pd.notna(x) else x)
            if 'NR_PRESCRICAO' in df.columns:
                df['NR_PRESCRICAO'] = df['NR_PRESCRICAO'].apply(lambda x: "{:.0f}".format(x) if pd.notna(x) else x)

            if not df.empty:
                print(f"{agora()} - DataFrame após conversões e renomeações (amostra):\n{df.sample()}")
            
            #transformando as colunas em string
            if not df.empty:
                for col_data in ["DT_COL", "DT_APR", "DT_DIGITA"]:
                    if col_data in df.columns:
                        df[col_data] = df[col_data].astype(str)
            df = df.rename(columns={'NM_EXAME': 'EXAME'})
            df = df.rename(columns={'NR_ATENDIMENTO': 'ATEND'})
            df = df.rename(columns={'NR_PRESCRICAO': 'PRESCRICAO'})
            df = df.rename(columns={'NM_PACIENTE': 'PACIENTE'})
            df = df.rename(columns={'STATUS_ATUAL': 'STATUS'})
            df = df.rename(columns={'APRAZO': 'PRAZO'})
            df = df.rename(columns={'DT_COL': 'COLETA'})
            df = df.rename(columns={'DT_DIGITA': 'DIGITACAO'})
            df = df.rename(columns={'DT_APR': 'APROVACAO'})

            # --- Cálculo dos Indicadores ---
            total_exames_solicitados = 0
            total_exames_atrasados = 0
            total_exames_dentro_prazo = 0
            percentual_aderencia_prazo = 0.0
            media_t_a_min, media_t_b_min, media_t_c_min, media_t_d_min, media_tat_coleta_aprovacao_min = 0, 0, 0, 0, 0
            contagem_status = pd.Series(dtype='int')

            if not df.empty:
                total_exames_solicitados = df.shape[0]
                if 'PRAZO' in df.columns:
                    total_exames_atrasados = df[df['PRAZO'] == 'Atrasado'].shape[0]
                    total_exames_dentro_prazo = df[df['PRAZO'] == 'Dentro do prazo'].shape[0]
                
                if total_exames_solicitados > 0:
                    percentual_aderencia_prazo = (total_exames_dentro_prazo / total_exames_solicitados) * 100
                
                media_t_a_min = (df['T_A'].mean() / 60) if 'T_A' in df.columns and not df['T_A'].dropna().empty else 0
                media_t_b_min = (df['T_B'].mean() / 60) if 'T_B' in df.columns and not df['T_B'].dropna().empty else 0
                media_t_c_min = (df['T_C'].mean() / 60) if 'T_C' in df.columns and not df['T_C'].dropna().empty else 0
                media_t_d_min = (df['T_D'].mean() / 60) if 'T_D' in df.columns and not df['T_D'].dropna().empty else 0
                media_tat_coleta_aprovacao_min = (df['T_E'].mean() / 60) if 'T_E' in df.columns and not df['T_E'].dropna().empty else 0
                contagem_status = df['STATUS'].value_counts() if 'STATUS' in df.columns else pd.Series(dtype='int')
            else:
                print(f"{agora()} - DataFrame 'df' está vazio. Indicadores serão definidos como 0.")



            # --- Fim do Cálculo dos Indicadores (Movido para dentro do 'if not df.empty') ---
            # Criando um estilo personalizado para o DataFrame
            st.markdown("""
            <style>
            .dataframe(display: block; width: 100% !important;)
            </style>
            """, unsafe_allow_html=True)
        
            st.write("# Monitoramento de Tempos")
            st.write("## H - Pronto Socorro")
            st.write(f'Atualizado: {datetime.datetime.now().strftime("%d/%m/%Y as %H:%M:%S")}')
            st.divider()

            # Criar o DataFrame df_filtrado_Atrasado
            df_filtrado_Atrasado = pd.DataFrame()
            if not df.empty and 'PRAZO' in df.columns:
                df_filtrado_Atrasado = df[df['PRAZO'] == 'Atrasado'].copy()

            # Define as datas ANTES de usá-las
            hoje = datetime.date.today()
            formato = "%d/%m/%Y"
            hoje_formatado = hoje.strftime(formato)

            st.write(f'## Exames Atrasado(s): {hoje_formatado}')
            
            #if not df_filtrado_Atrasado.empty:
            #    cols_data_format = ['COLETA', 'DIGITACAO', 'APROVACAO']
            #    for col_data in cols_data_format:
            #        if col_data in df_filtrado_Atrasado.columns:
            #            # Tenta converter para datetime, depois para string formatada
            #            try:
            #                df_filtrado_Atrasado[col_data] = pd.to_datetime(df_filtrado_Atrasado[col_data], errors='coerce').dt.strftime('%d/%m/%Y %H:%M:%S')
            #            except Exception: # Se falhar, preenche com '-'
            #                df_filtrado_Atrasado[col_data] = '-'
            #    
            #    if 'T_C' in df.columns and df_filtrado_Atrasado.index.isin(df.index).all(): # Garante que T_C exista no df original e os índices sejam compatíveis
            #         # Pega os valores de T_C do df original, preenche NaN com '-' e depois converte para string
            #        df_filtrado_Atrasado['COLETA - DIGITACAO'] = df.loc[df_filtrado_Atrasado.index, 'T_C'].fillna('-').astype(str)
            #    elif 'T_C' in df_filtrado_Atrasado.columns: # Se T_C já existe em df_filtrado_Atrasado (menos provável se vem de df)
            #        df_filtrado_Atrasado['COLETA - DIGITACAO'] = df_filtrado_Atrasado['T_C'].fillna('-').astype(str)
            #    else:
            #        df_filtrado_Atrasado['COLETA - DIGITACAO'] = '-'
                
            df_filtrado_Atrasado = df_filtrado_Atrasado.fillna('-')
            
            colunas_df_atrasado = ['EXAME','PRESCRICAO','PACIENTE' , 'STATUS' , 'PRAZO','COLETA','DIGITACAO','APROVACAO', 'COLETA - DIGITACAO']
            # Garante que todas as colunas existam em df_filtrado_Atrasado antes de tentar exibi-las
            colunas_existentes_atrasado = [col for col in colunas_df_atrasado if col in df_filtrado_Atrasado.columns]

            if not df_filtrado_Atrasado.empty:
                # Filtra o DataFrame para mostrar apenas exames sem data de aprovação.
                #DESATIA APENAS EM CARATER DE TESTES                
                df_filtrado_Atrasado = df_filtrado_Atrasado[df_filtrado_Atrasado['APROVACAO'] == '-']
                
                # Aplica o estilo condicional e exibe o DataFrame
                st.dataframe(
                    df_filtrado_Atrasado[colunas_existentes_atrasado].style.apply(style_row_by_time, axis=1),
                    hide_index=True, 
                    use_container_width=True)
            else:
                st.caption("Nenhum exame atrasado para exibir.")
            
            
            #Total de Atrasado:
            st.write(f"### Total: {df_filtrado_Atrasado.shape[0]}")
            st.divider()
            
                        
            print(f'{agora()} - Pausando por 2 minutos (120 segundos)!')
            time.sleep(120)  # Pausa por 2 minutos
            print(f'\n{agora()} - st.experimental_rerun()\n')
            st.rerun()
        
    except Exception as err:
        print(f"Inexperado {err=}, {type(err)=}")
        st.error(f"Ocorreu um erro inesperado na página Pronto Socorro: {err}")

# Chamar a função principal da página
mostrar_pagina_pronto_socorro()