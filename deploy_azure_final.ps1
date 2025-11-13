# Sofia - Deploy Azure Automatico
# Execute: powershell -ExecutionPolicy Bypass -File deploy_azure_final.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sofia - Deploy Azure Automatico" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Encontrar az.cmd
$azPath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
if (!(Test-Path $azPath)) {
    $azPath = "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
}

if (!(Test-Path $azPath)) {
    Write-Host "Erro: Azure CLI nao encontrado!" -ForegroundColor Red
    Write-Host "Instale com: winget install Microsoft.AzureCLI" -ForegroundColor Yellow
    pause
    exit 1
}

# Funcao para executar az
function Invoke-Az {
    param([string]$command)
    $fullCommand = "& '$azPath' $command"
    Invoke-Expression $fullCommand
}

Write-Host "[1/6] Verificando login no Azure..." -ForegroundColor Yellow
$account = & $azPath account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fazendo login..." -ForegroundColor Yellow
    & $azPath login
}
Write-Host "OK - Logado com sucesso" -ForegroundColor Green
Write-Host ""

Write-Host "[2/6] Registrando providers Azure..." -ForegroundColor Yellow
& $azPath provider register --namespace Microsoft.Storage | Out-Null
& $azPath provider register --namespace Microsoft.Web | Out-Null
& $azPath provider register --namespace Microsoft.Compute | Out-Null
Write-Host "OK - Providers registrados" -ForegroundColor Green
Write-Host ""

Write-Host "[3/6] Criando Storage Account..." -ForegroundColor Yellow
$storageName = "sofiastorage" + (Get-Random -Min 1000 -Max 9999)
& $azPath storage account create --name $storageName --resource-group sofia-rg --location eastus --sku Standard_LRS --output none
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar storage account" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "OK - Storage criado: $storageName" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Criando Function App (pode demorar 2-3 min)..." -ForegroundColor Yellow
& $azPath functionapp create --name sofia-functions --resource-group sofia-rg --storage-account $storageName --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4 --os-type Linux --output none
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar function app" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "OK - Function App criado" -ForegroundColor Green
Write-Host ""

Write-Host "[5/6] Configurando variaveis de ambiente..." -ForegroundColor Yellow
# IMPORTANTE: Configure o GITHUB_TOKEN como variável de ambiente antes de executar:
# $env:GITHUB_TOKEN = "seu_token_aqui"
if (-not $env:GITHUB_TOKEN) {
    Write-Host "ERRO: GITHUB_TOKEN não configurado!" -ForegroundColor Red
    Write-Host "Execute: `$env:GITHUB_TOKEN = 'seu_token_github'" -ForegroundColor Yellow
    pause
    exit 1
}
& $azPath functionapp config appsettings set --name sofia-functions --resource-group sofia-rg --settings "GITHUB_TOKEN=$env:GITHUB_TOKEN" "SOFIA_USE_CLOUD=true" "GITHUB_MODEL=gpt-4o" --output none
Write-Host "OK - Variaveis configuradas" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Criando Static Web App (vai abrir navegador)..." -ForegroundColor Yellow
& $azPath staticwebapp create --name sofia-web --resource-group sofia-rg --location eastus2 --source https://github.com/SomBRaRCP/sofia --branch master --app-location "/sofia/web" --login-with-github
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar static web app" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "OK - Static Web App criado" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs da Aplicacao:" -ForegroundColor Cyan
Write-Host "  Frontend: https://sofia-web.azurestaticapps.net" -ForegroundColor White
Write-Host "  Backend:  https://sofia-functions.azurewebsites.net" -ForegroundColor White
Write-Host ""
Write-Host "Custos Estimados:" -ForegroundColor Cyan
Write-Host "  Uso Baixo: US$ 0,00/mes" -ForegroundColor Green
Write-Host "  Uso Medio: US$ 1-3/mes" -ForegroundColor Yellow
Write-Host "  Uso Alto:  US$ 5-10/mes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Configure Budget Alert no Portal Azure!" -ForegroundColor Cyan
Write-Host "  https://portal.azure.com" -ForegroundColor White
Write-Host ""
pause
