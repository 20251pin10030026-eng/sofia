# Script otimizado para iniciar Sofia com GPU
Write-Host "🚀 Iniciando Sofia com Aceleração por GPU..." -ForegroundColor Cyan
Write-Host ""

# 1. Configurar variáveis de ambiente para GPU
Write-Host "⚙️ Aplicando configurações de GPU..." -ForegroundColor Yellow
$env:OLLAMA_GPU_LAYERS = "999"        # Todas as camadas na GPU
$env:OLLAMA_NUM_PARALLEL = "4"         # 4 requisições paralelas
$env:OLLAMA_MAX_LOADED_MODELS = "1"    # Mantém modelo carregado
$env:OLLAMA_MODEL = "llama3.1:8b"      # Modelo otimizado

Write-Host "   ✅ Configurações aplicadas" -ForegroundColor Green
Write-Host ""

# 2. Verificar se Ollama está rodando
Write-Host "🔍 Verificando Ollama..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:11434" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Ollama está ativo" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Ollama não está rodando!" -ForegroundColor Red
    Write-Host ""
    Write-Host "   💡 Abra outro terminal e execute:" -ForegroundColor Cyan
    Write-Host "      ollama serve" -ForegroundColor White
    Write-Host ""
    Write-Host "   Pressione qualquer tecla quando o Ollama estiver rodando..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host ""

# 3. Parar servidor Flask anterior (se existir)
Write-Host "🛑 Parando servidor anterior..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*A.I_GitHUB*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Write-Host "   ✅ Limpo" -ForegroundColor Green
Write-Host ""

# 4. Exibir configuração
Write-Host "📊 Configuração Atual:" -ForegroundColor Cyan
Write-Host "   - GPU: NVIDIA GeForce GTX 1650 (4GB)" -ForegroundColor White
Write-Host "   - Modelo: $env:OLLAMA_MODEL" -ForegroundColor White
Write-Host "   - Camadas GPU: $env:OLLAMA_GPU_LAYERS" -ForegroundColor White
Write-Host "   - Paralelismo: $env:OLLAMA_NUM_PARALLEL" -ForegroundColor White
Write-Host ""

# 5. Iniciar servidor Flask
Write-Host "🌐 Iniciando servidor Sofia..." -ForegroundColor Cyan
Write-Host ""
Write-Host "┌─────────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│  Sofia IA - GPU Acelerada                  │" -ForegroundColor Green  
Write-Host "│  http://localhost:5000                      │" -ForegroundColor Green
Write-Host "│                                             │" -ForegroundColor Green
Write-Host "│  Modelo: llama3.1:8b                        │" -ForegroundColor Green
Write-Host "│  GPU: NVIDIA GTX 1650                       │" -ForegroundColor Green
Write-Host "│                                             │" -ForegroundColor Green
Write-Host "│  Pressione Ctrl+C para parar                │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────────┘" -ForegroundColor Green
Write-Host ""

Set-Location "D:\A.I_GitHUB"
& .\.venv\Scripts\python.exe -m sofia.api
