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

    query = carregar_query('query_prescr_exames.sql')
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

def mostrar_pagina_pronto_socorro():
    try:
        print(f'{agora()} - =============== Pronto Socorro - Lógica Principal ===============\n')
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
            st.write('___________________')

            # --- Exibição dos Indicadores Chave de Desempenho ---
            st.write("## Indicadores Chave de Desempenho")
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            with col_kpi1:
                st.metric(label="📊 Total Exames Solicitados", value=total_exames_solicitados)
            with col_kpi2:
                st.metric(label="⏰ Total Exames Atrasados", value=total_exames_atrasados, delta_color="inverse")
            with col_kpi3:
                st.metric(label="🎯 % Aderência ao Prazo", value=f"{percentual_aderencia_prazo:.2f}%")
            with col_kpi4:
                st.metric(label="⏱️ TAT Médio (Coleta-Aprovação)", value=f"{media_tat_coleta_aprovacao_min:.0f} min")
            st.write('___________________')

            ## --- Exibição dos Tempos Médios por Etapa ---
            #st.write("## Tempos Médios por Etapa (minutos)")
            #col_tm1, col_tm2, col_tm3, col_tm4 = st.columns(4)
            #with col_tm1:
            #    st.metric(label="➡️ Liberação → Coleta", value=f"{media_t_a_min:.0f}")
            #with col_tm2:
            #    st.metric(label="🧪 Coleta → Triagem", value=f"{media_t_b_min:.0f}")
            #with col_tm3:
            #    st.metric(label="💻 Triagem → Digitação", value=f"{media_t_c_min:.0f}")
            #with col_tm4:
            #    st.metric(label="✅ Digitação → Aprovação", value=f"{media_t_d_min:.0f}")
            #st.write('___________________')

            # --- Exibição da Distribuição de Exames por Status ---
            st.write("## Distribuição de Exames por Status")
            # Definindo o número de colunas com base no número de status únicos, limitado a 5 para não poluir.
            status_unicos = contagem_status.index.tolist()
            num_cols_status = min(len(status_unicos), 5)
            if num_cols_status > 0:
                cols_status = st.columns(num_cols_status)
                for i, status_nome in enumerate(status_unicos[:num_cols_status]):
                    with cols_status[i]:
                        # Adicionando ícones com base no nome do status (exemplo)
                        icone_status = "🔄" # Padrão
                        if "Pendente" in status_nome:
                            icone_status = "⏳"
                        elif "Coletado" in status_nome:
                            icone_status = "🩸"
                        elif "Aprovação" in status_nome or "Aprovado" in status_nome :
                            icone_status = "👍"
                        elif "Entrega" in status_nome:
                            icone_status = "🚚"
                        st.metric(label=f"{icone_status} {status_nome}", value=contagem_status[status_nome])
            else:
                st.caption("Nenhum dado de status para exibir.")
            st.write('___________________')


            st.write('\n\n\n')
            
            #Data Frames customizados:
            df_filtrado_Atrasado = pd.DataFrame()
            if not df.empty and 'PRAZO' in df.columns:
                df_filtrado_Atrasado = df[df['PRAZO'] == 'Atrasado'].copy()
            
            # Os dataframes abaixo não parecem ser usados posteriormente, mas se forem, aplicar lógica similar:
            # df_filtrado_Dentro = pd.DataFrame()
            # if not df.empty and 'PRAZO' in df.columns:
            #     df_filtrado_Dentro = df[df['PRAZO'] == 'Dentro do prazo'].copy()
            
            # df_filtrado_tria_area = pd.DataFrame()
            # if not df.empty and 'STATUS' in df.columns:
            #     df_filtrado_tria_area = df[df['STATUS'] == 'Triagem / Área Técnica'].copy()  
            # df_filtrado_Dig_Result = df[df['STATUS'] == 'Digitação do Resultado'].copy()  
            # df_filtrado_Pend_Colet = df[df['STATUS'] == 'Pendente de Coleta'].copy()  
            # df_filtrado_Aprov_Result = df[df['STATUS'] == 'Aprovação do Resultado'].copy()  
            # df_filtrado_Mat_Colet = df[df['STATUS'] == 'Material Coletado'].copy()  
            
            #Exibindo data frame Atrasado:
            st.write('## Atrasado(s):')
            hoje = datetime.date.today()
            ontem = hoje - datetime.timedelta(days=2)
            formato = "%d/%m/%Y"
            hoje_formatado = datetime.datetime.combine(hoje, datetime.time.min).strftime(formato)  
            ontem_formatado = datetime.datetime.combine(ontem, datetime.time.min).strftime(formato) 
            
            #Exibe as datas formatadas
            st.write(f"**De:** {ontem_formatado} **até:** {hoje_formatado}")
            
            
            #CALCULO DE MINUTOS DE DIFERENCA DA COLETA ATE A DIGITACAO
            if not df_filtrado_Atrasado.empty:
                cols_data_format = ['COLETA', 'DIGITACAO', 'APROVACAO']
                for col_data in cols_data_format:
                    if col_data in df_filtrado_Atrasado.columns:
                        # Tenta converter para datetime, depois para string formatada
                        try:
                            df_filtrado_Atrasado[col_data] = pd.to_datetime(df_filtrado_Atrasado[col_data], errors='coerce').dt.strftime('%d/%m/%Y %H:%M:%S')
                        except Exception: # Se falhar, preenche com '-'
                            df_filtrado_Atrasado[col_data] = '-'
                
                if 'T_C' in df.columns and df_filtrado_Atrasado.index.isin(df.index).all(): # Garante que T_C exista no df original e os índices sejam compatíveis
                     # Pega os valores de T_C do df original, preenche NaN com '-' e depois converte para string
                    df_filtrado_Atrasado['COLETA - DIGITACAO'] = df.loc[df_filtrado_Atrasado.index, 'T_C'].fillna('-').astype(str)
                elif 'T_C' in df_filtrado_Atrasado.columns: # Se T_C já existe em df_filtrado_Atrasado (menos provável se vem de df)
                    df_filtrado_Atrasado['COLETA - DIGITACAO'] = df_filtrado_Atrasado['T_C'].fillna('-').astype(str)
                else:
                    df_filtrado_Atrasado['COLETA - DIGITACAO'] = '-'
                
                df_filtrado_Atrasado = df_filtrado_Atrasado.fillna('-')
            
            colunas_df_atrasado = ['EXAME','PRESCRICAO','PACIENTE' , 'STATUS' , 'PRAZO','COLETA','DIGITACAO','APROVACAO', 'COLETA - DIGITACAO']
            # Garante que todas as colunas existam em df_filtrado_Atrasado antes de tentar exibi-las
            colunas_existentes_atrasado = [col for col in colunas_df_atrasado if col in df_filtrado_Atrasado.columns]

            if not df_filtrado_Atrasado.empty:
                #TODO: ordenar dataframe de forma decrescente pela coluna 'COLETA'
                # Para ordenar corretamente, converte a coluna 'COLETA' para datetime,
                # tratando erros para que valores inválidos não quebrem a ordenação.
                df_filtrado_Atrasado['COLETA_DT_SORT'] = pd.to_datetime(df_filtrado_Atrasado['COLETA'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                
                # Ordena o DataFrame pela coluna de data, com as mais recentes primeiro.
                # NaT (datas inválidas) serão colocadas no final.
                df_filtrado_Atrasado = df_filtrado_Atrasado.sort_values(by='COLETA_DT_SORT', ascending=False).drop(columns=['COLETA_DT_SORT'])

                # Exibe o DataFrame já ordenado. O .fillna() é removido pois já foi aplicado antes.
                st.dataframe(df_filtrado_Atrasado[colunas_existentes_atrasado], hide_index=True, use_container_width=True)
            else:
                st.caption("Nenhum exame atrasado para exibir.")
            
            
            #Total de Atrasado:
            st.write(f"### Total: {df_filtrado_Atrasado.shape[0]}")
            st.write('___________________')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            st.write('\n\n\n')
            
            ###############################################################################################################################
            #Exibindo data frame Analitico:
            st.write('## Analitico:')
            # Exibe as datas formatadas
            st.write(f"**De:** {ontem_formatado} **até:** {hoje_formatado}")
            # Criar um estado para armazenar a opção de filtro
            if 'filtro_exame' not in st.session_state:
                st.session_state.filtro_exame = 'Todos'
            
            df_analitico = df.copy() # Trabalhar com uma cópia para os filtros
            if not df_analitico.empty:
                cols_to_format_analitico = ['COLETA', 'DIGITACAO', 'APROVACAO']
                for col_data_an in cols_to_format_analitico:
                    if col_data_an in df_analitico.columns:
                        try:
                            df_analitico[col_data_an] = pd.to_datetime(df_analitico[col_data_an], errors='coerce').dt.strftime('%d/%m/%Y %H:%M:%S')
                        except Exception:
                             df_analitico[col_data_an] = '-'
               
                if 'T_C' in df_analitico.columns:
                    # Preenche NaN (float) com '-' (string) ANTES de converter para string
                    df_analitico['COLETA - DIGITACAO'] = df_analitico['T_C'].fillna('-').astype(str)
                else:
                    df_analitico['COLETA - DIGITACAO'] = '-'
                df_analitico = df_analitico.fillna('-')
            else: # Se df_analitico (originalmente df) estiver vazio, crie um df vazio com as colunas esperadas
                colunas_esperadas_analitico = ['EXAME','PRESCRICAO','PACIENTE' , 'STATUS' , 'PRAZO','COLETA','DIGITACAO','APROVACAO', 'COLETA - DIGITACAO']
                df_analitico = pd.DataFrame(columns=colunas_esperadas_analitico)

            print(f"\n{agora()} - *****Analitico - df['COLETA']")
            
            # Criar as colunas
            col0,col1,col2,col3,col4,col5,col6,col7,col8 = st.columns(9)
            col10,col11,col12,col13,col14,col15,col16,col17,col18 = st.columns(9)

            # Adiciona os botões em cada coluna
            with col0:
                button_amilase = st.button('Amilase',use_container_width=True)
            with col1:
                button_bilirrubina = st.button('Bilirrubina',use_container_width=True)
            with col2:
                button_calcio = st.button('Cálcio',use_container_width=True)
            with col3:
                button_coagulograma = st.button('Coagulograma',use_container_width=True)
            with col4:
                button_creatinina = st.button('Creatinina',use_container_width=True)
            with col5:
                button_fosfatase_alcalina = st.button('Fosfatase',use_container_width=True)
            with col6:
                button_GGT = st.button('GGT',use_container_width=True)
            with col7:
                button_glicose = st.button('Glicose',use_container_width=True)
            with col8:
                button_hemograma = st.button('Hemograma',use_container_width=True)
            
                
            #separacao das linhas
            
            with col10:
                button_HIV = st.button('HIV 1 E 2',use_container_width=True)
            with col11:
                button_lipase = st.button('Lipase',use_container_width=True)
            #Potássio ( K )
            with col12:
                button_potassio = st.button('Potássio ( K )',use_container_width=True) 
            with col13:
                button_sodio = st.button('Sódio',use_container_width=True) 
            with col14:
                button_TAP = st.button('TAP',use_container_width=True) 
            with col15:
                button_TGO = st.button('TGO',use_container_width=True) 
            with col16:
                button_TGP = st.button('TGP',use_container_width=True)   
            with col17:
                button_ureia = st.button('Uréia',use_container_width=True)
            #Button COMPLETO ficara na ponta para chamar a atencao:
            with col18:
                button_completo = st.button('COMPLETO',use_container_width=True)
                
                
            df_filtrado_para_exibicao = df_analitico # Por padrão, exibe o df_analitico (que pode estar vazio ou preenchido)

            #acoes dos botoes:
            if not df_analitico.empty and 'EXAME' in df_analitico.columns:
                if button_amilase:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Amilase ']
                elif button_bilirrubina:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Bilirrubina Total e Frações']
                elif button_calcio:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Cálcio ']
                elif button_coagulograma:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Coagulograma']
                elif button_creatinina:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Creatinina']
                elif button_fosfatase_alcalina:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Fosfatase Alcalina']
                elif button_GGT:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Gama Glutamil Transferase (GGT)']
                elif button_glicose:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Glicose']
                elif button_hemograma:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Hemograma']
                elif button_HIV:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'HIV 1 E 2 - Pesquisa de Antígeno e Anticorpos']
                elif button_lipase:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Lipase']
                elif button_potassio:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Potássio ( K )']
                elif button_sodio:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Sódio']   
                elif button_TAP:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'TAP - Tempo de Protrombina ']   
                elif button_TGO:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Transaminase Oxalacetica - TGO - AST']   
                elif button_TGP:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Transaminase Piruvica  - TGP - ALT']   
                elif button_ureia:
                    df_filtrado_para_exibicao = df_analitico[df_analitico['EXAME'] == 'Uréia']
                # Se button_completo ou nenhum botão de filtro for pressionado, df_filtrado_para_exibicao já é df_analitico
            
            colunas_df_analitico = ['EXAME','PRESCRICAO','PACIENTE' , 'STATUS' , 'PRAZO','COLETA','DIGITACAO','APROVACAO', 'COLETA - DIGITACAO']
            # Garante que todas as colunas existam em df_filtrado_para_exibicao antes de tentar exibi-las
            colunas_existentes_analitico = [col for col in colunas_df_analitico if col in df_filtrado_para_exibicao.columns]

            #EXIBINDO O DATA FRAME:
            if not df_filtrado_para_exibicao.empty:
                st.dataframe(df_filtrado_para_exibicao[colunas_existentes_analitico], hide_index=True,height=700, use_container_width=True)
            else: # Se após o filtro o df estiver vazio, exibe uma mensagem ou um df vazio estruturado
                st.dataframe(pd.DataFrame(columns=colunas_df_analitico), hide_index=True,height=700, use_container_width=True)
                st.caption("Nenhum dado analítico para exibir com os filtros aplicados.")


            ###############################################################################################################################
            
            #Total de Pacientes:
            st.write(f"### Total: {df[['EXAME']].shape[0]}")
            st.write('___________________')
            # st.write('\n\n\n') # Reduzir múltiplos newlines
                        
            with st.sidebar:
                st.write('# Indicadores gerais:')
                st.write('___________________')
                # Exibe as datas formatadas
                st.write(f"**De: {ontem_formatado} até: {hoje_formatado}**", unsafe_allow_html=True)
                #Exibir de forma dinamica apos o lick nos filtros de nome do exame
                # Usar df_filtrado_para_exibicao para os totais da sidebar se os filtros devem afetá-los
                # Ou usar 'df' (o DataFrame antes dos filtros de botão) se os totais da sidebar devem ser globais para o período.
                # Assumindo que os totais da sidebar devem refletir o df antes dos filtros de botão:
                sidebar_df_atrasados = 0
                sidebar_df_dentro_prazo = 0
                if not df.empty and 'PRAZO' in df.columns:
                    sidebar_df_atrasados = df[df['PRAZO'] == 'Atrasado'].shape[0]
                    sidebar_df_dentro_prazo = df[df['PRAZO'] == 'Dentro do prazo'].shape[0]

                st.write(f'Atrasado(s): {sidebar_df_atrasados}') 
                st.write(f'Dentro do prazo: {sidebar_df_dentro_prazo}')
                st.write(f'## Total (período): {df.shape[0]}')
                        
            print(f'{agora()} - Pausar por 350 segundos!')
            time.sleep(350)  # Pausar por 350 segundos            
            print(f'\n{agora()} - st.experimental_rerun()\n')
            st.rerun()
        
    except Exception as err:
        print(f"Inexperado {err=}, {type(err)=}")
        st.error(f"Ocorreu um erro inesperado na página Pronto Socorro: {err}")

# Chamar a função principal da página
mostrar_pagina_pronto_socorro()