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
Write-Host ""

# Verificar dependências Python
Write-Host "📚 Verificando e instalando dependências Python..." -ForegroundColor Cyan
$pythonExe = "D:\A.I_GitHUB\.venv\Scripts\python.exe"

# Verificar se o Python existe
if (-not (Test-Path $pythonExe)) {
    Write-Host "   ❌ Python não encontrado em: $pythonExe" -ForegroundColor Red
    Write-Host "   Configure o ambiente virtual primeiro!" -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✅ Python encontrado: $pythonExe" -ForegroundColor Green

# FORÇAR instalação do PyPDF2 no Python correto
Write-Host "   📦 Instalando PyPDF2 no ambiente correto..." -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade --quiet PyPDF2 2>&1 | Out-Null

# Verificar se instalou com sucesso
$pypdfCheck = & $pythonExe -c "import PyPDF2; print(f'PyPDF2 {PyPDF2.__version__}')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ $pypdfCheck instalado e verificado!" -ForegroundColor Green
} else {
    Write-Host "   ❌ ERRO: Não foi possível instalar/importar PyPDF2" -ForegroundColor Red
    Write-Host "   Saída do erro: $pypdfCheck" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Tente manualmente:" -ForegroundColor Yellow
    Write-Host "   $pythonExe -m pip install PyPDF2" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# FORÇAR instalação do duckduckgo-search no Python correto
Write-Host "   🌐 Instalando duckduckgo-search no ambiente correto..." -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade --quiet duckduckgo-search 2>&1 | Out-Null

# Verificar se instalou com sucesso
$ddgCheck = & $pythonExe -c "from duckduckgo_search import DDGS; print('duckduckgo-search OK')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ $ddgCheck instalado e verificado!" -ForegroundColor Green
} else {
    Write-Host "   ❌ ERRO: Não foi possível instalar/importar duckduckgo-search" -ForegroundColor Red
    Write-Host "   Saída do erro: $ddgCheck" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Tente manualmente:" -ForegroundColor Yellow
    Write-Host "   $pythonExe -m pip install duckduckgo-search" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# Iniciar servidor Sofia em background
Write-Host "🚀 Iniciando servidor Sofia..." -ForegroundColor Cyan
Write-Host "   Python: $pythonExe" -ForegroundColor Gray
Set-Location -Path "D:\A.I_GitHUB\sofia"

# Usar o mesmo Python que verificamos e instalamos PyPDF2
$sofiaProcess = Start-Process -FilePath $pythonExe -ArgumentList "api_web.py" -NoNewWindow -PassThru
Start-Sleep -Seconds 8

# Voltar para a raiz
Set-Location -Path "D:\A.I_GitHUB"

# Verificar se servidor iniciou
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Servidor Sofia iniciado!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao iniciar servidor Sofia" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🌐 Criando túnel público com ngrok..." -ForegroundColor Cyan
Write-Host ""

# Iniciar ngrok em background
Start-Process -FilePath "ngrok" -ArgumentList "http 8000" -NoNewWindow

# Aguardar ngrok iniciar
Start-Sleep -Seconds 3

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
    Write-Host "   - Válida enquanto este script estiver rodando"
    Write-Host "   - Pressione Ctrl+C para parar"
    Write-Host ""
    Write-Host "📊 Dashboard ngrok: http://localhost:4040" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "⚠️ Não foi possível obter URL do ngrok automaticamente" -ForegroundColor Yellow
    Write-Host "   Acesse: http://localhost:4040 para ver a URL pública" -ForegroundColor Yellow
}

Write-Host "⏳ Mantendo servidores ativos... (Ctrl+C para parar)" -ForegroundColor Gray
Write-Host ""

# Manter script rodando
try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Verificar se servidor ainda está ativo
        try {
            Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -UseBasicParsing | Out-Null
        } catch {
            Write-Host "❌ Servidor Sofia parou inesperadamente" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Encerrando servidores..." -ForegroundColor Yellow
    
    # Parar processos
    Stop-Process -Id $sofiaProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ Servidores encerrados" -ForegroundColor Green
}
