# 🔥 Liberar Firewall para Sofia
# Execute como Administrador

Write-Host "🔥 Configurando Firewall do Windows para Sofia..." -ForegroundColor Cyan

# Remover regra antiga se existir
Remove-NetFirewallRule -DisplayName "Sofia AI - Porta 8000" -ErrorAction SilentlyContinue

# Criar nova regra
New-NetFirewallRule -DisplayName "Sofia AI - Porta 8000" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8000 `
    -Action Allow `
    -Profile Any

Write-Host "✅ Firewall configurado!" -ForegroundColor Green
Write-Host ""
Write-Host "Agora acesse de qualquer dispositivo na sua rede:" -ForegroundColor Yellow
Write-Host "http://192.168.15.22:8000" -ForegroundColor Cyan
