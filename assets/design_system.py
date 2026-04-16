
# Design System para o Painel Florence
# Estética: Midnight Obsidian (High Contrast)

COMMON_STYLE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@600;700&display=swap" rel="stylesheet">

<style>
    /* Tipografia de Alta Precisão */
    html, body, [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span:not([data-testid*="Icon"]), [data-testid="stAppViewContainer"] div:not([data-testid*="Icon"]), label {
        font-family: 'Inter', sans-serif !important;
    }

    h1, h2, h3, h4, h5, [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
    }
    
    /* Métricas - Contraste Solicitado */
    div[data-testid="stMetricValue"] > div { color: var(--text-main) !important; font-size: 2.2rem !important; font-weight: 600 !important; }
    
    /* UNIFICAÇÃO DE LEGENDAS: Forçando #FFFFFF99 em todos os elementos de apoio */
    [data-testid="stMetricLabel"] *, 
    [data-testid="stVerticalBlock"] .stMarkdown p,
    [data-testid="stVerticalBlock"] .stText p,
    .stWrite p {
        color: var(--text-muted) !important;
    }

    /* Tabelas Clean - Sem Índice */
    .stTable thead tr th:first-child { display:none !important; }
    .stTable tbody tr td:first-child { display:none !important; }

    /* Cards 'Midnight' */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        margin-bottom: 2rem !important;
    }

    /* ALINHAMENTO DE FILTROS E BOTÕES */
    [data-testid="stHorizontalBlock"] { align-items: flex-end !important; }
    
    .stButton>button, [data-testid="stSelectbox"] div[data-baseweb="select"] {
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Estilização Premium do Toggle (Sol/Lua) */
    div[data-testid="stCheckbox"] > label > div[role="switch"] {
        background: #1d1d21 !important;
        border: 1px solid #333 !important;
        height: 30px !important; width: 60px !important;
        position: relative !important;
    }
    
    div[data-testid="stCheckbox"] > label > div[role="switch"]::before {
        content: '🌙'; position: absolute; right: 8px; top: 3px; font-size: 14px;
    }
    
    div[data-testid="stCheckbox"] > label > div[role="switch"]::after {
        content: '☀️'; position: absolute; left: 8px; top: 3px; font-size: 14px;
    }

    div[data-testid="stCheckbox"] > label > div[role="switch"] > div {
        background: #FFFFFF !important;
        height: 22px !important; width: 22px !important;
        margin-top: 3px !important; z-index: 2;
    }

    /* Sidebar */
    [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: var(--text-main) !important; font-weight: 500 !important; }
</style>
"""

THEMES = {
    "light": {
        "vars": """
        <style>
            :root {
                --card-bg: #ffffff;
                --card-border: #e5e7eb;
                --text-main: #000000;
                --text-muted: rgba(0, 0, 0, 0.6);
                --button-bg: #f9fafb;
            }
            .stApp { background-color: #f8fafc; }
            [data-testid="stSidebar"] { background-color: #ffffff !important; }
        </style>
        """,
        "plotly": "plotly_white"
    },
    "dark": {
        "vars": """
        <style>
            :root {
                --card-bg: #121214;
                --card-border: #262626;
                --text-main: #FFFFFF;
                --text-muted: #FFFFFF99;
                --button-bg: #1d1d21;
            }
            .stApp { background-color: #0A0A0B; }
            [data-testid="stSidebar"] { 
                background-color: #0A0A0B !important; 
                border-right: 1px solid var(--card-border);
            }
            .stTable td, .stTable th {
                color: #FFFFFF !important;
            }
        </style>
        """,
        "plotly": "plotly_dark"
    }
}
