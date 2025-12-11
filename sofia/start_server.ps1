# Script para iniciar servidor Sofia com Azure (GitHub Models)

# Configurar token GitHub
$env:GITHUB_TOKEN = "ghp_REDACTED"

Write-Host "Servidor iniciando com GITHUB_TOKEN configurado..." -ForegroundColor Green

# Navegar para diretório correto
Set-Location "D:\A.I_GitHUB"

# Iniciar servidor
python -m uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000
