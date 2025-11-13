Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZADOR DE URL NGROK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "D:\A.I_GitHUB"

# Pedir URL do ngrok
Write-Host "COPIE A URL DO NGROK" -ForegroundColor Green
Write-Host ""
Write-Host "Va ate a janela do ngrok e copie a URL em 'Forwarding'" -ForegroundColor Cyan
Write-Host "Exemplo: https://xxxxx.ngrok-free.app" -ForegroundColor Gray
Write-Host ""

$ngrokUrl = Read-Host "Cole a URL do ngrok aqui"

if ([string]::IsNullOrWhiteSpace($ngrokUrl)) {
    Write-Host ""
    Write-Host "ERRO: URL nao fornecida!" -ForegroundColor Red
    Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Limpar URL (remover espaços, http://, etc)
$ngrokUrl = $ngrokUrl.Trim()
if ($ngrokUrl -match 'http://') {
    $ngrokUrl = $ngrokUrl -replace 'http://', 'https://'
}
if ($ngrokUrl -notmatch '^https://') {
    $ngrokUrl = "https://$ngrokUrl"
}

# Validar URL
if ($ngrokUrl -notmatch '^https://[a-z0-9]+\.ngrok-free\.app$') {
    Write-Host ""
    Write-Host "AVISO: URL pode estar incorreta!" -ForegroundColor Yellow
    Write-Host "URL recebida: $ngrokUrl" -ForegroundColor Gray
    Write-Host "Formato esperado: https://xxxxx.ngrok-free.app" -ForegroundColor Gray
    Write-Host ""
    $continuar = Read-Host "Deseja continuar mesmo assim? (S/N)"
    if ($continuar -ne 'S' -and $continuar -ne 's') {
        Write-Host "Operacao cancelada." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Atualizando configuracao..." -ForegroundColor Yellow
Write-Host ""

$scriptJsPath = "sofia\web\script.js"
$wsUrl = $ngrokUrl -replace '^https://', 'wss://'

try {
    # Atualizar script.js local
    Write-Host "[1/3] Atualizando arquivo local..." -ForegroundColor Cyan
    $content = Get-Content $scriptJsPath -Raw -Encoding UTF8
    
    $content = $content -replace "const API_URL = '[^']*';", "const API_URL = '$ngrokUrl';"
    $content = $content -replace "const WS_URL = '[^']*';", "const WS_URL = '$wsUrl';"
    
    [System.IO.File]::WriteAllText("$PWD\$scriptJsPath", $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "     -> OK" -ForegroundColor Green
    
    # Commit e Push
    Write-Host "[2/3] Enviando para GitHub..." -ForegroundColor Cyan
    git add sofia/web/script.js | Out-Null
    $urlCurta = $ngrokUrl -replace 'https://|\.ngrok-free\.app', ''
    $commitMsg = "Update: Nova URL ngrok ($urlCurta)"
    git commit -m $commitMsg | Out-Null
    git push origin master 2>&1 | Out-Null
    Write-Host "     -> OK" -ForegroundColor Green
    
    # Abrir site
    Write-Host "[3/3] Testando..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    Start-Process $ngrokUrl
    Write-Host "     -> OK - Site aberto no navegador" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERRO: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ATUALIZACAO COMPLETA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nova configuracao:" -ForegroundColor Cyan
Write-Host "  API: $ngrokUrl" -ForegroundColor White
Write-Host "  WS:  $wsUrl" -ForegroundColor White
Write-Host ""
Write-Host "O Azure Static Web App atualizara em 1-2 minutos." -ForegroundColor Yellow
Write-Host "Acesso direto ja funciona: $ngrokUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
