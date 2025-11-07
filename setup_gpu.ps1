# Configuração do Ollama para usar GPU NVIDIA

## Variáveis de Ambiente para Otimizar GPU

# Força uso da GPU (CUDA)
$env:OLLAMA_GPU_ENABLED = "1"

# Configurações de memória GPU
# Permite que o Ollama use até 4GB da GPU (ajuste conforme necessário)
$env:OLLAMA_GPU_LAYERS = "999"  # Usa todas as camadas possíveis na GPU

# Configurações de contexto e paralelismo
$env:OLLAMA_NUM_PARALLEL = "4"  # Número de requisições paralelas
$env:OLLAMA_MAX_LOADED_MODELS = "1"  # Mantém modelo carregado na GPU

# Log detalhado para debug
$env:OLLAMA_DEBUG = "1"

Write-Host "🎮 Configurações de GPU aplicadas!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Configuração atual:" -ForegroundColor Cyan
Write-Host "   - GPU habilitada: $env:OLLAMA_GPU_ENABLED" -ForegroundColor Yellow
Write-Host "   - Camadas na GPU: $env:OLLAMA_GPU_LAYERS (todas disponíveis)" -ForegroundColor Yellow
Write-Host "   - Paralelismo: $env:OLLAMA_NUM_PARALLEL requisições" -ForegroundColor Yellow
Write-Host "   - Modelos carregados: $env:OLLAMA_MAX_LOADED_MODELS" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Para aplicar essas configurações, execute:" -ForegroundColor Cyan
Write-Host "   .\setup_gpu.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Em seguida, inicie o Ollama normalmente" -ForegroundColor Cyan
