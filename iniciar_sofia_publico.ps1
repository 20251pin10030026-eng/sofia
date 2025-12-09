# 🌸 Sofia - Iniciar com ngrok (Acesso Público)
# Este script inicia a Sofia localmente e cria um túnel público via ngrok

Write-Host "🌸 Iniciando Sofia com acesso público via ngrok..." -ForegroundColor Cyan
Write-Host ""

# Verificar se ngrok está instalado
$ngrokCommand = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokCommand) {
    Write-Host "❌ ngrok não encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Baixe ngrok em: https://ngrok.com/download"
    Write-Host "2. Configure o authtoken"
    Write-Host ""
    exit 1
}

# Configurar variáveis de ambiente
$env:PYTHONPATH = "D:\A.I_GitHUB"
$env:SOFIA_AUTORIDADE_DECLARADA = "1"
$env:SOFIA_USE_CLOUD = "true"
$env:GITHUB_TOKEN = "ghp_REDACTED"
$env:GITHUB_MODEL = "gpt-4o"

Write-Host "✅ Variáveis de ambiente configuradas" -ForegroundColor Green
Write-Host "   - PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "   - Modo: Cloud (GitHub Models)" -ForegroundColor Gray
Write-Host "   - Modelo: GPT-4o" -ForegroundColor Gray
Write-Host "   - Token: $($env:GITHUB_TOKEN.Substring(0,10))..." -ForegroundColor Gray
Write-Host ""

# Python executável
$pythonExe = "D:\A.I_GitHUB\.venv\Scripts\python.exe"

# Verificar se o Python existe
if (-not (Test-Path $pythonExe)) {
    Write-Host "   ❌ Python não encontrado em: $pythonExe" -ForegroundColor Red
    Write-Host "   Configure o ambiente virtual primeiro!" -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✅ Python encontrado: $pythonExe" -ForegroundColor Green
Write-Host ""

# Iniciar servidor Sofia em background
Write-Host "🚀 Iniciando servidor Sofia..." -ForegroundColor Cyan
Set-Location -Path "D:\A.I_GitHUB"

# Iniciar processo em nova janela que mantém as variáveis
$serverProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:GITHUB_TOKEN='$env:GITHUB_TOKEN'; `$env:GITHUB_MODEL='$env:GITHUB_MODEL'; `$env:SOFIA_USE_CLOUD='$env:SOFIA_USE_CLOUD'; `$env:PYTHONPATH='$env:PYTHONPATH'; Set-Location 'D:\A.I_GitHUB'; & '$pythonExe' -m uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000"
) -PassThru

Write-Host "   ✅ Servidor iniciado (PID: $($serverProcess.Id))" -ForegroundColor Green
Write-Host "   ⏳ Aguardando servidor inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Verificar se servidor iniciou
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Servidor Sofia respondendo!" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Servidor ainda inicializando... (normal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 Criando túnel público com ngrok..." -ForegroundColor Cyan
Write-Host ""

# Iniciar ngrok
Start-Process -FilePath "ngrok" -ArgumentList "http", "8000"

# Aguardar ngrok iniciar
Start-Sleep -Seconds 5

# Obter URL pública
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels"
    $publicUrl = $ngrokApi.tunnels[0].public_url
    
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "✅ SOFIA ESTÁ NO AR!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URL Pública (compartilhe com quem quiser):" -ForegroundColor Cyan
    Write-Host "   $publicUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🏠 URL Local (só você):" -ForegroundColor Cyan
    Write-Host "   http://localhost:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Dicas:" -ForegroundColor Cyan
    Write-Host "   - A URL pública funciona em qualquer lugar do mundo"
    Write-Host "   - Válida enquanto os servidores estiverem rodando"
    Write-Host "   - Para parar: feche as janelas do servidor e ngrok"
    Write-Host ""
    Write-Host "📊 Dashboard ngrok: http://localhost:4040" -ForegroundColor Cyan
    Write-Host ""
    
    # Abrir dashboard ngrok
    Start-Process "http://localhost:4040"
    
} catch {
    Write-Host "⚠️ Não foi possível obter URL do ngrok automaticamente" -ForegroundColor Yellow
    Write-Host "   Acesse: http://localhost:4040 para ver a URL pública" -ForegroundColor Yellow
}

Write-Host "⏳ Servidores rodando... Feche esta janela quando quiser parar." -ForegroundColor Gray
Write-Host ""
Write-Host "Pressione qualquer tecla para encerrar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Parar processos
Write-Host ""
Write-Host "🛑 Encerrando servidores..." -ForegroundColor Yellow
Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
Write-Host "✅ Servidores encerrados" -ForegroundColor Green
