import streamlit as st
import datetime

# Data da última modificação: 2024-05-24
# Autor: @PLima
# Descrição: HFS - Painel de indicadores para a equipe de Enfermagem (Florence).

# Comandos úteis:
# Ativar ambiente virtual: venv\Scripts\activate
# Rodar o app: streamlit run Home.py --server.port 8002

# --- Configuração da Página ---
# O título e o ícone da página podem ser definidos no .streamlit/config.toml,
# mas é uma boa prática tê-los aqui como fallback.
st.set_page_config(
    page_title="HSF - Painel Enfermagem",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constantes ---
LOGO_PATH = 'HSF_LOGO_-_1228x949_001.png'

# --- Funções Auxiliares ---
def agora():
    """Retorna a data e hora atual formatada como string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Função principal que constrói a página inicial do aplicativo."""
    st.logo(LOGO_PATH) # Adiciona o logo no topo da sidebar
    st.image(LOGO_PATH, width=400)
    st.title('Dashboard Florence - HSF - Enfermagem')
    st.subheader('Destinado para exibição de indicadores pertinentes à Enfermagem do Hospital.')

if __name__ == "__main__":
    # Este bloco é executado quando o script é chamado diretamente com 'python Home.py'.
    # Para rodar o aplicativo Streamlit, use o comando: streamlit run Home.py
    print("Para iniciar o aplicativo, execute o seguinte comando no seu terminal:")
    print("streamlit run Home.py --server.port 8002")
