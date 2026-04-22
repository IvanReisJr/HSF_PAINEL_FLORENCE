"""
Script de diagnostico: testa conexao Oracle (thick mode via add_dll_directory) e nova query CTE.
Execucao (a partir da raiz do projeto):
    venv\\Scripts\\python.exe scratch\\test_connection.py
"""

import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import oracledb  # noqa: E402

DSN  = "192.168.5.9:1521/TASYPRD"
USER = "TASY"
PASS = "aloisk"

IC_REL = ".\\instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6"
IC_ABS = os.path.abspath(IC_REL)

# ─── 1. Oracle Client (Thick Mode via add_dll_directory) ─────────────────────
print("\n[1/4] Inicializando Oracle Client (Thick Mode)...")

if not os.path.exists(IC_ABS):
    print(f"   AVISO: Instant Client nao encontrado em: {IC_REL}")
    print("   Tentando Thin Mode (pode falhar com autenticacao antiga)...")
    init_ok = False
else:
    print(f"   Instant Client encontrado.")
    print(f"   Usando os.add_dll_directory() para contornar encoding do path.")
    init_ok = False
    try:
        with os.add_dll_directory(IC_ABS):
            oracledb.init_oracle_client()
        print("   Oracle Client inicializado via add_dll_directory — SUCESSO.")
        init_ok = True
    except Exception as e:
        msg = str(e)
        if any(c in msg for c in ("DPY-2016", "DPY-2017", "already")):
            print(f"   Oracle Client ja inicializado (ok).")
            init_ok = True
        else:
            print(f"   add_dll_directory falhou: {e}")
            print("   Tentando lib_dir convencional...")
            try:
                oracledb.init_oracle_client(lib_dir=IC_REL)
                print("   Oracle Client inicializado via lib_dir — SUCESSO.")
                init_ok = True
            except Exception as e2:
                if any(c in str(e2) for c in ("DPY-2016", "DPY-2017", "already")):
                    print("   Oracle Client ja inicializado (ok).")
                    init_ok = True
                else:
                    print(f"   lib_dir tambem falhou: {e2}")

if not init_ok:
    print("   FALHA: nao foi possivel inicializar Oracle Client em Thick Mode.")
    print("   Abortando — servidor requer Thick Mode (DPY-3015).")
    sys.exit(1)

# ─── 2. Conexao ──────────────────────────────────────────────────────────────
print(f"\n[2/4] Conectando ao Oracle TASY ({DSN})...")
try:
    conn = oracledb.connect(user=USER, password=PASS, dsn=DSN)
    print("   Conexao estabelecida com SUCESSO.")
except Exception as e:
    print(f"   ERRO ao conectar: {e}")
    sys.exit(1)

# ─── 3. SELECT basico ────────────────────────────────────────────────────────
print("\n[3/4] SELECT 1 FROM DUAL...")
try:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM DUAL")
    val = cur.fetchone()[0]
    cur.close()
    print(f"   Resultado: {val} — banco respondendo normalmente.")
except Exception as e:
    print(f"   ERRO: {e}")
    conn.close()
    sys.exit(1)

# ─── 4. Nova query CTE ───────────────────────────────────────────────────────
hoje = datetime.date.today().strftime("%d/%m/%Y")
print(f"\n[4/4] Testando nova query CTE (Pages/query.sql) — data: {hoje}, todos setores...")

query_path = os.path.join(ROOT, "Pages", "query.sql")
try:
    with open(query_path, "r", encoding="utf-8") as f:
        query = f.read()
except Exception as e:
    print(f"   ERRO ao ler query.sql: {e}")
    conn.close()
    sys.exit(1)

query = query.replace("/*{{FILTER_SETOR}}*/", "")

try:
    cur = conn.cursor()
    cur.execute(query, DATA_INICIAL=hoje, DATA_FINAL=hoje)

    colunas = [c[0] for c in cur.description]
    linhas  = cur.fetchmany(5)
    cur.close()

    print(f"   Query CTE executou com SUCESSO.")
    print(f"   Colunas ({len(colunas)}): {', '.join(colunas)}")
    print(f"   Linhas retornadas (primeiras 5): {len(linhas)}")

    if linhas:
        print("\n   Amostra — 1a linha:")
        for col, val in zip(colunas, linhas[0]):
            print(f"     {col:<22} = {val}")
    else:
        print("   (Resultado vazio — nenhuma ocupacao ativa hoje.)")

except Exception as e:
    print(f"\n   ERRO na query CTE: {e}")
    print("\n   Primeiras 50 linhas da query:")
    for i, line in enumerate(query.split("\n")[:50], 1):
        print(f"   {i:3d} | {line}")
    conn.close()
    sys.exit(1)

conn.close()
print("\n=== Todos os testes de integracao passaram. ===\n")
