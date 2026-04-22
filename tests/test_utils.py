"""Testes unitários para utils.py — HSF Painel Florence.

Execução:
    cd HSF_PAINEL_FLORENCE
    pytest tests/ -v

Estratégia de isolamento: utils.py é importado com mock de streamlit e oracledb,
que são dependências de runtime não disponíveis fora do ambiente Streamlit.
"""

import io
import sys
import unittest.mock as mock

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixture: mock de streamlit/oracledb antes de qualquer import de utils
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="module")
def mock_dependencies():
    """Injeta mocks de streamlit e oracledb no sys.modules antes dos testes."""
    st_mock = mock.MagicMock()
    # cache_resource deve retornar um decorador que repassa a função original
    st_mock.cache_resource = lambda func: func

    sys.modules["streamlit"] = st_mock
    sys.modules["oracledb"] = mock.MagicMock()

    yield

    # Limpeza: remove os mocks para não contaminar outros módulos
    sys.modules.pop("streamlit", None)
    sys.modules.pop("oracledb", None)
    sys.modules.pop("utils", None)


def _import_utils():
    """Importa utils após injetar mocks (evita cache de import entre testes)."""
    sys.modules.pop("utils", None)
    import importlib
    return importlib.import_module("utils")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _df_simples() -> pd.DataFrame:
    return pd.DataFrame(
        {"PACIENTE": ["Ana", "Bruno"], "LEITO": ["101A", "102B"], "MEWS": [2, 7]}
    )


def _df_censo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "NR_ATENDIMENTO": [1, 2, 3],
            "CD_MEWS":    [2,    None, 8],
            "MEWS":       ["BAIXO", None, "ALTO"],
            "CD_BRADEN":  [18,   12,   None],
            "BRADEN":     ["Leve", "Alto", None],
            "CD_MORSE":   [25,   None, 50],
            "MORSE":      ["Baixo", None, "Alto"],
            "CD_SAPSIII": [None, None, None],
            "SAP3":       [None, None, None],
            "CD_RASS":    [0,    -1,   None],
            "RASS":       ["Acordado", "Sonolento", None],
            "CD_FUGULIN": ["CM", "AD", None],
            "FUGULIN":    ["Cuidados Mínimos", "Alta Dependência", None],
            "MARTINS":    [None, None, None],
            "CD_GLASGOW": [15,   14,   None],
            "GLASGOW":    ["Normal", "Normal", None],
        }
    )


# ---------------------------------------------------------------------------
# Testes: export_to_excel
# ---------------------------------------------------------------------------

class TestExportToExcel:

    def test_retorna_bytes(self):
        utils = _import_utils()
        resultado = utils.export_to_excel(_df_simples())
        assert isinstance(resultado, bytes)

    def test_bytes_nao_vazios(self):
        utils = _import_utils()
        resultado = utils.export_to_excel(_df_simples())
        assert len(resultado) > 0

    def test_excel_legivel_pelo_pandas(self):
        utils = _import_utils()
        df = _df_simples()
        resultado = utils.export_to_excel(df, sheet_name="Teste")
        df_lido = pd.read_excel(io.BytesIO(resultado), sheet_name="Teste")
        assert list(df_lido.columns) == list(df.columns)
        assert len(df_lido) == len(df)

    def test_sheet_name_customizado(self):
        utils = _import_utils()
        resultado = utils.export_to_excel(_df_simples(), sheet_name="MinhaPlanilha")
        df_lido = pd.read_excel(io.BytesIO(resultado), sheet_name="MinhaPlanilha")
        assert not df_lido.empty

    def test_dataframe_vazio(self):
        utils = _import_utils()
        df = pd.DataFrame(columns=["A", "B"])
        resultado = utils.export_to_excel(df)
        assert isinstance(resultado, bytes)
        df_lido = pd.read_excel(io.BytesIO(resultado))
        assert list(df_lido.columns) == ["A", "B"]
        assert len(df_lido) == 0


# ---------------------------------------------------------------------------
# Testes: calcular_indicadores
# ---------------------------------------------------------------------------

class TestCalcularIndicadores:

    def test_total_atendimentos(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        assert ind["total_atendimentos"] == 3

    def test_total_mews_classificado(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        assert ind["total_mews"] == 2  # 2 linhas com CD_MEWS não nulo

    def test_sem_classificacao_mews(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        assert ind["sem_classificacao_mews"] == 1

    def test_sem_classificacao_saps3_todos(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        assert ind["sem_classificacao_saps3"] == 3  # todos None

    def test_contagem_mews_retorna_dataframe(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        df_cont = ind["contagem_mews"]
        assert isinstance(df_cont, pd.DataFrame)
        assert "Descrição" in df_cont.columns
        assert "Qtde" in df_cont.columns

    def test_contagem_mews_valores_corretos(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        df_cont = ind["contagem_mews"]
        total = df_cont["Qtde"].sum()
        assert total == 2  # BAIXO=1, ALTO=1

    def test_total_glasgow(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        assert ind["total_glasgow"] == 2

    def test_martins_sem_dados(self):
        utils = _import_utils()
        ind = utils.calcular_indicadores(_df_censo())
        assert ind["total_martins"] == 0
        assert ind["sem_classificacao_martins"] == 3
