# 🌸 Sofia - Iniciar com ngrok (Duplo Clique)# ========================================

# Este script inicia o servidor Sofia e o túnel ngrok automaticamente# 🌸 Sofia - Iniciador da API Web (PowerShell)

# ========================================

$Host.UI.RawUI.WindowTitle = "🌸 Sofia - Servidor Público"

$Host.UI.RawUI.BackgroundColor = "DarkBlue"# Ir para o diretório do script

$Host.UI.RawUI.ForegroundColor = "White"Set-Location $PSScriptRoot

Clear-Host

Write-Host ""

Write-Host ""Write-Host "========================================"

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor CyanWrite-Host "🌸 SOFIA - INICIANDO API WEB"

Write-Host "           🌸 INICIANDO SOFIA COM NGROK 🌸            " -ForegroundColor MagentaWrite-Host "========================================"

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor CyanWrite-Host ""

Write-Host ""

# Ativar ambiente virtual se existir

# Configurar variáveis de ambienteif (Test-Path ".venv\Scripts\Activate.ps1") {

$env:PYTHONPATH = "D:\A.I_GitHUB"    Write-Host "🔧 Ativando ambiente virtual..."

$env:SOFIA_USE_CLOUD = "true"    & .venv\Scripts\Activate.ps1

$env:GITHUB_TOKEN = "ghp_REDACTED"}

$env:GITHUB_MODEL = "gpt-4o"

# Executar script Python

Write-Host "[1/4] ✅ Ambiente configurado (Cloud Mode + GPT-4o)" -ForegroundColor Greenpython iniciar_sofia.py

Start-Sleep -Seconds 2

# Pausar no final (opcional)

# Mudar para diretório do projeto# Read-Host -Prompt "Pressione Enter para sair"

Set-Location "D:\A.I_GitHUB"

Write-Host "[2/4] 🚀 Iniciando servidor Sofia na porta 8000..." -ForegroundColor Yellow
$sofiaProcess = Start-Process python -ArgumentList "-m", "uvicorn", "sofia.api_web:app", "--host", "0.0.0.0", "--port", "8000" -NoNewWindow -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 8

# Verificar se servidor iniciou
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "      ✅ Sofia online!" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Erro ao iniciar Sofia" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "[3/4] 🌐 Criando túnel público com ngrok..." -ForegroundColor Yellow
$ngrokProcess = Start-Process ngrok -ArgumentList "http", "8000" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

# Obter URL pública
Write-Host "[4/4] 🔍 Obtendo URL pública..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels"
    $publicUrl = $ngrokApi.tunnels[0].public_url
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "              ✅ SOFIA ESTÁ NO AR! ✅                  " -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URL Pública (acesse de qualquer lugar):" -ForegroundColor Cyan
    Write-Host "   $publicUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🏠 URL Local:" -ForegroundColor Cyan
    Write-Host "   http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Dashboard ngrok:" -ForegroundColor Cyan
    Write-Host "   http://localhost:4040" -ForegroundColor White
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Dicas:" -ForegroundColor Yellow
    Write-Host "   • Compartilhe a URL pública para acesso remoto" -ForegroundColor Gray
    Write-Host "   • Mantenha esta janela aberta enquanto usa Sofia" -ForegroundColor Gray
    Write-Host "   • Use o Dashboard para ver conexões em tempo real" -ForegroundColor Gray
    Write-Host ""
    
    # Copiar URL para clipboard
    Set-Clipboard -Value $publicUrl
    Write-Host "📋 URL copiada para a área de transferência!" -ForegroundColor Green
    Write-Host ""
    
    # Perguntar se quer abrir no navegador
    Write-Host "Deseja abrir Sofia no navegador agora? (S/N): " -ForegroundColor Cyan -NoNewline
    $resposta = Read-Host
    
    if ($resposta -eq "S" -or $resposta -eq "s" -or $resposta -eq "") {
        Start-Process $publicUrl
        Write-Host "✅ Navegador aberto!" -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "⚠️  Não foi possível obter URL automaticamente" -ForegroundColor Yellow
    Write-Host "    Acesse http://localhost:4040 para ver a URL pública" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Servidores ativos. Mantenha esta janela aberta!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para PARAR Sofia:" -ForegroundColor Red
Write-Host "  • Pressione Ctrl+C ou" -ForegroundColor Gray
Write-Host "  • Feche esta janela" -ForegroundColor Gray
Write-Host ""
Write-Host "Pressione qualquer tecla para encerrar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host ""
Write-Host "🛑 Encerrando servidores..." -ForegroundColor Yellow

try {
    Stop-Process -Id $sofiaProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $ngrokProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
} catch {
    # Ignorar erros ao parar processos
}

Write-Host "✅ Sofia encerrada com sucesso!" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2
