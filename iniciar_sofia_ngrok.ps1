# 🌸 Sofia - Iniciar com ngrok (Acesso Público)

Write-Host "🌸 Iniciando Sofia com acesso público via ngrok..." -ForegroundColor Cyan
Write-Host ""

# Configurar variáveis de ambiente  
$env:PYTHONPATH = "D:\A.I_GitHUB"
$env:SOFIA_AUTORIDADE_DECLARADA = "1"
$env:SOFIA_USE_CLOUD = "true"
$env:GITHUB_TOKEN = "ghp_REDACTED"
$env:GITHUB_MODEL = "gpt-4o"

Write-Host "✅ Variáveis configuradas (Cloud + GPT-4o)" -ForegroundColor Green
Write-Host ""

# Verificar dependências Python
Write-Host "📚 Verificando dependências Python..." -ForegroundColor Cyan
$pythonExe = "D:\A.I_GitHUB\.venv\Scripts\python.exe"

# Verificar PyPDF2
$pypdfCheck = & $pythonExe -c "import PyPDF2; print(f'PyPDF2 {PyPDF2.__version__}')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ $pypdfCheck" -ForegroundColor Green
} else {
    Write-Host "   ❌ PyPDF2 não encontrado. Instalando..." -ForegroundColor Yellow
    & $pythonExe -m pip install PyPDF2
    Write-Host "   ✅ PyPDF2 instalado!" -ForegroundColor Green
}
Write-Host ""

# Iniciar servidor Sofia
Write-Host "🚀 Iniciando servidor Sofia..." -ForegroundColor Cyan
Set-Location -Path "D:\A.I_GitHUB\sofia"
$sofiaProcess = Start-Process $pythonExe -ArgumentList "-m", "uvicorn", "api_web:app", "--host", "0.0.0.0", "--port", "8000" -NoNewWindow -PassThru
Set-Location -Path "D:\A.I_GitHUB"
Start-Sleep -Seconds 8

# Verificar servidor
try {
    Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing | Out-Null
    Write-Host "✅ Sofia rodando!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao iniciar Sofia" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🌐 Criando túnel ngrok..." -ForegroundColor Cyan
Start-Process ngrok -ArgumentList "http", "8000" -NoNewWindow
Start-Sleep -Seconds 4

# Obter URL
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels"
    $publicUrl = $ngrokApi.tunnels[0].public_url
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
    Write-Host "✅ SOFIA ESTÁ NO AR!" -ForegroundColor Green  
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URL Pública:" -ForegroundColor Cyan
    Write-Host "   $publicUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🏠 URL Local:" -ForegroundColor Cyan
    Write-Host "   http://localhost:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📊 Dashboard: http://localhost:4040" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 A URL pública funciona em QUALQUER LUGAR!" -ForegroundColor Yellow
    Write-Host "   Compartilhe com quem quiser 🌍" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "⚠️ Veja URL em: http://localhost:4040" -ForegroundColor Yellow
}

Write-Host "⏳ Servidores ativos (Ctrl+C para parar)..." -ForegroundColor Gray
Write-Host ""

# Loop
try {
    while ($true) {
        Start-Sleep -Seconds 10
        try {
            Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -UseBasicParsing | Out-Null
        } catch {
            Write-Host "❌ Sofia parou" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Encerrando..." -ForegroundColor Yellow
    Stop-Process -Id $sofiaProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Encerrado" -ForegroundColor Green
}
    Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Encerrado" -ForegroundColor Green
}
