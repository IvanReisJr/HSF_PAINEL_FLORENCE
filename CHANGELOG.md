# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.  
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [Não lançado] — 2025-04-15

### Corrigido
- **`utils.py`** — Inicialização do Oracle Client refatorada para usar
  `os.add_dll_directory()` (API Windows wide-string / UTF-16) em vez de passar
  `lib_dir` diretamente ao oracledb. Corrige `UnicodeDecodeError` causado pelo
  "ç"/"ã" no path (`_Homologação`). O TASY exige Thick Mode (`DPY-3015` em thin).
- **`Pages/query.sql`** — Substituição de 16 subconsultas correlacionadas por CTEs com
  `ROW_NUMBER()`. A estrutura anterior executava ~2 subqueries por escala para *cada linha*
  do resultado (O(n × escalas)); agora cada escala é calculada uma única vez e filtrada
  pelo escopo do período/setor via `CTE_ATENDIMENTOS`. Impacto direto nos timeouts
  relatados em consultas com intervalos longos (ex.: 31 dias, setor 66).
- **`Pages/query.sql`** — `ORDER BY` externo agora usa o alias `SETOR` em vez de chamar
  `OBTER_DESC_SETOR_ATEND()` novamente durante a ordenação.
- **`Pages/Censo.py`** — TTL do cache de dados alterado de `0` (sem cache) para `300`
  segundos (5 minutos), alinhado com a tolerância de defasagem aceita pela operação.
- **`Pages/Censo.py`** — `carregar_setores()` adicionado `ttl=3600`; lista de setores
  raramente muda e não precisava ir ao banco a cada interação.

### Removido
- **`Pages/Censo.py`** — Bloco `split_and_assign` era código morto: a query retorna colunas
  separadas (`CD_MEWS`, `MEWS` etc.) e `RAW_MEWS` nunca existia no DataFrame.
- **`Pages/Censo.py`** — Cópia local de `dataframe_to_excel_bytes()` removida (duplicata
  da lógica centralizada em `utils.py`).
- **`utils.py`** — Variável global `_ORACLE_CLIENT_INITIALIZED` e função
  `initialize_oracle_client()` removidas; `@st.cache_resource` já garante execução única
  por processo, tornando a flag redundante.

### Adicionado
- **`utils.py`** — Função `export_to_excel(df, sheet_name)` centralizada e reutilizável;
  Censo agora importa esta função em vez de manter cópia própria (DRY).
- **`.streamlit/config.toml`** — Arquivo de configuração real criado (apenas o `.bak`
  existia). Define porta 8019, `headless=true` e coleta de telemetria desativada.
- **`tests/test_utils.py`** — Suite de testes Pytest cobrindo `export_to_excel` e
  `calcular_indicadores` com DataFrames sintéticos (sem dependência de banco).

### Alterado
- **`requirements.txt`** — Versões de todas as dependências fixadas para reprodutibilidade
  de ambiente (`streamlit==1.50.0`, `pandas==2.3.3`, `oracledb==3.4.2`,
  `SQLAlchemy==2.0.46`, `openpyxl==3.1.5`, `greenlet==3.0.3`).

---

## [0.2.0] — 2025-08-05  *(reconstituído do histórico git)*

### Adicionado
- Dashboard **Cirurgias Centro Cirúrgico** com tabela pivotada por caráter e porte.
- Exportação Excel formatada com MultiIndex de cabeçalho e célula de título mesclada.
- KPIs de resumo (total, eletivas, urgências/emergências).

### Corrigido
- Query do Censo otimizada para evitar `TRUNC()` em colunas indexadas (commits e39eeb7,
  ca924e0) após timeout identificado em busca de 31 dias.

---

## [0.1.0] — 2024-05-24  *(reconstituído do histórico git)*

### Adicionado
- Estrutura inicial do projeto com `Home.py` e `Pages/Censo.py`.
- Dashboard de Censo com 7 escalas clínicas: MEWS, BRADEN, MORSE, SAPS3, RASS,
  FUGULIN, GLASGOW e MARTINS.
- Exportação de dados em Excel via `openpyxl`.
- Script `hsf_painel_florence.bat` para inicialização no Windows.
