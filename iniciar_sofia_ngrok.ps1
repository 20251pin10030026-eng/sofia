# Sofia - iniciar local + ngrok (acesso publico)

$ErrorActionPreference = "Stop"

Write-Host "Iniciando Sofia local via ngrok..." -ForegroundColor Cyan
Write-Host ""

$projectRoot = "D:\A.I_GitHUB"
$sofiaModule = "sofia.api_web:app"
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$ollamaExe = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
$ollamaHost = "http://localhost:11434"
$healthUrl = "http://localhost:8000/api/health"
$ngrokApiUrl = "http://localhost:4040/api/tunnels"

function Test-Ollama {
    try {
        $null = Invoke-WebRequest -Uri "$ollamaHost/api/tags" -TimeoutSec 3 -UseBasicParsing
        return $true
    } catch {
        return $false
    }
}

function Get-OllamaModelNames {
    try {
        $tags = Invoke-RestMethod -Uri "$ollamaHost/api/tags" -TimeoutSec 5
        if ($tags -and $tags.models) {
            return @($tags.models | ForEach-Object { $_.name })
        }
    } catch {
    }
    return @()
}

function Pick-Model([string[]]$models) {
    $priority = @(
        "llama3.1:8b",
        "mistral:latest",
        "sofia-fast:latest",
        "sofia-balanced:latest",
        "gpt-oss:20b",
        "llama3:latest"
    )

    foreach ($cand in $priority) {
        if ($models -contains $cand) {
            return $cand
        }
    }

    if ($models.Count -gt 0) {
        return $models[0]
    }

    return "llama3.1:8b"
}

function Wait-Http([string]$url, [int]$attempts = 15, [int]$sleepSec = 1) {
    for ($i = 1; $i -le $attempts; $i++) {
        try {
            $null = Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing
            return $true
        } catch {
            Start-Sleep -Seconds $sleepSec
        }
    }
    return $false
}

if (-not (Test-Path $pythonExe)) {
    Write-Host "Python nao encontrado: $pythonExe" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "ngrok nao encontrado no PATH." -ForegroundColor Red
    exit 1
}

# Garantir modo LOCAL e saida mais limpa/natural por padrao.
$env:PYTHONPATH = $projectRoot
$env:SOFIA_AUTORIDADE_DECLARADA = "1"
$env:SOFIA_USE_CLOUD = "false"
$env:GITHUB_TOKEN = ""
$env:GITHUB_MODEL = ""
$env:SOFIA_EXIBIR_COT = "0"
$env:SOFIA_LAYOUT_ESTRITO = "0"

# Subir Ollama se necessario.
if (-not (Test-Ollama)) {
    Write-Host "Ollama nao esta ativo. Iniciando..." -ForegroundColor Yellow
    if (-not (Test-Path $ollamaExe)) {
        Write-Host "Ollama nao encontrado em: $ollamaExe" -ForegroundColor Red
        Write-Host "Instale o Ollama primeiro: https://ollama.com/download/windows" -ForegroundColor Yellow
        exit 1
    }
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" | Out-Null
}

if (-not (Wait-Http -url "$ollamaHost/api/tags" -attempts 15 -sleepSec 1)) {
    Write-Host "Nao foi possivel conectar ao Ollama em $ollamaHost." -ForegroundColor Red
    exit 1
}

$models = Get-OllamaModelNames
$selectedModel = Pick-Model -models $models

# FAST por padrao para reduzir latencia no acesso via ngrok.
$env:SOFIA_LOCAL_PROFILE = "FAST"
$env:SOFIA_MODEL_FAST = $selectedModel

if ($models -contains "gpt-oss:20b") {
    $env:SOFIA_MODEL_QUALITY = "gpt-oss:20b"
} elseif ($models -contains "sofia-balanced:latest") {
    $env:SOFIA_MODEL_QUALITY = "sofia-balanced:latest"
} else {
    $env:SOFIA_MODEL_QUALITY = $selectedModel
}

$env:OLLAMA_MODEL = $selectedModel

Write-Host "Ambiente local configurado:" -ForegroundColor Green
Write-Host "  SOFIA_USE_CLOUD=$env:SOFIA_USE_CLOUD"
Write-Host "  SOFIA_LOCAL_PROFILE=$env:SOFIA_LOCAL_PROFILE"
Write-Host "  OLLAMA_MODEL=$env:OLLAMA_MODEL"
Write-Host ""

# Limpar processos antigos para evitar conflito de porta/tunel.
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $pythonExe } | Stop-Process -Force -ErrorAction SilentlyContinue

$sofiaProcess = $null
$ngrokProcess = $null

try {
    Set-Location $projectRoot

    Write-Host "Iniciando servidor Sofia na porta 8000..." -ForegroundColor Cyan
    $sofiaProcess = Start-Process -FilePath $pythonExe -ArgumentList "-m", "uvicorn", $sofiaModule, "--host", "0.0.0.0", "--port", "8000" -PassThru

    if (-not (Wait-Http -url $healthUrl -attempts 20 -sleepSec 1)) {
        Write-Host "Servidor Sofia nao respondeu em $healthUrl." -ForegroundColor Red
        exit 1
    }
    Write-Host "Sofia online localmente." -ForegroundColor Green

    Write-Host "Iniciando tunel ngrok..." -ForegroundColor Cyan
    $ngrokProcess = Start-Process -FilePath "ngrok" -ArgumentList "http", "8000" -PassThru

    if (-not (Wait-Http -url $ngrokApiUrl -attempts 15 -sleepSec 1)) {
        Write-Host "ngrok nao respondeu no painel local (4040)." -ForegroundColor Red
        exit 1
    }

    $publicUrl = $null
    try {
        $ngrokApi = Invoke-RestMethod -Uri $ngrokApiUrl -TimeoutSec 5
        if ($ngrokApi.tunnels -and $ngrokApi.tunnels.Count -gt 0) {
            $publicUrl = $ngrokApi.tunnels[0].public_url
        }
    } catch {
    }

    Write-Host ""
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host "SOFIA NO AR (MODO LOCAL + NGROK)" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host "Local:     http://localhost:8000"
    if ($publicUrl) {
        Write-Host "Publica:   $publicUrl" -ForegroundColor Yellow
    } else {
        Write-Host "Publica:   verifique em http://localhost:4040" -ForegroundColor Yellow
    }
    Write-Host "Dashboard: http://localhost:4040"
    Write-Host ""
    Write-Host "Mantenha esta janela aberta. Ctrl+C para parar." -ForegroundColor Gray
    Write-Host ""

    while ($true) {
        Start-Sleep -Seconds 10
        if (-not (Wait-Http -url $healthUrl -attempts 1 -sleepSec 1)) {
            Write-Host "Servidor Sofia interrompido." -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "Encerrando processos..." -ForegroundColor Yellow
    if ($sofiaProcess) {
        Stop-Process -Id $sofiaProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($ngrokProcess) {
        Stop-Process -Id $ngrokProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Finalizado." -ForegroundColor Green
}
