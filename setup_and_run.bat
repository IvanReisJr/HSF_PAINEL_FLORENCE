@echo on
TITLE HSF PAINEL FLORENCE - Diagnostico de Inicializacao
SET PORT=8019

echo [1/4] Acessando pasta...
cd /d "%~dp0"
echo Pasta atual: %CD%

echo [2/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O comando 'python' nao foi encontrado neste servidor.
    echo Certifique-se de que o Python esta instalado e a opcao 'Add Python to PATH' foi marcada.
    pause
    exit /b
)

echo [3/4] Preparando Ambiente Virtual...
if not exist "venv" (
    python -m venv venv
)

echo [4/4] Instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [SUCESSO] Iniciando Streamlit...
python -m streamlit run Home.py --server.port %PORT% --server.address 0.0.0.0

pause
