# Script para criar atalho na area de trabalho

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Sofia - Servidor Publico.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "D:\A.I_GitHUB\Iniciar_Sofia.vbs"
$Shortcut.WorkingDirectory = "D:\A.I_GitHUB"
$Shortcut.Description = "Inicia Sofia com acesso publico via ngrok"
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Save()

Write-Host "Atalho criado na area de trabalho!" -ForegroundColor Green
Write-Host ""
Write-Host "Voce pode agora:" -ForegroundColor Cyan
Write-Host "  - Dar duplo clique no atalho" -ForegroundColor Gray
Write-Host "  - Ou executar: Iniciar_Sofia.bat" -ForegroundColor Gray
Write-Host "  - Ou executar: Iniciar_Sofia.vbs" -ForegroundColor Gray
Write-Host ""
Start-Sleep -Seconds 3
