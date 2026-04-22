@echo off
title Painel HSF FLORENCE

:: Usa o executavel do venv diretamente para evitar problemas de encoding
:: com caracteres especiais no path (_Homologacao tem 'a' com til)
set "PROJ_DIR=%~dp0"
set "PYTHON=%~dp0venv\Scripts\python.exe"
set "STREAMLIT=%~dp0venv\Scripts\streamlit.exe"

echo Verificando ambiente...
if not exist "%PYTHON%" (
    echo ERRO: Ambiente virtual nao encontrado em %PROJ_DIR%venv
    echo Execute: python -m venv venv
    pause
    exit /b 1
)

echo Iniciando Painel HSF Florence na porta 8019...
echo Acesse: http://localhost:8019
echo Pressione Ctrl+C para encerrar.
echo.

"%PYTHON%" -m streamlit run "%~dp0Home.py" --server.port 8019
pause
