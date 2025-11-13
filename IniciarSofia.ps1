Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SOFIA - INICIANDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# 1. Iniciar Sofia API
Write-Host "Iniciando Sofia API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd D:\A.I_GitHUB; & .venv\Scripts\Activate.ps1; cd sofia; python api.py`""
Start-Sleep -Seconds 5

# 2. Iniciar ngrok
Write-Host "Iniciando ngrok..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"ngrok http 5000`""
Start-Sleep -Seconds 3

# 3. Abrir site
Write-Host "Abrindo site..." -ForegroundColor Yellow
Start-Process "https://ambitious-desert-09adbb10f.3.azurestaticapps.net"

Write-Host ""
Write-Host "PRONTO!" -ForegroundColor Green
Write-Host "- Copie a URL do ngrok" -ForegroundColor Cyan
Write-Host "- Execute: atualizar_ngrok_url.ps1" -ForegroundColor Cyan
Write-Host ""
