#16/06/2025
#@PLima
#HFS - PAINEL PARA O FLORENCE

import streamlit as st
import datetime

#venv\Scripts\activate
#streamlit run Home.py --server.port 8002

#Configurando pagina para exibicao em modo WIDE:
st.set_page_config(layout="wide",initial_sidebar_state="expanded")

# Caminho da sua imagem (ajuste conforme a sua estrutura de pastas)
logo_path = 'HSF_LOGO_-_1228x949_001.png'

def agora():
    agora = datetime.datetime.now()
    agora = agora.strftime("%Y-%m-%d %H:%M:%S")
    return str(agora)

if __name__ == "__main__":
    print(f'{agora()} - =================================== Home.py - __main__')
    st.logo(logo_path,size="large")
    #st.sidebar.markdown("# HOME")
    st.image(logo_path,width=400)
    st.write('\n\n\n\n')
    st.write('\n\n\n\n')
    st.write('# Dashboard - Enfermagem')
    st.write('\n\n\n\n')
    st.write('## Destinado para exibição de indicadores pertinentes ao Enfermagem do Hospital...')
