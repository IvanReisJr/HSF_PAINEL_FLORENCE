import io
import os

import oracledb
import pandas as pd
import streamlit as st
from assets.design_system import COMMON_STYLE, THEMES


@st.cache_resource
def ensure_oracle_initialized() -> bool:
    """Inicializa o cliente Oracle uma única vez por processo em Thick Mode.

    Usa os.add_dll_directory() SEM bloco 'with' para manter o handle vivo
    permanentemente durante o processo. Isso é necessário porque:
    - lib_dir= falha com UnicodeDecodeError em paths com 'ç'/'ã' (_Homologação)
    - os.environ["PATH"] não propaga para o carregador de DLLs no nível C do Windows
    - TASY usa autenticação 0x939 que requer Thick Mode (DPY-3015 em thin mode)

    DPY-2016/DPY-2017 = já inicializado = sucesso (não há fallback para thin mode).
    """
    _JA_INIT = ("DPY-2016", "DPY-2017", "already been initialized")

    # Detecta o diretório raiz do projeto dinamicamente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_instantclient = os.path.join(
        base_dir, 
        "instantclient-basiclite-windows.x64-23.6.0.24.10", 
        "instantclient_23_6"
    )
    abs_path = os.path.abspath(caminho_instantclient)

    if not os.path.exists(abs_path):
        return False

    try:
        # A forma mais robusta: passar o lib_dir diretamente para o driver
        # Isso substitui o os.add_dll_directory e costuma resolver o Error 126
        oracledb.init_oracle_client(lib_dir=abs_path)
        return True
    except Exception as e:
        # Se ja estiver inicializado, apenas confirmamos o sucesso
        if any(code in str(e) for code in _JA_INIT):
            return True
        st.error(f"Erro ao inicializar Oracle Client (Portatil): {e}. Verifique se as DLLs vcruntime140 e msvcp140 estao na pasta {abs_path}")
        return False


def export_to_excel(df: pd.DataFrame, sheet_name: str = "Planilha1") -> bytes:
    """Converte um DataFrame para bytes de arquivo Excel (.xlsx) em memória."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def calcular_indicadores(df: pd.DataFrame) -> dict:
    """Calcula indicadores de escalas clínicas a partir do DataFrame do Censo.

    Função pura (sem I/O, sem Streamlit) — testável isoladamente.
    """
    total_atendimentos = df["NR_ATENDIMENTO"].dropna().count()
    indicadores: dict = {"total_atendimentos": total_atendimentos}

    config_escalas = [
        {"nome": "mews",    "cd": "CD_MEWS",    "ds": "MEWS"},
        {"nome": "braden",  "cd": "CD_BRADEN",  "ds": "BRADEN"},
        {"nome": "saps3",   "cd": "CD_SAPSIII", "ds": "SAP3"},
        {"nome": "rass",    "cd": "CD_RASS",    "ds": "RASS"},
        {"nome": "glasgow", "cd": "CD_GLASGOW", "ds": "GLASGOW"},
        {"nome": "fugulin", "cd": "CD_FUGULIN", "ds": "FUGULIN"},
        {"nome": "martins", "cd": "MARTINS",    "ds": "MARTINS"},
    ]

    for cfg in config_escalas:
        nome, col_cd, col_ds = cfg["nome"], cfg["cd"], cfg["ds"]
        total_classificado = int(df[col_cd].dropna().count()) if col_cd in df.columns else 0
        indicadores[f"total_{nome}"] = total_classificado
        indicadores[f"sem_classificacao_{nome}"] = total_atendimentos - total_classificado
        if col_ds in df.columns:
            indicadores[f"contagem_{nome}"] = (
                df[col_ds].value_counts().rename_axis("Descrição").reset_index(name="Qtde")
            )

    return indicadores


def apply_florence_ui():
    """Aplica o estilo visual Florence e gerencia o tema.
    
    Retorna o nome do template Plotly a ser usado.
    """
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    # Injeta CSS base e variáveis de tema
    st.markdown(COMMON_STYLE, unsafe_allow_html=True)
    st.markdown(THEMES[st.session_state.theme]["vars"], unsafe_allow_html=True)

    return THEMES[st.session_state.theme]["plotly"]
