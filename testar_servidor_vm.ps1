# Teste de Conexao com Servidor Sofia na VM
$serverUrl = "http://52.226.167.30:5000"

Write-Host "Testando conexao com servidor Sofia..." -ForegroundColor Cyan
Write-Host "URL: $serverUrl" -ForegroundColor White
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri $serverUrl -TimeoutSec 5
    Write-Host "SUCESSO! Servidor respondendo" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor White
} catch {
    Write-Host "ERRO: Servidor nao respondeu" -ForegroundColor Red
    Write-Host "Detalhes: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Testando endpoint de chat..." -ForegroundColor Cyan
try {
    $body = @{
        message = "Ola Sofia, voce esta ai?"
        session_id = "test123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$serverUrl/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "SUCESSO! Chat respondeu" -ForegroundColor Green
    Write-Host "Resposta: $($response.response)" -ForegroundColor White
} catch {
    Write-Host "ERRO: Chat nao respondeu" -ForegroundColor Red
    Write-Host "Detalhes: $($_.Exception.Message)" -ForegroundColor Yellow
}

pause
