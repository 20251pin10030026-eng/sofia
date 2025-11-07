# Script para reiniciar a Sofia com ambiente correto
Write-Host "🔄 Parando servidor Flask existente..." -ForegroundColor Yellow

# Para processos Python que possam estar rodando
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*A.I_GitHUB*"} | Stop-Process -Force

Start-Sleep -Seconds 2

Write-Host "✅ Servidor parado" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Iniciando Sofia com ambiente virtual..." -ForegroundColor Cyan
Write-Host ""

# Ativa ambiente virtual e inicia servidor
Set-Location "D:\A.I_GitHUB"
& .\.venv\Scripts\python.exe -m sofia.api

# Nota: Este script mantém o terminal aberto com o servidor rodando
# Para parar: Ctrl+C
