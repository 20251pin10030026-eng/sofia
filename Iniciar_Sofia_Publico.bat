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

REM Mudar para o diretorio do projeto
cd /d D:\A.I_GitHUB

REM Configurar variaveis de ambiente
set PYTHONPATH=D:\A.I_GitHUB
set SOFIA_AUTORIDADE_DECLARADA=1

REM Forcar modo CLOUD (GitHub Models)
set SOFIA_USE_CLOUD=true
set GITHUB_MODEL=gpt-4o
REM GITHUB_TOKEN deve ficar fora do repositório.
REM Opcional: salve o token em %USERPROFILE%\.sofia_token (1ª linha) ou defina antes de rodar.

REM Carregar token de arquivo seguro, se não estiver definido
if not defined GITHUB_TOKEN (
    if exist "%USERPROFILE%\.sofia_token" (
        for /f "usebackq delims=" %%A in ("%USERPROFILE%\.sofia_token") do (
            if not defined GITHUB_TOKEN set "GITHUB_TOKEN=%%A"
        )
    )
)

REM Validar se o token está presente
if not defined GITHUB_TOKEN (
    echo ERRO: GITHUB_TOKEN não definido. Crie %USERPROFILE%\.sofia_token com o token ou exporte antes de rodar.
    pause
    exit /b 1
)

echo [1/4] Ambiente configurado (Cloud + GitHub Models)
timeout /t 1 /nobreak >nul

echo [2/4] Instalando/Verificando PyPDF2...
D:\A.I_GitHUB\.venv\Scripts\python.exe -m pip install --quiet --upgrade PyPDF2
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar PyPDF2
    pause
    exit /b 1
)
echo      PyPDF2 instalado com sucesso!
timeout /t 1 /nobreak >nul

echo [3/4] Iniciando servidor Sofia na porta 8000...
start /B D:\A.I_GitHUB\.venv\Scripts\python.exe -m uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000

REM Aguardar servidor iniciar
echo      Aguardando servidor iniciar...
timeout /t 10 /nobreak >nul

echo [4/4] Iniciando tunel ngrok...
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
