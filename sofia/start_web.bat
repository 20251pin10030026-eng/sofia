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

REM Inicia o servidor
echo Servidor iniciando em http://localhost:5000
echo Abra web/index.html no seu navegador
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python api.py

pause
