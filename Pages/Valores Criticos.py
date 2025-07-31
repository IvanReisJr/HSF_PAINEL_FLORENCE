#16/12/2024
#@PLima
#HSF - PAINEL LABORATORIO - VALORES CRITICOS
import streamlit as st
import pandas as pd
import os
import oracledb
import time
import datetime
import re

#streamlit run "c:\Pietro\Projetos\HSF_PAINEL_LAB_VAL_CRIT\Valores Criticos.py" --server.port 8003


#Configurando pagina para exibicao em modo WIDE:
st.set_page_config(layout="wide",initial_sidebar_state="expanded",page_title="Valores Críticos")

# Caminho da sua imagem (ajuste conforme a sua estrutura de pastas)
# O script está em 'pages', o logo está um nível acima.
logo_path = '../HSF_LOGO_-_1228x949_001.png'

def agora():
    agora = datetime.datetime.now()
    agora = agora.strftime("%Y-%m-%d %H-%M-%S")
    return str(agora)

#apontamento para usar o Thin Mod
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
    #print(f"A pasta '{nome_pasta}' nao foi encontrada na raiz do aplicativo.")
    return None

def conectar_banco_seguro():
    """Centraliza a lógica de conexão com o banco, usando st.secrets."""
    caminho_instantclient = encontrar_diretorio_instantclient()
    if not caminho_instantclient:
        st.error("Erro crítico: Oracle Instant Client não encontrado.")
        return None

    try:
        oracledb.init_oracle_client(lib_dir=caminho_instantclient)
    except Exception as e_init:
        if "already been initialized" not in str(e_init):
             print(f"Erro ao inicializar o Oracle Instant Client: {e_init}")
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

def valores_criticos_exames(data_inicial_selecionada, data_final_selecionada):
    print(f'{agora()} - valores_criticos_exames() - INÍCIO')
    df = pd.DataFrame() # Inicializa df como DataFrame vazio
    data_inicial_str = data_inicial_selecionada.strftime('%Y-%m-%d')
    data_final_str = data_final_selecionada.strftime('%Y-%m-%d')
    try:
        connection = conectar_banco_seguro()
        if not connection:
            return pd.DataFrame() # Retorna DF vazio se a conexão falhar
        
        with connection:
            with connection.cursor() as cursor:
                print(f'with connection.cursor() as cursor:')
                #####################################################################################
                # Ler a query do arquivo query.sql
                query_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query.sql")
                try:
                    with open(query_file_path, 'r', encoding='utf-8') as f:
                        query = f.read()
                except FileNotFoundError:
                    print(f"Erro: O arquivo query.sql não foi encontrado em {query_file_path}")
                    return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro
                except Exception as e:
                    print(f"Erro ao ler o arquivo query.sql: {e}")
                    return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

                #####################################################################################
                
                params = {'data_inicial': data_inicial_str, 'data_final': data_final_str}
                print(f"Executando query com parâmetros: {params}")
                cursor.execute(query, params)

                results = cursor.fetchall()
                df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
    
    except Exception as erro:
        print(f"Erro Inexperado:\n{erro}")
    
    print(f'{agora()} - valores_criticos_exames() - FIM')
    return df

def calculo_valores_criticos_exames(df_criticos):
    print(f'{agora()} - calculo_valores_criticos_exames() - INÍCIO')

    # Certifique-se de que o DataFrame não está vazio
    if df_criticos.empty:
        print(f'{agora()} - DataFrame de exames críticos está vazio. Nenhum cálculo será realizado.')
        print(f'{agora()} - calculo_valores_criticos_exames() - FIM')
        return { # Retorna um dicionário com valores padrão ou zero para evitar erros
            "total_exames_criticos": 0,
            "tipos_exames_distintos_criticos": 0,
            "resultados_criticos_por_exame": pd.Series(dtype='int64'), # Série vazia
            "total_prescricoes_unicas_criticas": 0,
            "exames_com_coleta": 0,
            "exames_com_digitacao": 0,
            "exames_com_aprovacao": 0,
            "exames_com_impressao": 0,
            "pacientes_unicos_afetados": 0,
            "pacientes_mais_exames": pd.Series(dtype='int64'),
            "prescricoes_mais_exames": pd.Series(dtype='int64') # Novo
        }

    #print(f'{agora()} - df_criticos (primeiras 5 linhas):\n{df_criticos.head(5)}')
    print(f'{agora()} - df_criticos.shape: {df_criticos.shape}')
    try: # Linha 112 conforme o traceback
        # 1) numero total de exames criticos;
        # Como o df_criticos já contém apenas exames críticos, o total é o número de linhas.
        total_exames_criticos = len(df_criticos)
        #print(f"1) Número total de exames críticos: {total_exames_criticos}")
 
        # 2) numero total de tipos de exame distintos com resultados críticos;
        tipos_exames_distintos_criticos = df_criticos['NM_EXAME'].nunique()
        #print(f"2) Número total de tipos de exame distintos com resultados críticos: {tipos_exames_distintos_criticos}")
 
        # 3) numero de resultados criticos de cada exame distinto;
        resultados_criticos_por_exame = df_criticos['NM_EXAME'].value_counts()
        #print(f"3) Número de resultados críticos por tipo de exame:\n{resultados_criticos_por_exame}")
 
        # 4) numero total de prescricoes únicas com exames críticos;
        total_prescricoes_unicas_criticas = df_criticos['NR_PRESCRICAO'].nunique()
        #print(f"4) Número total de prescrições únicas com exames críticos: {total_prescricoes_unicas_criticas}")
 
        # 5-8) Contagem de exames com datas específicas (considerando que '-' significa ausência de data)
        exames_com_coleta = df_criticos[df_criticos['DT_COLETA'] != '-'].shape[0]
        exames_com_digitacao = df_criticos[df_criticos['DT_DIGITACAO'] != '-'].shape[0]
        exames_com_aprovacao = df_criticos[df_criticos['DT_APROVACAO'] != '-'].shape[0]
        exames_com_impressao = df_criticos[df_criticos['DT_IMPRESSAO'] != '-'].shape[0]
        #print(f"5) Número total de exames críticos com data de coleta: {exames_com_coleta}")
        #print(f"6) Número total de exames críticos com data de digitação: {exames_com_digitacao}")
        #print(f"7) Número total de exames críticos com data de aprovação: {exames_com_aprovacao}")
        #print(f"8) Número total de exames críticos com data de impressão: {exames_com_impressao}")

        # Adicional: Número de pacientes únicos afetados (assumindo que a coluna PACIENTE existe após o rename)
        # Se o rename ainda não ocorreu quando esta função é chamada, use 'NM_PACIENTE'
        # Para este exemplo, vamos assumir que o DataFrame já tem a coluna 'PACIENTE' ou 'NM_PACIENTE'
        # Se 'PACIENTE' não estiver disponível aqui, você precisará ajustar ou passar o df após o rename.
        # Por simplicidade, vamos usar 'NM_PACIENTE' que vem da query.
        pacientes_unicos_afetados = df_criticos['NM_PACIENTE'].nunique()
        #print(f"9) Número de pacientes únicos afetados: {pacientes_unicos_afetados}")

        # Novo cálculo: Pacientes com mais exames críticos
        pacientes_mais_exames = df_criticos['NM_PACIENTE'].value_counts()
        #print(f"10) Pacientes com mais exames críticos:\n{pacientes_mais_exames.head()}")

        # Novo cálculo: Prescrições com mais exames críticos
        prescricoes_mais_exames = df_criticos['NR_PRESCRICAO'].value_counts()
        #print(f"11) Prescrições com mais exames críticos:\n{prescricoes_mais_exames.head()}")
 
        # Você pode retornar esses valores se precisar usá-los fora da função
        return {
            "total_exames_criticos": total_exames_criticos,
            "tipos_exames_distintos_criticos": tipos_exames_distintos_criticos,
            "resultados_criticos_por_exame": resultados_criticos_por_exame, # Isso é uma Series
            "total_prescricoes_unicas_criticas": total_prescricoes_unicas_criticas,
            "pacientes_unicos_afetados": pacientes_unicos_afetados,
            "pacientes_mais_exames": pacientes_mais_exames, # Adicionado
            "prescricoes_mais_exames": prescricoes_mais_exames # Adicionado
        }
 
    except Exception as erro: # Linha 125 conforme o traceback
        print(f"Erro Inexperado:\n{erro}")
    print(f'{agora()} - calculo_valores_criticos_exames() - FIM')

def buscar_dados_hemogramas(data_inicial_selecionada, data_final_selecionada):
    print(f'{agora()} - buscar_dados_hemogramas() - INÍCIO')
    df_hemogramas = pd.DataFrame()
    data_inicial_str = data_inicial_selecionada.strftime('%Y-%m-%d')
    data_final_str = data_final_selecionada.strftime('%Y-%m-%d')
    try:
        connection = conectar_banco_seguro()
        if not connection:
            return pd.DataFrame()
        
        with connection:
            with connection.cursor() as cursor:
                query_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query_hemogramas.sql")
                try:
                    with open(query_file_path, 'r', encoding='utf-8') as f:
                        query_h = f.read()
                except FileNotFoundError:
                    print(f"Erro: O arquivo query_hemogramas.sql não foi encontrado em {query_file_path}")
                    return df_hemogramas
                except Exception as e:
                    print(f"Erro ao ler o arquivo query_hemogramas.sql: {e}")
                    return df_hemogramas

                params_h = {'data_inicial': data_inicial_str, 'data_final': data_final_str}
                print(f"Executando query de hemogramas com parâmetros: {params_h}")
                cursor.execute(query_h, params_h)
                results_h = cursor.fetchall()
                
                if results_h:
                    df_hemogramas = pd.DataFrame(results_h, columns=[desc[0] for desc in cursor.description])
                    print(f'df_hemogramas: {df_hemogramas.shape[0]} linhas')
                else:
                    print("Nenhum dado de hemograma encontrado para o período.")
    
    except oracledb.Error as erro_db:
        print(f"Erro OracleDB em buscar_dados_hemogramas: {erro_db}")
    except Exception as erro_geral:
        print(f"Erro Inesperado em buscar_dados_hemogramas: {erro_geral}")
    
    print(f'{agora()} - buscar_dados_hemogramas() - FIM. {len(df_hemogramas)} linhas retornadas.')
    return df_hemogramas


def limpar_rtf_para_texto(rtf_text):
    """
    Limpa uma string RTF, removendo tags comuns e convertendo entidades
    para um texto mais próximo do plano.
    """
    if not rtf_text:
        return ""

    text = str(rtf_text) # Garantir que é uma string

    # 1. Remover blocos de controle RTF e tags comuns
    # Regex mais robusta para remover control words RTF (ex: \b, \par, \fs22)
    text = re.sub(r'\\[a-zA-Z0-9*]+(-?\d+)? ?', '', text)
    # Remover grupos RTF complexos, incluindo aqueles com informações de fonte, cor, etc.
    # Esta regex tenta ser mais abrangente.
    text = re.sub(r'\{\*?\\[^{}]+;\}|\{\*?(\\[a-zA-Z0-9]+)+\s*\}', '', text)
    # Remover chaves restantes que podem não ter sido pegas
    text = re.sub(r'[{}]', '', text)

    # 2. Converter entidades de caracteres RTF comuns
    # Valores de referência adicionados ao replacements
    replacements = {
        "\'e1": "á", "\'E1": "Á",
        "\'e9": "é", "\'E9": "É",
        "\'ed": "í", "\'ED": "Í",
        "\'f3": "ó", "\'F3": "Ó",
        "\'fa": "ú", "\'FA": "Ú",
        "\'e7": "ç", "\'C7": "Ç",
        "\'e3": "ã", "\'E3": "Ã",
        "\'f5": "õ", "\'F5": "Õ",
        "\'fc": "ü", "\'FC": "Ü",
        r"\~": "~", # Usando raw string para evitar warning
        r"\^": "^", # Usando raw string para evitar warning
        # "." : "",  # Comente ou remova esta linha
        ";" : "", 
        "default" : "",
        "Valores de Refer" : "", # "Valores de Referência"
        "eancia" : "",           # (continuação de "Referência")
        "\'": "",               # Remover apóstrofos RTF soltos
        # "Homens" : "", # Decida se quer remover "Homens" e "Mulheres"
        # "Mulheres" : "",
        "Courier" : "", 
        "NewMicrosoft" : "", 
        "Sans" : "", 
        "Serif" : "",
        # Adicionando os valores de referência para serem removidos ou normalizados se necessário
        # A ideia aqui é remover essas strings se elas atrapalham a extração dos valores numéricos.
        # Se você precisa deles para algo, ajuste.
        "4,4 a 5,9": "", "3,8 a 5,2": "", "Milhões/mmb3": "Milhões/mmb3", # Manter unidade
        "13,0 a 18,0": "", "12,0 a 16,0": "", "g/dL": "g/dL",             # Manter unidade
        "40,0 a 53,0": "", "35,0 a 47,0": "", "%": "%",                   # Manter unidade
        "80,0 a 100,0": "", "fl": "fl",                                   # Manter unidade
        "26,0 a 34": "", "pg": "pg",                                     # Manter unidade
        "32,0 a 36,0": "", # g/dL já coberto
        "11,5 a 16,0": "", # % já coberto
    }
    for rtf_code, char_code in replacements.items():
        text = text.replace(rtf_code, char_code)

    # 3. Remover múltiplos espaços e linhas em branco
    text = re.sub(r' +', ' ', text) 
    text = re.sub(r'(\r\n|\r|\n){2,}', '\n', text).strip() 

    return text

def processar_hemogramas_criticos(df_hemogramas_bruto):
    print(f'{agora()} - processar_hemogramas_criticos() - INÍCIO')
    
    if df_hemogramas_bruto is None or df_hemogramas_bruto.empty:
        print("DataFrame de hemogramas brutos está vazio.")
        return pd.DataFrame()

    hemogramas_criticos_lista = []
    
    # Padrões de extração (adaptados do seu main.py)
    # Ajuste DS_RESULTADO_RTF para o nome da coluna correta retornada pela query_hemogramas.sql
    # Se sua query já retorna como DS_RESULTADO_RTF, está ok.
    coluna_rtf = 'DS_RESULTADO_RTF' 
    if coluna_rtf not in df_hemogramas_bruto.columns:
        print(f"ERRO: Coluna '{coluna_rtf}' esperada não foi encontrada no DataFrame de hemogramas. Verifique a 'query_hemogramas.sql'.")
        return pd.DataFrame() # Retorna DataFrame vazio se a coluna essencial não existir


    for index, linha in df_hemogramas_bruto.iterrows():
        nr_prescricao = linha.get('NR_PRESCRICAO', 'N/A')
        nm_paciente = linha.get('NM_PACIENTE', 'N/A') # Opcional
        ds_resultado_valor_rtf = linha[coluna_rtf]

        # DEBUG: Adicione um if para focar no RTF problemático se souber a prescrição
        # Exemplo: 
        # if "HEMOGRAMA" in ds_resultado_valor_rtf.upper(): # Comentado para reduzir o log inicial
            # print(f"\nDEBUG: Processando Prescrição {nr_prescricao}, Paciente: {nm_paciente}, Index DataFrame: {index}")
            # print(f"DEBUG: RTF Original:\n{ds_resultado_valor_rtf[:500]}...") # Primeiros 500 chars


        if pd.isna(ds_resultado_valor_rtf) or not ds_resultado_valor_rtf:
            continue
        
        texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)
        
        # DEBUG: Ver o texto após a limpeza APENAS para o RTF que contém HEMOGRAMA
        is_hemograma_rtf = "HEMOGRAMA" in texto_limpo.upper() # Verifica uma vez
        #if is_hemograma_rtf:
            #print(f"\n--- DEBUG Prescrição: {nr_prescricao} (HEMOGRAMA) ---")
            #print(f"Texto Limpo:\n{texto_limpo}\n--------------------")
        
        padroes_extracao = {
            "Hemácias": r"Hemácias[\s\.]*:\s*([0-9,.]+)\s*Milhões/mmb3",
            "Hemoglobina": r"Hemoglobina[\s\.]*:\s*([0-9,.]+)\s*g/dL",
            "Hematócrito": r"Hematócrito[\s\.]*:\s*([0-9,.]+)\s*%",
            "VCM": r"VCM[\s\.]*:\s*([0-9,.]+)\s*fl",
            "HCM": r"HCM[\s\.]*:\s*([0-9,.]+)\s*pg",
            "CHCM": r"CHCM[\s\.]*:\s*([0-9,.]+)\s*g/dL",
            "RDW": r"RDW[\s\.]*:\s*([0-9,.]+)\s*%",
            "Eritroblastos": r"Eritroblastos[\s\.]*:\s*([0-9,.]+)", # Ajustar se tiver unidade
            "Leucócitos": r"Leucócitos Totais[\s\.]*:\s*([0-9,.]+)\s*(?:mmb3|/µL|mm3)", # Aceita mmb3, /µL ou mm3
            "Plaquetas": r"PLAQUETAS[\s\.]*:\s*([0-9,.]+)\s*mil/mmb3"
        }
        dados_extraidos = {"NR_PRESCRICAO": nr_prescricao, "NM_PACIENTE": nm_paciente}

        for nome_campo, padrao in padroes_extracao.items():
            match = re.search(padrao, texto_limpo, re.IGNORECASE)
            if match:
                dados_extraidos[nome_campo] = match.group(1).strip().replace(",", ".")
                # DEBUG: Para Hemoglobina especificamente
                # if nome_campo == "Hemoglobina" and is_hemograma_rtf: # Comentado para reduzir log
                    #print(f"DEBUG: Hemoglobina - Match encontrado! Grupo 1: '{match.group(1)}', Convertido: '{dados_extraidos[nome_campo]}'")
            else:
                dados_extraidos[nome_campo] = None 
                # DEBUG: Para Hemoglobina especificamente
                # if nome_campo == "Hemoglobina" and is_hemograma_rtf: # Comentado para reduzir log
                    #print(f"DEBUG: Hemoglobina - Nenhum match encontrado com o padrão: {padrao}")

        # DEBUG: Mostrar o dicionário dados_extraidos completo para RTFs de HEMOGRAMA
        #if is_hemograma_rtf:
            #print(f"Dados Extraídos para Prescrição {nr_prescricao}:\n{dados_extraidos}\n--------------------")

        # Verificar criticidade
        # Hemoglobina (< 6.6 ou > 19.9 g/dL)
        if dados_extraidos.get("Hemoglobina"):
            try:
                val = float(dados_extraidos["Hemoglobina"])
                #if is_hemograma_rtf: # Log apenFheas para hemogramas
                    #print(f"DEBUG: Hemoglobina - Valor float: {val}")
                if val < 6.6 or val > 19.9: # Lógica de criticidade
                    hemogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao, "Paciente": nm_paciente,
                        "Parâmetro": "Hemoglobina", "Valor": val, "Unidade": "g/dL",
                        "Critério": "< 6.6 ou > 19.9"
                    })
            except (ValueError, TypeError): pass

        # Hematócrito (< 18.0 ou > 60.0 %)
        if dados_extraidos.get("Hematócrito"):
            try:
                val = float(dados_extraidos["Hematócrito"])
                if val < 18.0 or val > 60.0:
                    hemogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao, "Paciente": nm_paciente,
                        "Parâmetro": "Hematócrito", "Valor": val, "Unidade": "%",
                        "Critério": "< 18.0 ou > 60.0"
                    })
            except (ValueError, TypeError): pass
        
        # Leucócitos (< 2.000/µL ou > 50.000/µL)
        # A regex captura o valor que já deve estar em /µL (ou mmb3, que é equivalente)
        # Se o valor for, por exemplo, "1.5" e isso significar 1500, a conversão já está ok.
        # Se for "15.52" e isso significar 15520, também ok.
        if dados_extraidos.get("Leucócitos"):
            try:
                val_str = dados_extraidos["Leucócitos"]
                # Se o valor já inclui ponto como separador de milhar (ex: "2.500" ou "50.000")
                # precisamos remover o ponto antes de converter para float.
                # A regex atual `([0-9,.]+)` pode capturar "50.000" como string.
                # Se o sistema usa "." como separador de milhar e "," como decimal,
                # ou vice-versa, a limpeza `replace(",", ".")` já ajuda.
                # Se o valor for "50.000" (cinquenta mil), o float("50.000") dará erro.
                # Vamos assumir que a regex e o replace já trataram isso para "50000" ou "50.0"
                # Se a regex captura "1.500" (mil e quinhentos), float("1.500") -> erro.
                # Se a regex captura "1500", float("1500") -> ok.
                # Se a regex captura "1,5" (um vírgula cinco), replace vira "1.5", float("1.5") -> ok.
                # Se o valor for tipo "1.5" (mil e quinhentos) e a regex pegar "1.5", precisa multiplicar por 1000.
                # A regex `([0-9,.]+)` é um pouco ambígua. Vamos assumir que o valor após replace(",", ".")
                # é o valor numérico direto ou precisa de ajuste se for em milhares.
                # Ex: "1.52" (mil quinhentos e vinte) -> regex pega "1.52" -> float(1.52) -> precisa *1000
                # Ex: "1520" -> regex pega "1520" -> float(1520) -> ok
                # Ex: "50.0" (cinquenta mil) -> regex pega "50.0" -> float(50.0) -> precisa *1000
                # A melhor forma é a query/sistema fornecer o valor numérico de forma consistente.
                # Por ora, vamos confiar que o valor extraído é o número direto de leucócitos.
                val = float(dados_extraidos["Leucócitos"])
                # Se o valor extraído for em milhares (ex: 1.5 para 1500), descomente a linha abaixo:
                # if val < 100: val *= 1000 # Heurística simples, ajuste conforme seus dados

                if val > 2000.0 or val < 50000.0:
                    hemogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao, "Paciente": nm_paciente,
                        "Parâmetro": "Leucócitos", "Valor": val, "Unidade": "/µL",
                        "Critério": "> 2.000 ou < 50.000"
                    })
            except (ValueError, TypeError): pass

        # Plaquetas (< 20.000/µL ou > 1.000.000/µL)
        # Valor extraído é em "mil/mmb3", então precisa multiplicar por 1000.
        if dados_extraidos.get("Plaquetas"):
            try:
                val = float(dados_extraidos["Plaquetas"]) * 1000 # Convertendo de mil/mmb3 para /µL
                if val < 20000.0 or val > 1000000.0:
                    hemogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao, "Paciente": nm_paciente,
                        "Parâmetro": "Plaquetas", "Valor": val, "Unidade": "/µL",
                        "Critério": "< 20.000 ou > 1.000.000"
                    })
            except (ValueError, TypeError): pass
            
    df_criticos = pd.DataFrame(hemogramas_criticos_lista)
    print(f'{agora()} - processar_hemogramas_criticos() - FIM. {len(df_criticos)} hemogramas críticos encontrados.')
    return df_criticos

def calcular_indicadores_hemogramas(df_hemogramas_criticos):
    print(f'{agora()} - calcular_indicadores_hemogramas() - INÍCIO')
    if df_hemogramas_criticos.empty:
        print("DataFrame de hemogramas críticos está vazio para cálculo de indicadores.")
        return {
            "total_hemogramas_criticos": 0,
            "parametros_criticos_contagem": pd.Series(dtype='int64'),
            "prescricoes_unicas_criticas_hemograma": 0,
            "top_parametros_criticos": pd.Series(dtype='int64')
        }

    total_hemogramas_criticos = len(df_hemogramas_criticos)
    # Conta a ocorrência de cada parâmetro crítico
    parametros_criticos_contagem = df_hemogramas_criticos['Parâmetro'].value_counts()
    # Número de prescrições únicas com pelo menos um valor crítico de hemograma
    prescricoes_unicas_criticas_hemograma = df_hemogramas_criticos['Prescrição'].nunique()
    
    print(f"Total de Hemogramas Críticos (parâmetros individuais): {total_hemogramas_criticos}")
    #print(f"Contagem de Parâmetros Críticos:\n{parametros_criticos_contagem}")
    #print(f"Prescrições Únicas com Hemograma Crítico: {prescricoes_unicas_criticas_hemograma}")
    
    print(f'{agora()} - calcular_indicadores_hemogramas() - FIM')
    return {
        "total_hemogramas_criticos": total_hemogramas_criticos, # Total de linhas de parâmetros críticos
        "parametros_criticos_contagem": parametros_criticos_contagem, # Series com contagem por parâmetro
        "prescricoes_unicas_criticas_hemograma": prescricoes_unicas_criticas_hemograma,
        "top_parametros_criticos": parametros_criticos_contagem.head(5) # Top 5 parâmetros
    }

def processar_coagulogramas_criticos(df_exames_rtf_bruto):
    print(f'{agora()} - processar_coagulogramas_criticos() - INÍCIO')
    print(f'df_exames_rtf_bruto: {df_exames_rtf_bruto.shape[0]} linhas')
    
    if df_exames_rtf_bruto is None or df_exames_rtf_bruto.empty:
        print("DataFrame de exames RTF brutos está vazio para Coagulograma.")
        return pd.DataFrame()

    coagulogramas_criticos_lista = []
    coluna_rtf = 'DS_RESULTADO_RTF'

    # Filtrar preliminarmente por RTFs que contêm "COAGULOGRAMA" para otimizar
    # Usamos .astype(str) para evitar erros se houver valores não string, e na=False para tratar NaNs.
    df_coagulograma_candidatos = df_exames_rtf_bruto[
        df_exames_rtf_bruto[coluna_rtf].astype(str).str.contains("COAGULOGRAMA", case=False, na=False)
    ].copy()
    print(f"{agora()} - df_coagulograma_candidatos: {df_coagulograma_candidatos.shape[0]} linhas encontradas contendo 'COAGULOGRAMA'.")
    #print(f'\n###########################################################')

    for index, linha in df_coagulograma_candidatos.iterrows():
        #print(f'{agora()} - Processando linha {index} de {df_coagulograma_candidatos.shape[0]}')
        nr_prescricao = linha.get('NR_PRESCRICAO', 'N/A')
        nm_paciente = linha.get('NM_PACIENTE', 'N/A')
        dt_exame = linha.get('DT_EXAME', None)
        ds_resultado_valor_rtf = linha[coluna_rtf]
        if pd.isna(ds_resultado_valor_rtf) or not ds_resultado_valor_rtf:
            continue

        texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)

        # Regex para extrair INR: Procura "INR", seguido por espaços/pontos e ":", depois o valor.
        match_inr = re.search(r"INR\s*\.*\s*:\s*([0-9,]+)", texto_limpo, re.IGNORECASE)
        
        if match_inr:
            try:
                inr_str = match_inr.group(1).strip().replace(",", ".")
                inr_val = float(inr_str)
                #if inr_val > 2.2:
                #    print(f'inr_val:{inr_val}')
                if inr_val > 6.00:
                    coagulogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao,
                        "Paciente": nm_paciente,
                        "Parâmetro": "INR",
                        "Valor": inr_val,
                        "Unidade": "", # INR não tem unidade explícita comum
                        "Critério": "> 6.00",
                        "Data Exame": dt_exame
                    })
                    print(f'inr_val:{inr_val}')
            except (ValueError, TypeError):
                pass # Ignora se não conseguir converter

    df_criticos = pd.DataFrame(coagulogramas_criticos_lista)
    print(f'{agora()} - processar_coagulogramas_criticos():{df_criticos.shape[0]} linhas')
    print(f'{agora()} - FIM.')
    print(f'{agora()} - processar_coagulogramas_criticos() - FIM. {len(df_criticos)} coagulogramas críticos encontrados.')
    return df_criticos

def calcular_indicadores_coagulograma(df_coagulogramas_criticos):
    print(f'{agora()} - calcular_indicadores_coagulograma() - INÍCIO')
    if df_coagulogramas_criticos.empty:
        print("DataFrame de coagulogramas críticos está vazio.")
        print(f'{agora()} - calcular_indicadores_coagulograma() - FIM')
        return {
            "total_coagulogramas_criticos": 0,
            "prescricoes_unicas_criticas_coagulograma": 0,
            "media_inr_critico": 0.0
        }

    total_coagulogramas_criticos = len(df_coagulogramas_criticos)
    prescricoes_unicas_criticas_coagulograma = df_coagulogramas_criticos['Prescrição'].nunique()
    media_inr_critico = df_coagulogramas_criticos['Valor'].mean() if total_coagulogramas_criticos > 0 else 0.0
    
    print(f"Total de Coagulogramas Críticos (INR > 6.00): {total_coagulogramas_criticos}")
    print(f"Prescrições Únicas com Coagulograma Crítico: {prescricoes_unicas_criticas_coagulograma}")
    print(f"Média do INR Crítico: {media_inr_critico:.2f}")
    
    print(f'{agora()} - calcular_indicadores_coagulograma() - FIM')
    return {
        "total_coagulogramas_criticos": total_coagulogramas_criticos,
        "prescricoes_unicas_criticas_coagulograma": prescricoes_unicas_criticas_coagulograma,
        "media_inr_critico": media_inr_critico
    }



def processar_hepatogramas_criticos(df_exames_rtf_bruto):
    print(f'{agora()} - processar_hepatogramas_criticos() - INÍCIO')
    print(f'df_exames_rtf_bruto: {df_exames_rtf_bruto.shape[0]} linhas')
    
    if df_exames_rtf_bruto is None or df_exames_rtf_bruto.empty:
        print("DataFrame de exames RTF brutos está vazio para Hepatograma.")
        return pd.DataFrame()

    hepatogramas_criticos_lista = []
    coluna_rtf = 'DS_RESULTADO_RTF' # Assumindo que a coluna RTF é a mesma

    # Filtrar preliminarmente por RTFs que contêm "HEPATOGRAMA"
    df_hepatograma_candidatos = df_exames_rtf_bruto[
        df_exames_rtf_bruto[coluna_rtf].astype(str).str.contains("HEPATOGRAMA", case=False, na=False)
    ].copy()
    print(f"{agora()} - df_hepatograma_candidatos: {df_hepatograma_candidatos.shape[0]} linhas encontradas contendo 'HEPATOGRAMA'.")

    for index, linha in df_hepatograma_candidatos.iterrows():
        nr_prescricao = linha.get('NR_PRESCRICAO', 'N/A')
        nm_paciente = linha.get('NM_PACIENTE', 'N/A')
        dt_exame = linha.get('DT_EXAME', None) # Se disponível e relevante
        ds_resultado_valor_rtf = linha[coluna_rtf]

        if pd.isna(ds_resultado_valor_rtf) or not ds_resultado_valor_rtf:
            continue

        texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)

        # Regex para extrair "Contagem de plaquetas"
        # Ajuste esta regex conforme o padrão exato no seu RTF/texto limpo.
        # Exemplo: "Contagem de plaquetas: 150.000 /uL" ou "Plaquetas: 150 mil/mm3"
        # Esta regex tenta ser um pouco genérica para "Plaquetas" ou "Contagem de plaquetas"
        # e captura o valor e, opcionalmente, a unidade "mil".
        match_plaquetas = re.search(r"(?:Contagem de plaquetas|Plaquetas)\s*[:\s]*\s*([0-9,.]+)\s*(mil)?(?:/uL|/mm3|/\xb5L)?", texto_limpo, re.IGNORECASE)
        
        # Flag para saber se este exame já foi adicionado por causa das plaquetas
        # Isso é mais para controle de log ou se quiséssemos evitar duplicidade exata,
        # mas a abordagem atual é adicionar uma entrada por parâmetro crítico.

        if match_plaquetas:
            try:
                plaquetas_str = match_plaquetas.group(1).strip().replace(",", ".")
                plaquetas_val = float(plaquetas_str)
                unidade_mil = match_plaquetas.group(2)
                if unidade_mil and unidade_mil.lower() == 'mil':
                    plaquetas_val *= 1000
                
                # Critério de criticidade: < 20.000/uL ou > 1.000.000/uL
                if plaquetas_val < 20000.0 or plaquetas_val > 1000000.0:
                    hepatogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao,
                        "Paciente": nm_paciente,
                        "Parâmetro": "Contagem de Plaquetas (Hepatograma)",
                        "Valor": plaquetas_val,
                        "Unidade": "/uL", # Padronizando a unidade após conversão
                        "Critério": "< 20.000 ou > 1.000.000",
                        "Data Exame": dt_exame # Se aplicável
                    })
                    # print(f'Plaquetas (Hepatograma) Críticas: {plaquetas_val} para prescrição {nr_prescricao}')
            except (ValueError, TypeError) as e:
                # print(f"Erro ao converter plaquetas do hepatograma para float: '{match_plaquetas.group(1)}' na prescrição {nr_prescricao}. Erro: {e}")
                pass # Ignora se não conseguir converter
        # else: # Removido o print de debug para plaquetas não encontradas para não poluir o log se for comum
            # print(f"DEBUG Hepatograma: Nenhuma contagem de plaquetas encontrada para prescrição {nr_prescricao} no texto: {texto_limpo[:200]}")

        # Regex para extrair Bilirrubina (Total, Direta, Indireta - priorizando Total se houver)
        # Esta regex tenta capturar "Bilirrubina Total" ou apenas "Bilirrubina"
        # Ajuste conforme os nomes exatos nos seus laudos.
        # Ex: "Bilirrubina Total: 16.5 mg/dL"
        match_bilirrubina = re.search(r"(Bilirrubina\s*(?:Total)?)\s*[:\s]*\s*([0-9,.]+)\s*(?:mg/dL)?", texto_limpo, re.IGNORECASE)

        if match_bilirrubina:
            try:
                bilirrubina_str = match_bilirrubina.group(2).strip().replace(",", ".")
                bilirrubina_val = float(bilirrubina_str)

                # Critério de criticidade: Bilirrubina > 15 mg/dL
                if bilirrubina_val > 15.0:
                    hepatogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao,
                        "Paciente": nm_paciente,
                        "Parâmetro": "Bilirrubina", # Poderia ser match_bilirrubina.group(1) para pegar "Bilirrubina Total"
                        "Valor": bilirrubina_val,
                        "Unidade": "mg/dL",
                        "Critério": "> 15 mg/dL",
                        "Data Exame": dt_exame
                    })
                    # print(f'Bilirrubina Crítica: {bilirrubina_val} para prescrição {nr_prescricao}')
            except (ValueError, TypeError) as e:
                # print(f"Erro ao converter bilirrubina do hepatograma para float: '{match_bilirrubina.group(2)}' na prescrição {nr_prescricao}. Erro: {e}")
                pass
    print(f"{agora()} tamanho da lista: {len(hepatogramas_criticos_lista)}")
    df_criticos = pd.DataFrame(hepatogramas_criticos_lista)
    print(f'{agora()} - processar_hepatogramas_criticos() - FIM. {len(df_criticos)} hepatogramas com plaquetas críticas encontrados.')
    return df_criticos


def calcular_indicadores_hepatograma(df_hepatogramas_criticos):
    print(f'{agora()} - calcular_indicadores_hepatograma() - INÍCIO')
    if df_hepatogramas_criticos.empty:
        print("DataFrame de hepatogramas críticos (plaquetas) está vazio.")
        print(f'{agora()} - calcular_indicadores_hepatograma() - FIM')
        return {
            "total_hepatogramas_plaquetas_criticas": 0,
            "prescricoes_unicas_criticas_hepatograma_plaquetas": 0,
            # Adicione outras métricas se desejar, ex: média, min, max das plaquetas críticas
        }

    total_hepatogramas_plaquetas_criticas = len(df_hepatogramas_criticos)
    prescricoes_unicas_criticas_hepatograma_plaquetas = df_hepatogramas_criticos['Prescrição'].nunique()
    
    print(f"Total de Hepatogramas com Plaquetas Críticas: {total_hepatogramas_plaquetas_criticas}")
    print(f"Prescrições Únicas com Hepatograma (Plaquetas Críticas): {prescricoes_unicas_criticas_hepatograma_plaquetas}")
    
    print(f'{agora()} - calcular_indicadores_hepatograma() - FIM')
    return {
        "total_hepatogramas_plaquetas_criticas": total_hepatogramas_plaquetas_criticas,
        "prescricoes_unicas_criticas_hepatograma_plaquetas": prescricoes_unicas_criticas_hepatograma_plaquetas
    }

def processar_lipidogramas_criticos(df_exames_rtf_bruto):
    print(f'{agora()} - processar_lipidogramas_criticos() - INÍCIO')
    
    if df_exames_rtf_bruto is None or df_exames_rtf_bruto.empty:
        print("DataFrame de exames RTF brutos está vazio para Lipidograma.")
        return pd.DataFrame()

    lipidogramas_criticos_lista = []
    coluna_rtf = 'DS_RESULTADO_RTF'

    # Filtrar preliminarmente por RTFs que contêm "LIPIDOGRAMA" ou "COLESTEROL"
    df_lipidograma_candidatos = df_exames_rtf_bruto[
        df_exames_rtf_bruto[coluna_rtf].astype(str).str.contains("LIPIDOGRAMA|COLESTEROL", case=False, na=False, regex=True)
    ].copy()
    print(f"{agora()} - df_lipidograma_candidatos: {df_lipidograma_candidatos.shape[0]} linhas encontradas contendo 'LIPIDOGRAMA' ou 'COLESTEROL'.")

    for index, linha in df_lipidograma_candidatos.iterrows():
        nr_prescricao = linha.get('NR_PRESCRICAO', 'N/A')
        nm_paciente = linha.get('NM_PACIENTE', 'N/A')
        dt_exame = linha.get('DT_EXAME', None)
        ds_resultado_valor_rtf = linha[coluna_rtf]

        if pd.isna(ds_resultado_valor_rtf) or not ds_resultado_valor_rtf:
            continue

        texto_limpo = limpar_rtf_para_texto(ds_resultado_valor_rtf)

        # Regex para extrair "COLESTEROL TOTAL"
        # Procura "COLESTEROL TOTAL", seguido opcionalmente por espaços/pontos e ":", depois o valor.
        match_colesterol = re.search(r"COLESTEROL\s*TOTAL\s*\.*\s*:?\s*([0-9,.]+)", texto_limpo, re.IGNORECASE)
        
        if match_colesterol:
            try:
                colesterol_str = match_colesterol.group(1).strip().replace(",", ".")
                colesterol_val = float(colesterol_str)
                
                # Critério: Colesterol Total > 0
                if colesterol_val > 0:
                    lipidogramas_criticos_lista.append({
                        "Prescrição": nr_prescricao,
                        "Paciente": nm_paciente,
                        "Parâmetro": "Colesterol Total",
                        "Valor": colesterol_val,
                        "Unidade": "mg/dL", # Assumindo mg/dL, ajuste se necessário
                        "Critério": "> 0",
                        "Data Exame": dt_exame
                    })
            except (ValueError, TypeError) as e:
                # print(f"Erro ao converter Colesterol Total: '{colesterol_str}' para Prescrição {nr_prescricao}. Erro: {e}")
                pass 

    df_criticos = pd.DataFrame(lipidogramas_criticos_lista)
    print(f'{agora()} - processar_lipidogramas_criticos() - FIM. {len(df_criticos)} lipidogramas (Colesterol Total > 0) encontrados.')
    return df_criticos

def calcular_indicadores_lipidograma(df_lipidogramas_criticos):
    print(f'{agora()} - calcular_indicadores_lipidograma() - INÍCIO')
    if df_lipidogramas_criticos.empty:
        print("DataFrame de lipidogramas críticos está vazio.")
        return {
            "total_lipidogramas_criticos": 0,
            "prescricoes_unicas_criticas_lipidograma": 0,
            "media_colesterol_total": 0.0 
        }

    total_lipidogramas_criticos = len(df_lipidogramas_criticos)
    prescricoes_unicas_criticas_lipidograma = df_lipidogramas_criticos['Prescrição'].nunique()
    media_colesterol_total = df_lipidogramas_criticos['Valor'].mean() if total_lipidogramas_criticos > 0 else 0.0
    
    print(f"Total de Lipidogramas (Colesterol Total > 0): {total_lipidogramas_criticos}")
    print(f"Prescrições Únicas com Lipidograma (Colesterol Total > 0): {prescricoes_unicas_criticas_lipidograma}")
    print(f"Média do Colesterol Total (para os > 0): {media_colesterol_total:.2f}")
    
    print(f'{agora()} - calcular_indicadores_lipidograma() - FIM')
    return {
        "total_lipidogramas_criticos": total_lipidogramas_criticos,
        "prescricoes_unicas_criticas_lipidograma": prescricoes_unicas_criticas_lipidograma,
        "media_colesterol_total": media_colesterol_total
    }

def mostrar_pagina_valores_criticos():
    try:
        # Inicializa o session_state para controlar a execução
        if 'busca_realizada' not in st.session_state:
            st.session_state.busca_realizada = False
            st.session_state.df_criticos = pd.DataFrame()
            st.session_state.df_rtf = pd.DataFrame()
            st.session_state.indicadores = {}
            # ... outros estados que precisar guardar

        st.write("# Valores críticos")
        
        # --- BARRA LATERAL (SIDEBAR) COM FILTROS E BOTÃO ---
        with st.sidebar:
            st.write('# Filtros de Data:')
            data_inicial = st.date_input(
                "Data Inicial",
                value=datetime.date.today() - datetime.timedelta(days=1),
                max_value=datetime.date.today()
            )
            data_final = st.date_input(
                "Data Final",
                value=datetime.date.today(),
                max_value=datetime.date.today(),
                min_value=data_inicial
            )
            
            if st.button("Buscar Dados", type="primary"):
                st.session_state.busca_realizada = True

                with st.spinner('Buscando dados de valores críticos...'):
                    st.session_state.df_criticos = valores_criticos_exames(data_inicial, data_final)
                
                with st.spinner('Buscando dados de exames complexos (RTF)... Isso pode levar um minuto.'):
                    st.session_state.df_rtf = buscar_dados_hemogramas(data_inicial, data_final)

        # --- ÁREA PRINCIPAL DA PÁGINA ---
        if st.session_state.busca_realizada:
            # Se a busca foi feita, executa todo o processamento e exibição
            df = st.session_state.df_criticos
            df_hemogramas_bruto = st.session_state.df_rtf

            # --- Placeholders para cada seção de processamento ---
            placeholder_sinteticos = st.empty()
            placeholder_hemograma = st.empty()
            placeholder_coagulograma = st.empty()
            placeholder_hepatograma = st.empty()
            placeholder_lipidograma = st.empty()
            placeholder_analitico = st.empty()

            # --- Processamento e Exibição dos Indicadores Sintéticos ---
            with placeholder_sinteticos.container():
                with st.spinner("Calculando indicadores sintéticos..."):
                    indicadores = calculo_valores_criticos_exames(df)
                
                # --- Exibição dos Indicadores Sintéticos ---
                if not df.empty:
                    st.write("## Indicadores Sintéticos Chave")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(label="🔥 Total Exames Críticos", value=indicadores.get("total_exames_criticos", 0))
                    with col2:
                        st.metric(label="⚠️ Tipos de Exame Afetados", value=indicadores.get("tipos_exames_distintos_criticos", 0))
                    with col3:
                        st.metric(label="🏥 Pacientes Únicos Afetados", value=indicadores.get("pacientes_unicos_afetados", 0), delta_color="off")
                    with col4:
                        st.metric(label="📌 Prescrições Únicas Críticas", value=indicadores.get("total_prescricoes_unicas_criticas", 0))
                else:
                    st.caption("Nenhum dado de valor crítico para exibir.")
                st.write('___________________')

            # --- Processamento e Exibição de Hemogramas ---
            with placeholder_hemograma.container():
                with st.spinner("Processando Hemogramas Críticos..."):
                    df_hemogramas_criticos = processar_hemogramas_criticos(df_hemogramas_bruto)
                    indicadores_hemograma = calcular_indicadores_hemogramas(df_hemogramas_criticos)

                # --- Exibição dos Indicadores de Hemograma ---
                if not df_hemogramas_criticos.empty:
                    st.write("## Indicadores de Hemogramas Críticos")
                    col_hemo1, col_hemo2 = st.columns(2)
                    with col_hemo1:
                        st.metric(label="🩸 Total Parâmetros Críticos", 
                                    value=indicadores_hemograma.get("total_hemogramas_criticos", 0))
                    with col_hemo2:
                        st.metric(label="📄 Prescrições com Hemograma Crítico", 
                                    value=indicadores_hemograma.get("prescricoes_unicas_criticas_hemograma", 0))
                    
                    with st.expander("Detalhes dos Hemogramas Críticos"):
                         st.dataframe(df_hemogramas_criticos, use_container_width=True, hide_index=True)
                else:
                    # Você pode optar por não mostrar nada se não houver dados, ou uma mensagem
                    st.write("## Indicadores de Hemogramas Críticos")
                    st.caption("Nenhum hemograma crítico encontrado no período.")
                st.write('___________________')

            # --- Processamento e Exibição de Coagulogramas ---
            with placeholder_coagulograma.container():
                with st.spinner("Processando Coagulogramas Críticos..."):
                    df_coagulogramas_criticos = processar_coagulogramas_criticos(df_hemogramas_bruto)
                    indicadores_coagulograma = calcular_indicadores_coagulograma(df_coagulogramas_criticos)
                
                if not df_coagulogramas_criticos.empty:
                    st.write("## Indicadores de Coagulogramas Críticos (INR > 6.00)")
                    col_coag1, col_coag2, col_coag3 = st.columns(3)
                    with col_coag1:
                        st.metric(label="🩸 Total Coagulogramas Críticos", value=indicadores_coagulograma.get("total_coagulogramas_criticos", 0))
                    with col_coag2:
                        st.metric(label="📄 Prescrições com Coagulograma Crítico", value=indicadores_coagulograma.get("prescricoes_unicas_criticas_coagulograma", 0))
                    with col_coag3:
                        st.metric(label="📈 Média INR (Críticos)", value=f"{indicadores_coagulograma.get('media_inr_critico', 0.0):.2f}")
                    
                    with st.expander("Detalhes dos Coagulogramas Críticos"):
                        st.dataframe(df_coagulogramas_criticos, use_container_width=True, hide_index=True)
                else:
                    st.write("## Indicadores de Coagulogramas Críticos (INR > 6.00)")
                    st.caption("Nenhum coagulograma crítico encontrado no período.")
                st.write('___________________')
            
            # --- Processamento e Exibição de Hepatogramas ---
            with placeholder_hepatograma.container():
                with st.spinner("Processando Hepatogramas Críticos..."):
                    df_hepatogramas_plaquetas_criticas = processar_hepatogramas_criticos(df_hemogramas_bruto)
                    indicadores_hepatograma_plaquetas = calcular_indicadores_hepatograma(df_hepatogramas_plaquetas_criticas)

                if not df_hepatogramas_plaquetas_criticas.empty:
                    st.write("## Indicadores de Hepatograma (Plaquetas Críticas)")
                    col_hepato1, col_hepato2 = st.columns(2)
                    with col_hepato1:
                        st.metric(label="🧪 Total Hepatogramas (Plaquetas Críticas)", value=indicadores_hepatograma_plaquetas.get("total_hepatogramas_plaquetas_criticas", 0))
                    with col_hepato2:
                        st.metric(label="📄 Prescrições com Hepatograma (Plaquetas Críticas)", value=indicadores_hepatograma_plaquetas.get("prescricoes_unicas_criticas_hepatograma_plaquetas", 0))
                    
                    with st.expander("Detalhes dos Hepatogramas com Plaquetas Críticas"):
                        st.dataframe(df_hepatogramas_plaquetas_criticas, use_container_width=True, hide_index=True)
                else:
                    st.write("## Indicadores de Hepatograma (Plaquetas Críticas)")
                    st.caption("Nenhum hepatograma com plaquetas críticas encontrado no período.")
                st.write('___________________')

            # --- Processamento e Exibição de Lipidogramas ---
            with placeholder_lipidograma.container():
                with st.spinner("Processando Lipidogramas Críticos..."):
                    df_lipidogramas_criticos = processar_lipidogramas_criticos(df_hemogramas_bruto)
                    indicadores_lipidograma = calcular_indicadores_lipidograma(df_lipidogramas_criticos)

                if not df_lipidogramas_criticos.empty:
                    st.write("## Indicadores de Lipidograma (Colesterol Total > 0)")
                    col_lipi1, col_lipi2, col_lipi3 = st.columns(3)
                    with col_lipi1:
                        st.metric(label="🧪 Total Lipidogramas (Col. > 0)", value=indicadores_lipidograma.get("total_lipidogramas_criticos", 0))
                    with col_lipi2:
                        st.metric(label="📄 Prescrições com Lipidograma (Col. > 0)", value=indicadores_lipidograma.get("prescricoes_unicas_criticas_lipidograma", 0))
                    with col_lipi3:
                        st.metric(label="📈 Média Colesterol Total (mg/dL)", value=f"{indicadores_lipidograma.get('media_colesterol_total', 0.0):.2f}")

                    with st.expander("Detalhes dos Lipidogramas"):
                        st.dataframe(df_lipidogramas_criticos, use_container_width=True, hide_index=True)
                else:
                    st.write("## Indicadores de Lipidograma (Colesterol Total > 0)")
                    st.caption("Nenhum lipidograma crítico encontrado no período.")
                st.write('___________________')
            
            #Substitui os espancos em branco por hifen:
            if not df.empty:
                df = df.fillna('-')
            
            #Removendo a virgula do atendimento e prescricao
            if not df.empty and 'NR_ATENDIMENTO' in df.columns and 'NR_PRESCRICAO' in df.columns:
                df['NR_ATENDIMENTO'] = df['NR_ATENDIMENTO'].apply(lambda x: "{:.0f}".format(x) if pd.notnull(x) else '-')
                df['NR_PRESCRICAO'] = df['NR_PRESCRICAO'].apply(lambda x: "{:.0f}".format(x) if pd.notnull(x) else '-')
            elif df.empty:
                print(f"{agora()} - DataFrame 'df' está vazio. Pulando formatação de NR_ATENDIMENTO e NR_PRESCRICAO.")
        
            df = df.rename(columns={
                'NM_EXAME': 'EXAME',
                'NR_ATENDIMENTO': 'ATENDIMENTO',
                'NR_PRESCRICAO': 'PRESCRICAO',
                'NM_PACIENTE': 'PACIENTE',
                'RESULTADO': 'RESULTADO',
                'DT_COLETA': 'COLETA',
                'DT_DIGITACAO': 'DIGITACAO',
                'DT_APROVACAO': 'APROVACAO',
                'DT_IMPRESSAO': 'IMPRESSAO'
            })

            with placeholder_analitico.container():
                st.write(f'Atualizado: {datetime.datetime.now().strftime("%d/%m/%Y as %H:%M:%S")}')
                st.write('___________________')
                
                # Exibindo data frame Analitico:
                with st.expander("Visualizar Dados Analíticos Detalhados", expanded=False):
                    if not df.empty:
                        st.dataframe(df[['EXAME' , 'RESULTADO', 'PRESCRICAO', 'PACIENTE' ,  'COLETA', 'DIGITACAO', 'APROVACAO', 'IMPRESSAO']],hide_index=True, use_container_width=True)
                    else:
                        st.caption("Nenhum dado para exibir.")

        else:
            st.info("⬅️ Por favor, selecione um período e clique em 'Buscar Dados' na barra lateral para começar.")

    except Exception as err:
        print(f'{agora()} - Inexperado {err=}, {type(err)=}')
        st.error(f"Ocorreu um erro ao carregar a página Valores Críticos: {err}")

# Chamar a função principal da página para renderizar seu conteúdo
mostrar_pagina_valores_criticos()