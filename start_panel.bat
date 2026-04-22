@echo off
TITLE Painel HSF FLORENCE - Servidor
SET PORT=8019

echo ==========================================
echo    INICIANDO PAINEL HSF FLORENCE
echo ==========================================
echo Diretorio Atual: %~dp0
cd /d "%~dp0"

echo.
echo Verificando instalacao do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do Sistema.
    echo Por favor, instale o Python no servidor ou adicione-o as Variaveis de Ambiente.
    pause
    exit /b
)

echo Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo Iniciando Painel na porta %PORT%...
echo Acesse no navegador: http://localhost:%PORT%
echo.

python -m streamlit run Home.py --server.port %PORT% --server.address 0.0.0.0

pause
