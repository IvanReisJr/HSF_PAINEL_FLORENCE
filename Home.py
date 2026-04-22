import datetime
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import apply_florence_ui, ensure_oracle_initialized

# --- Configuração da Página ---
st.set_page_config(
    page_title="HSF - Painel Enfermagem",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constantes ---
LOGO_PATH = 'HSF_LOGO_-_1228x949_001.png'


def main():
    """Função principal que constrói a página inicial do aplicativo."""
    
    # Sidebar: Configurações de Tema
    with st.sidebar:
        st.markdown("### 🎨 Interface")
        
        # Função para troca imediata
        if "theme" not in st.session_state:
            st.session_state.theme = "light"
            
        def change_theme():
            st.session_state.theme = "dark" if st.session_state.theme_toggle else "light"

        st.toggle(
            "Modo Escuro" if st.session_state.theme == "dark" else "Modo Claro", 
            key="theme_toggle",
            value=st.session_state.theme == "dark",
            on_change=change_theme
        )
        st.divider()

    # Aplica UI Florence e obtém template Plotly
    apply_florence_ui()
    
    # Inicialização do Banco
    db_status = ensure_oracle_initialized()
    
    # Layout Principal
    st.logo(LOGO_PATH)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(LOGO_PATH, width=350)
        
    with col2:
        # Card de Boas-vindas Midnight Obsidian
        with st.container(border=True):
            st.markdown(f"""
                <div style="padding: 10px 0;">
                    <h1 style="margin:0; font-size: 2.2rem;">Dashboard Florence</h1>
                    <p style="font-size:1.1rem; color: var(--text-muted); margin-bottom: 20px;">HFS - Gestão de Indicadores de Enfermagem</p>
                    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--button-bg); border-radius: 8px; border: 1px solid var(--card-border);">
                        <div style="
                            width: 10px; height: 10px; border-radius: 50%; 
                            background: {'#10b981' if db_status else '#ef4444'};
                            box-shadow: 0 0 10px {'rgba(16, 185, 129, 0.4)' if db_status else 'rgba(239, 68, 68, 0.4)'};
                        "></div>
                        <span style="font-weight:500; font-size: 0.9rem; color: var(--text-main);">
                            Status do Sistema: <span style="color: {'#10b981' if db_status else '#ef4444'};">{'Conectado ao TASY' if db_status else 'Offline'}</span>
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.caption("Utilize o menu lateral para navegar entre o Censo e o Centro Cirúrgico.")


if __name__ == "__main__":
    main()
