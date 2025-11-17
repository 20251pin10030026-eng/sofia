# ============================================================
# Script: Criar Atalho da Sofia na Área de Trabalho
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRIAR ATALHO DA SOFIA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Caminhos
$scriptPath = "$PSScriptRoot\Iniciar_Sofia.bat"
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\Sofia - Assistente Virtual.lnk"
$iconPath = "$PSScriptRoot\sofia\web\favicon.ico"

# Verificar se o script existe
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERRO: Iniciar_Sofia.bat nao encontrado!" -ForegroundColor Red
    Write-Host "Caminho esperado: $scriptPath" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Criando atalho..." -ForegroundColor Cyan
Write-Host "Script: $scriptPath" -ForegroundColor Gray
Write-Host "Atalho: $shortcutPath" -ForegroundColor Gray
Write-Host ""

# Criar objeto WScript Shell
$WScriptShell = New-Object -ComObject WScript.Shell

# Criar atalho
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $scriptPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Sofia - Assistente Virtual com IA (GPT-4o)"
$Shortcut.WindowStyle = 1  # Normal window

# Tentar usar icone customizado
if (Test-Path $iconPath) {
    $Shortcut.IconLocation = $iconPath
    Write-Host "Icone: $iconPath" -ForegroundColor Gray
} else {
    # Usar icone padrao do Windows (estrela)
    $Shortcut.IconLocation = "%SystemRoot%\System32\imageres.dll,77"
    Write-Host "Icone: Padrao do Windows (estrela)" -ForegroundColor Gray
}

# Salvar atalho
$Shortcut.Save()

# Verificar se foi criado
if (Test-Path $shortcutPath) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ATALHO CRIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Localizacao: $shortcutPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Para usar:" -ForegroundColor Yellow
    Write-Host "  1. Clique duplo no atalho 'Sofia - Assistente Virtual'" -ForegroundColor White
    Write-Host "  2. Aguarde Sofia e ngrok iniciarem" -ForegroundColor White
    Write-Host "  3. Copie a URL do ngrok" -ForegroundColor White
    Write-Host "  4. Se necessario, execute: atualizar_ngrok_url.ps1" -ForegroundColor White
    Write-Host "  5. Converse com Sofia no site!" -ForegroundColor White
    Write-Host ""
    
    # Perguntar se quer abrir a area de trabalho
    Write-Host "Abrir area de trabalho? (S/N): " -NoNewline -ForegroundColor Yellow
    $resposta = Read-Host
    if ($resposta -eq "S" -or $resposta -eq "s") {
        explorer $desktopPath
    }
} else {
    Write-Host "ERRO: Falha ao criar atalho!" -ForegroundColor Red
}

Write-Host ""
pause
