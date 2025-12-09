# Sofia - iniciar com ngrok (acesso publico)
# Sem emojis para evitar problemas de encoding no PowerShell 5

Write-Host "Iniciando Sofia com acesso publico via ngrok..." -ForegroundColor Cyan
Write-Host ""

# Verificar se ngrok está instalado
$ngrokCommand = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokCommand) {
    Write-Host "ngrok nao encontrado. Instale e configure o authtoken." -ForegroundColor Red
    exit 1
}

# Configurar variaveis de ambiente
$env:PYTHONPATH = "D:\A.I_GitHUB"
$env:SOFIA_AUTORIDADE_DECLARADA = "1"
$env:SOFIA_USE_CLOUD = "false"  # usar Ollama local
$env:GITHUB_TOKEN = ""          # não usado no modo local
$env:GITHUB_MODEL = ""          # não usado no modo local

Write-Host "Variaveis configuradas:" -ForegroundColor Green
Write-Host " PYTHONPATH = $env:PYTHONPATH"
Write-Host " SOFIA_USE_CLOUD = $env:SOFIA_USE_CLOUD"
Write-Host " OLLAMA_MODEL (definido no cerebro.py/.env)"
Write-Host ""

# Python executavel
$pythonExe = "D:\A.I_GitHUB\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Python nao encontrado em $pythonExe" -ForegroundColor Red
    exit 1
}
Write-Host "Python encontrado: $pythonExe" -ForegroundColor Green

# Iniciar servidor (nova janela powershell para preservar env)
Set-Location "D:\A.I_GitHUB"
$serverProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:GITHUB_TOKEN='$env:GITHUB_TOKEN'; `$env:GITHUB_MODEL='$env:GITHUB_MODEL'; `$env:SOFIA_USE_CLOUD='$env:SOFIA_USE_CLOUD'; `$env:PYTHONPATH='$env:PYTHONPATH'; Set-Location 'D:\A.I_GitHUB'; & '$pythonExe' -m uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000"
) -PassThru
Write-Host "Servidor iniciado. PID=$($serverProcess.Id)" -ForegroundColor Green
Write-Host "Aguardando servidor subir..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Verificar health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "Servidor responde em /api/health" -ForegroundColor Green
} catch {
    Write-Host "Servidor ainda inicializando (health falhou)." -ForegroundColor Yellow
}

# Iniciar ngrok
Write-Host "Iniciando ngrok..." -ForegroundColor Cyan
Start-Process -FilePath "ngrok" -ArgumentList "http", "8000"
Start-Sleep -Seconds 5

# Obter URL ngrok
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels"
    $publicUrl = $ngrokApi.tunnels[0].public_url
    Write-Host "URL publica: $publicUrl" -ForegroundColor Green
    Write-Host "Dashboard ngrok: http://localhost:4040" -ForegroundColor Green
    Start-Process "http://localhost:4040"
} catch {
    Write-Host "Nao foi possivel obter URL do ngrok; acesse http://localhost:4040" -ForegroundColor Yellow
}

Write-Host "Servidores rodando. Feche esta janela para encerrar." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "Encerrando servidores..." -ForegroundColor Yellow
Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
Write-Host "Finalizado." -ForegroundColor Green
