@echo off
title Pedra Papel e Tesoura - BACKUP
cd /d "%~dp0"

echo ==================================================
echo   VERSAO BACKUP
echo   Cria um ambiente proprio (.venv) para o jogo e
echo   abre o navegador pelo proprio Windows.
echo ==================================================
echo.

if not exist "app.py" (
    echo [ERRO] Nao encontrei o arquivo app.py.
    echo Extraia a pasta inteira do ZIP antes de abrir este arquivo.
    echo.
    pause
    exit /b 1
)

set "PY="

py -3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
    goto CRIAR
)

python --version >nul 2>nul
if not errorlevel 1 (
    set "PY=python"
    goto CRIAR
)

python3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY=python3"
    goto CRIAR
)

echo [ERRO] O Python nao foi encontrado.
echo Instale em https://www.python.org/downloads/ marcando "Add Python to PATH".
echo.
pause
exit /b 1

:CRIAR
if exist ".venv\Scripts\python.exe" goto INSTALAR
echo Criando ambiente virtual, aguarde...
%PY% -m venv .venv
if errorlevel 1 goto ERRO

:INSTALAR
echo Instalando o Flask (so demora na primeira vez)...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto ERRO

echo.
echo Abrindo o jogo em instantes: http://127.0.0.1:5000
echo Para encerrar, feche esta janela.
echo.

rem espera 4 segundos e abre o navegador pelo Windows
start "" cmd /c "ping -n 5 127.0.0.1 >nul & start http://127.0.0.1:5000"

".venv\Scripts\python.exe" app.py
echo.
pause
exit /b

:ERRO
echo.
echo [ERRO] Algo deu errado. Leia a mensagem acima.
echo Se a porta 5000 estiver ocupada, feche outros programas e tente de novo.
echo.
pause
exit /b 1
