@echo off
title Pedra Papel e Tesoura
cd /d "%~dp0"

if not exist "index.py" (
    echo [ERRO] Nao encontrei o arquivo index.py.
    echo Extraia a pasta inteira do ZIP antes de abrir este arquivo.
    echo.
    pause
    exit /b 1
)

set "PY="

py -3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
    goto RODAR
)

python --version >nul 2>nul
if not errorlevel 1 (
    set "PY=python"
    goto RODAR
)

python3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY=python3"
    goto RODAR
)

goto SEM_PYTHON

:RODAR
echo Usando: %PY%
echo.
%PY% index.py
if errorlevel 1 (
    echo.
    echo [ERRO] O jogo fechou com erro. Leia a mensagem acima.
    echo Se nao resolver, use o arquivo INICIAR_BACKUP.bat
)
echo.
pause
exit /b

:SEM_PYTHON
echo [ERRO] O Python nao foi encontrado neste computador.
echo.
echo 1. Instale o Python: https://www.python.org/downloads/
echo 2. Na instalacao, MARQUE a opcao "Add Python to PATH"
echo 3. Depois abra este arquivo de novo
echo.
start "" https://www.python.org/downloads/
pause
exit /b 1
