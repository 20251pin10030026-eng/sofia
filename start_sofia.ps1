# Script de inicialização da Sofia
# Use: .\start_sofia.ps1

Write-Host "🌸 Iniciando Sofia..." -ForegroundColor Magenta

# Ir para o diretório da Sofia
Set-Location -Path "D:\A.I_GitHUB\sofia"

# Configurar variáveis de ambiente
$env:PYTHONPATH = "D:\A.I_GitHUB"
$env:SOFIA_AUTORIDADE_DECLARADA = "1"

Write-Host "✅ Variáveis de ambiente configuradas" -ForegroundColor Green
Write-Host "   PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "   SOFIA_AUTORIDADE_DECLARADA: $env:SOFIA_AUTORIDADE_DECLARADA" -ForegroundColor Gray

# Verificar se PyPDF2 está instalado
Write-Host "`n📚 Verificando dependências..." -ForegroundColor Cyan
$pypdfCheck = & "D:\A.I_GitHUB\.venv\Scripts\python.exe" -c "import PyPDF2; print(f'PyPDF2 {PyPDF2.__version__}')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ $pypdfCheck" -ForegroundColor Green
} else {
    Write-Host "   ❌ PyPDF2 não encontrado. Instalando..." -ForegroundColor Yellow
    & "D:\A.I_GitHUB\.venv\Scripts\python.exe" -m pip install PyPDF2
}

# Iniciar servidor
Write-Host "`n🚀 Iniciando servidor FastAPI na porta 8000..." -ForegroundColor Cyan
Write-Host "   Acesse: http://localhost:8000" -ForegroundColor Gray
Write-Host "   Para parar: Ctrl+C`n" -ForegroundColor Gray

& "D:\A.I_GitHUB\.venv\Scripts\python.exe" .\api_web.py
