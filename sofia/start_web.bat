@echo off
echo ================================================
echo    Sofia - Interface Web
echo    Iniciando servidor...
echo ================================================
echo.

REM Navega para o diretório do script
cd /d "%~dp0"

REM Ativa o ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Configura variáveis de ambiente da Sofia
set SOFIA_MODO_WEB=1
set SOFIA_AUTORIDADE_DECLARADA=1

REM Inicia o servidor FastAPI/WebSocket
echo Servidor iniciando em http://localhost:8000
echo Acesse a interface web da Sofia no navegador.
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python api_web.py

pause
