@echo off
title Sofia - Servidor Publico via ngrok
color 0D

echo.
echo ========================================
echo    INICIANDO SOFIA COM NGROK
echo ========================================
echo.

REM Matar processos antigos
taskkill /F /IM python.exe 2>nul
taskkill /F /IM ngrok.exe 2>nul
timeout /t 2 /nobreak >nul

REM Mudar para o diretorio do projeto
cd /d D:\A.I_GitHUB

REM Configurar variaveis de ambiente
set PYTHONPATH=D:\A.I_GitHUB
set SOFIA_USE_CLOUD=true
set GITHUB_TOKEN=ghp_REDACTED
set GITHUB_MODEL=gpt-4o

echo [1/3] Ambiente configurado (Cloud + GPT-4o)
timeout /t 2 /nobreak >nul

echo [2/3] Iniciando servidor Sofia na porta 8000...
start /B python -m uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000

REM Aguardar servidor iniciar
echo      Aguardando servidor iniciar...
timeout /t 10 /nobreak >nul

echo [3/3] Iniciando tunel ngrok...
start "ngrok - Sofia" ngrok http 8000

timeout /t 6 /nobreak >nul

echo.
echo ========================================
echo      SOFIA ESTA NO AR!
echo ========================================
echo.
echo Local: http://localhost:8000
echo Dashboard ngrok: http://localhost:4040
echo.
echo IMPORTANTE: Aguarde 5 segundos e acesse
echo o Dashboard para ver a URL publica!
echo.

REM Aguardar ngrok estabilizar
timeout /t 5 /nobreak >nul

echo Abrindo Dashboard ngrok...
start http://localhost:4040

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo.

REM Abrir janela para atualizar URL
echo Abrindo atualizador de URL...
start "Atualizador Ngrok" powershell -ExecutionPolicy Bypass -NoExit -File "D:\A.I_GitHUB\Atualizar_Ngrok.ps1"

echo.
echo ========================================
echo.
echo MANTENHA ESTA JANELA ABERTA!
echo.
echo Para parar Sofia:
echo  - Feche esta janela
echo  - Ou pressione Ctrl+C
echo.
echo ========================================
echo.

REM Loop infinito para manter janela aberta
:loop
timeout /t 10 /nobreak >nul
goto loop
