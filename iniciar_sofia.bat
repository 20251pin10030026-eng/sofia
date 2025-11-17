@echo off
REM ============================================================
REM SOFIA - Inicializador Completo (Web + API + ngrok)
REM ============================================================

cd /d "%~dp0"

echo.
echo ========================================
echo   SOFIA - ASSISTENTE VIRTUAL
echo ========================================
echo.
echo Inicializando componentes...
echo.

REM Verificar se esta no diretorio correto
if not exist "sofia" (
    echo ERRO: Diretorio sofia nao encontrado!
    pause
    exit /b 1
)

REM ============================================================
REM 1. INICIAR SOFIA API
REM ============================================================
echo [1/3] Iniciando Sofia API...

start "SOFIA API - Processamento Local" powershell -NoExit -Command ^
    "Write-Host ''; ^
     Write-Host '========================================' -ForegroundColor Cyan; ^
     Write-Host '  SOFIA API - Processamento Local' -ForegroundColor Cyan; ^
     Write-Host '========================================' -ForegroundColor Cyan; ^
     Write-Host ''; ^
     Write-Host 'Ativando ambiente Python...' -ForegroundColor Yellow; ^
     cd '%~dp0'; ^
     if (Test-Path '.venv\Scripts\Activate.ps1') { ^
         & .venv\Scripts\Activate.ps1; ^
         Write-Host 'OK - Ambiente ativado' -ForegroundColor Green; ^
     } else { ^
         Write-Host 'ERRO: Virtual environment nao encontrado' -ForegroundColor Red; ^
         Write-Host 'Execute: python -m venv .venv' -ForegroundColor Yellow; ^
         pause; ^
         exit; ^
     }; ^
     Write-Host ''; ^
     Write-Host 'Iniciando servidor Flask...' -ForegroundColor Yellow; ^
     Write-Host 'Porta: 5000' -ForegroundColor Gray; ^
     Write-Host 'Modelo: GitHub Models (GPT-4o)' -ForegroundColor Gray; ^
     Write-Host ''; ^
     Write-Host 'Pressione Ctrl+C para parar' -ForegroundColor Red; ^
     Write-Host ''; ^
     cd sofia; ^
     python sofia/api.py"

REM Aguardar Sofia iniciar
echo Aguardando Sofia iniciar (8 segundos)...
timeout /t 8 /nobreak >nul

REM ============================================================
REM 2. INICIAR NGROK
REM ============================================================
echo [2/3] Iniciando ngrok...

REM Verificar se ngrok esta instalado
where ngrok >nul 2>&1
if errorlevel 1 (
    echo AVISO: ngrok nao encontrado!
    echo.
    echo Para instalar ngrok:
    echo   1. Baixe em: https://ngrok.com/download
    echo   2. Crie conta em: https://dashboard.ngrok.com/signup
    echo   3. Execute: ngrok config add-authtoken SEU_TOKEN
    echo.
    echo Pressione qualquer tecla para continuar sem ngrok...
    pause >nul
    goto :abrir_site
)

start "NGROK - Tunel Publico" powershell -NoExit -Command ^
    "Write-Host ''; ^
     Write-Host '========================================' -ForegroundColor Cyan; ^
     Write-Host '  NGROK - Tunel Publico' -ForegroundColor Cyan; ^
     Write-Host '========================================' -ForegroundColor Cyan; ^
     Write-Host ''; ^
     Write-Host 'IMPORTANTE: Copie a URL do Forwarding!' -ForegroundColor Yellow; ^
     Write-Host 'Exemplo: https://abc123.ngrok-free.app' -ForegroundColor Gray; ^
     Write-Host ''; ^
     Write-Host 'Se a URL mudou, execute:' -ForegroundColor Yellow; ^
     Write-Host '  atualizar_ngrok_url.ps1' -ForegroundColor Cyan; ^
     Write-Host ''; ^
     Write-Host 'Pressione Ctrl+C para parar' -ForegroundColor Red; ^
     Write-Host ''; ^
     ngrok http 5000"

REM Aguardar ngrok iniciar
echo Aguardando ngrok iniciar (5 segundos)...
timeout /t 5 /nobreak >nul

REM ============================================================
REM 3. ABRIR SITE NO NAVEGADOR
REM ============================================================
:abrir_site
echo [3/3] Abrindo site no navegador...
timeout /t 2 /nobreak >nul

start http://52.226.167.30

echo.
echo ========================================
echo   SOFIA INICIADA COM SUCESSO!
echo ========================================
echo.
echo Componentes ativos:
echo   [X] Sofia API (porta 5000)
echo   [X] ngrok (tunel publico)
echo   [X] Site (http://52.226.167.30)
echo.
echo Arquitetura:
echo   - Site: VM Azure (nginx)
echo   - Processamento: Seu PC (GPT-4o)
echo   - Conexao: ngrok
echo.
echo Proximos passos:
echo   1. Copie a URL do ngrok no terminal dele
echo   2. Se for primeira vez ou URL mudou:
echo      Execute: atualizar_ngrok_url.ps1
echo   3. Converse com Sofia no site!
echo.
echo Para parar:
echo   - Feche os terminais da Sofia e ngrok
echo.

pause

