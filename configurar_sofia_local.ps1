# ============================================================
# Script: Configurar Sofia Localmente com GitHub Models
# ============================================================
# Configura Sofia para rodar no seu PC (mais potente)
# Usa GitHub Models (GPT-4o) - gratis com Copilot Pro
# Expoe API via ngrok para acesso publico
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR SOFIA LOCAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta no diretorio correto
if (-not (Test-Path "sofia")) {
    Write-Host "ERRO: Execute este script em D:\A.I_GitHUB" -ForegroundColor Red
    exit 1
}

Write-Host "[1/5] Verificando ambiente Python..." -ForegroundColor Cyan

# Ativar venv
if (Test-Path ".venv/Scripts/Activate.ps1") {
    & .venv/Scripts/Activate.ps1
    Write-Host "OK - Virtual environment ativado" -ForegroundColor Green
} else {
    Write-Host "Criando virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & .venv/Scripts/Activate.ps1
    Write-Host "OK - Virtual environment criado" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Instalando dependencias..." -ForegroundColor Cyan

pip install -q -r sofia/requirements.txt
if (Test-Path "sofia/requirements.txt") {
    pip install -q flask requests python-dotenv
}

Write-Host "OK - Dependencias instaladas" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Configurando GitHub Models..." -ForegroundColor Cyan

# Verificar se .env existe
$envPath = "sofia/.env"
if (-not (Test-Path $envPath)) {
    Write-Host "Criando arquivo .env..." -ForegroundColor Yellow
    @"
# GitHub Models (GPT-4o) - Gratis com Copilot Pro
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_REDACTED
GITHUB_MODEL=gpt-4o

# Servidor local
HOST=0.0.0.0
PORT=5000
"@ | Out-File -FilePath $envPath -Encoding UTF8
    Write-Host "OK - Arquivo .env criado" -ForegroundColor Green
} else {
    # Atualizar .env existente
    $content = Get-Content $envPath -Raw
    if ($content -notmatch "SOFIA_USE_CLOUD=true") {
        Write-Host "Atualizando .env existente..." -ForegroundColor Yellow
        @"

# GitHub Models (GPT-4o) - Gratis com Copilot Pro
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_REDACTED
GITHUB_MODEL=gpt-4o
"@ | Add-Content -Path $envPath
        Write-Host "OK - Arquivo .env atualizado" -ForegroundColor Green
    } else {
        Write-Host "OK - Arquivo .env ja configurado" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[4/5] Testando Sofia..." -ForegroundColor Cyan

# Testar importacao
python -c "from sofia.core.cerebro import Cerebro; print('OK - Cerebro importado')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Sofia funcionando" -ForegroundColor Green
} else {
    Write-Host "AVISO: Erro ao importar Sofia" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Verificando ngrok..." -ForegroundColor Cyan

# Verificar se ngrok esta instalado
if (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "OK - ngrok ja instalado" -ForegroundColor Green
    $ngrokInstalled = $true
} else {
    Write-Host "ngrok nao encontrado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para instalar ngrok:" -ForegroundColor White
    Write-Host "  1. Baixe em: https://ngrok.com/download" -ForegroundColor Gray
    Write-Host "  2. Extraia o arquivo" -ForegroundColor Gray
    Write-Host "  3. Mova para C:\Windows\System32\" -ForegroundColor Gray
    Write-Host "  4. Crie conta gratis em: https://dashboard.ngrok.com/signup" -ForegroundColor Gray
    Write-Host "  5. Execute: ngrok config add-authtoken SEU_TOKEN" -ForegroundColor Gray
    Write-Host ""
    $ngrokInstalled = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SOFIA CONFIGURADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar Sofia:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Iniciar servidor local:" -ForegroundColor White
Write-Host "   cd sofia" -ForegroundColor Gray
Write-Host "   python sofia/api.py" -ForegroundColor Gray
Write-Host ""
if ($ngrokInstalled) {
    Write-Host "2. Em outro terminal, expor via ngrok:" -ForegroundColor White
    Write-Host "   ngrok http 5000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Copie a URL do ngrok (ex: https://abc123.ngrok.io)" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Atualize o site (script.js):" -ForegroundColor White
    Write-Host "   const API_URL = 'https://sua-url.ngrok.io'" -ForegroundColor Gray
} else {
    Write-Host "2. Instale ngrok (veja instrucoes acima)" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Exponha a API:" -ForegroundColor White
    Write-Host "   ngrok http 5000" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Arquivo de configuracao: sofia/.env" -ForegroundColor Cyan
Write-Host ""

# Perguntar se deseja iniciar agora
Write-Host "Deseja iniciar Sofia agora? (S/N): " -NoNewline -ForegroundColor Yellow
$resposta = Read-Host
if ($resposta -eq "S" -or $resposta -eq "s") {
    Write-Host ""
    Write-Host "Iniciando Sofia..." -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray
    Write-Host ""
    cd sofia
    python sofia/api.py
}
