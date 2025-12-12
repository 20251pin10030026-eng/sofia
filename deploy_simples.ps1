# Deploy Sofia no Azure - Simplificado
Write-Host "Iniciando deploy Sofia no Azure..." -ForegroundColor Green

# Verificar Azure CLI
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Azure CLI nao instalado. Instalando..." -ForegroundColor Yellow
    winget install Microsoft.AzureCLI --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Login
Write-Host "Fazendo login no Azure..." -ForegroundColor Yellow
az login

# Variaveis
$rg = "sofia-rg"
$loc = "eastus"
$storage = "sofiastorage" + (Get-Random -Min 1000 -Max 9999)
$func = "sofia-functions"
$web = "sofia-web"

Write-Host "Criando Resource Group: $rg" -ForegroundColor Yellow
az group create --name $rg --location $loc

Write-Host "Criando Storage: $storage" -ForegroundColor Yellow
az storage account create --name $storage --resource-group $rg --location $loc --sku Standard_LRS

Write-Host "Criando Function App: $func" -ForegroundColor Yellow
az functionapp create --name $func --resource-group $rg --storage-account $storage --consumption-plan-location $loc --runtime python --runtime-version 3.11 --functions-version 4 --os-type Linux

Write-Host "Configurando variaveis..." -ForegroundColor Yellow
if (-not $env:GITHUB_TOKEN) {
    Write-Host "ERRO: GITHUB_TOKEN não configurado no ambiente." -ForegroundColor Red
    Write-Host "Defina antes de executar (exemplo):" -ForegroundColor Yellow
    Write-Host "  `$env:GITHUB_TOKEN = 'seu_token_aqui'" -ForegroundColor Yellow
    exit 1
}
az functionapp config appsettings set --name $func --resource-group $rg --settings "GITHUB_TOKEN=$env:GITHUB_TOKEN" "SOFIA_USE_CLOUD=true" "GITHUB_MODEL=gpt-4o"

Write-Host "Criando Static Web App: $web" -ForegroundColor Yellow
az staticwebapp create --name $web --resource-group $rg --location $loc --source https://github.com/SomBRaRCP/sofia --branch master --app-location "/sofia/web" --login-with-github

Write-Host "Deploy concluido!" -ForegroundColor Green
Write-Host "Acesse: https://$web.azurestaticapps.net" -ForegroundColor Cyan
