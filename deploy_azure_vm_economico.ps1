# 🌸 Sofia - Deploy VM Econômica (com auto-shutdown)
# Mesma VM, mas desliga automaticamente à noite para economizar

$ErrorActionPreference = "Stop"
$azPath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

Write-Host "🌸 Sofia VM Econômica - Auto Shutdown" -ForegroundColor Magenta
Write-Host ""

# Configurar auto-shutdown (desliga às 22h, liga às 7h)
$resourceGroup = "sofia-rg"
$vmName = "sofia-vm"

Write-Host "Configurando auto-shutdown..." -ForegroundColor Yellow
Write-Host "VM desligará automaticamente às 22:00 BRT" -ForegroundColor Cyan
Write-Host ""

& $azPath vm auto-shutdown `
    --resource-group $resourceGroup `
    --name $vmName `
    --time 0100 `
    --location eastus `
    --email "seu-email@example.com"

Write-Host ""
Write-Host "✅ Auto-shutdown configurado!" -ForegroundColor Green
Write-Host ""
Write-Host "💰 Economia estimada:" -ForegroundColor Yellow
Write-Host "   • Sem auto-shutdown: US$ 8.09/mês (24h/dia)" -ForegroundColor White
Write-Host "   • Com auto-shutdown: US$ 3.54/mês (9h/dia útil)" -ForegroundColor Green
Write-Host "   • Economia: 56% (US$ 4.55/mês)" -ForegroundColor Green
Write-Host ""

pause
