# Script para iniciar servidor Sofia com Azure (GitHub Models)

if (-not $env:GITHUB_TOKEN) {
	Write-Host "ERRO: GITHUB_TOKEN não configurado no ambiente." -ForegroundColor Red
	Write-Host "Defina antes de executar (exemplo):" -ForegroundColor Yellow
	Write-Host "  `$env:GITHUB_TOKEN = 'seu_token_aqui'" -ForegroundColor Yellow
	exit 1
}

Write-Host "Servidor iniciando com GITHUB_TOKEN no ambiente..." -ForegroundColor Green

# Navegar para diretório correto
Set-Location "D:\A.I_GitHUB"

# Iniciar servidor
python -m uvicorn sofia.api_web:app --host 0.0.0.0 --port 8000
