# ============================================================
# Script: Atualizar URL do ngrok no site da VM
# ============================================================
# Atualiza automaticamente a URL do ngrok quando ela mudar
# Uso: .\atualizar_ngrok_url.ps1
# ============================================================

param(
    [string]$NgrokUrl = ""
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZAR URL DO NGROK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Se não passou URL, pedir
if ([string]::IsNullOrEmpty($NgrokUrl)) {
    Write-Host "Digite a nova URL do ngrok:" -ForegroundColor Yellow
    Write-Host "Exemplo: https://abc123.ngrok-free.app" -ForegroundColor Gray
    Write-Host ""
    $NgrokUrl = Read-Host "URL"
}

# Validar URL
if (-not $NgrokUrl.StartsWith("https://")) {
    Write-Host "ERRO: URL deve começar com https://" -ForegroundColor Red
    exit 1
}

# Remover barra final se houver
$NgrokUrl = $NgrokUrl.TrimEnd('/')

Write-Host ""
Write-Host "URL do ngrok: $NgrokUrl" -ForegroundColor Cyan
Write-Host ""

# Confirmar
Write-Host "Atualizar site na VM com esta URL? (S/N): " -NoNewline -ForegroundColor Yellow
$confirma = Read-Host
if ($confirma -ne "S" -and $confirma -ne "s") {
    Write-Host "Operação cancelada" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "[1/3] Atualizando arquivo local..." -ForegroundColor Cyan

# Atualizar script.js local
$scriptPath = "sofia/web/script.js"
if (Test-Path $scriptPath) {
    $content = Get-Content $scriptPath -Raw
    
    # Substituir API_URL
    $content = $content -replace "const API_URL = '[^']*';", "const API_URL = '$NgrokUrl';"
    
    # Substituir WS_URL
    $wsUrl = $NgrokUrl -replace "https://", "wss://"
    $content = $content -replace "const WS_URL = '[^']*';", "const WS_URL = '$wsUrl';"
    
    $content | Set-Content $scriptPath -Encoding UTF8
    Write-Host "OK - script.js atualizado localmente" -ForegroundColor Green
} else {
    Write-Host "AVISO: script.js não encontrado em $scriptPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/3] Enviando para VM Azure..." -ForegroundColor Cyan

$azPath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

# Criar script de atualização
$updateScript = @"
cd /var/www/html
if [ -f script.js ]; then
    # Backup
    cp script.js script.js.bak
    
    # Atualizar API_URL
    sed -i "s|const API_URL = '[^']*';|const API_URL = '$NgrokUrl';|g" script.js
    
    # Atualizar WS_URL
    sed -i "s|const WS_URL = '[^']*';|const WS_URL = '$wsUrl';|g" script.js
    
    echo "Arquivo atualizado"
    echo "---"
    grep -E "(const API_URL|const WS_URL)" script.js
else
    echo "ERRO: script.js não encontrado em /var/www/html"
    exit 1
fi
"@

# Executar na VM
& $azPath vm run-command invoke `
    --resource-group sofia-rg `
    --name sofia-vm `
    --command-id RunShellScript `
    --scripts $updateScript `
    --output json | ConvertFrom-Json | ForEach-Object {
        if ($_.value[0].message -match "Enable succeeded") {
            Write-Host "OK - Script executado na VM" -ForegroundColor Green
        } else {
            Write-Host "AVISO: Verifique a saída" -ForegroundColor Yellow
        }
    }

Write-Host ""
Write-Host "[3/3] Testando..." -ForegroundColor Cyan

Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://52.226.167.30" -TimeoutSec 10
    Write-Host "OK - Site acessível" -ForegroundColor Green
} catch {
    Write-Host "AVISO: Site pode estar temporariamente indisponível" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ATUALIZAÇÃO COMPLETA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nova configuração:" -ForegroundColor Yellow
Write-Host "  - Site: http://52.226.167.30" -ForegroundColor Cyan
Write-Host "  - API: $NgrokUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Teste conversando com Sofia no site!" -ForegroundColor White
Write-Host ""

# Perguntar se quer abrir o site
Write-Host "Abrir site no navegador? (S/N): " -NoNewline -ForegroundColor Yellow
$abrir = Read-Host
if ($abrir -eq "S" -or $abrir -eq "s") {
    Start-Process "http://52.226.167.30"
}
