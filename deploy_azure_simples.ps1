# Deploy Economico Sofia no Azure
# Estrategia: Serverless + Cache = US$ 0-3/mes

Write-Host "Sofia - Deploy Economico no Azure" -ForegroundColor Magenta
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Azure CLI
Write-Host "Verificando Azure CLI..." -ForegroundColor Yellow
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Azure CLI nao instalado!" -ForegroundColor Red
    Write-Host "Instale com: winget install Microsoft.AzureCLI" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: Azure CLI instalado" -ForegroundColor Green
Write-Host ""

# Verificar Azure Functions Core Tools
Write-Host "Verificando Azure Functions Core Tools..." -ForegroundColor Yellow
if (!(Get-Command func -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Azure Functions Core Tools nao instalado!" -ForegroundColor Red
    Write-Host "Instale com: npm install -g azure-functions-core-tools@4" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: Functions Core Tools instalado" -ForegroundColor Green
Write-Host ""

# Login no Azure
Write-Host "Fazendo login no Azure..." -ForegroundColor Yellow
az login --only-show-errors
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha no login" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Login realizado" -ForegroundColor Green
Write-Host ""

# Configuracoes
$resourceGroup = "sofia-rg"
$location = "eastus"
$storageAccount = "sofiastorage$(Get-Random -Minimum 1000 -Maximum 9999)"
$functionApp = "sofia-functions-$(Get-Random -Minimum 100 -Maximum 999)"
$staticWebApp = "sofia-web"

Write-Host "Configuracoes do Deploy:" -ForegroundColor Cyan
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
Write-Host "  Location: $location" -ForegroundColor White
Write-Host "  Storage: $storageAccount" -ForegroundColor White
Write-Host "  Functions: $functionApp" -ForegroundColor White
Write-Host "  Static Web: $staticWebApp" -ForegroundColor White
Write-Host ""

# Confirmar
$confirm = Read-Host "Continuar com o deploy? (s/n)"
if ($confirm -ne "s") {
    Write-Host "Deploy cancelado pelo usuario" -ForegroundColor Red
    exit 0
}
Write-Host ""

# Criar Resource Group
Write-Host "[1/5] Criando Resource Group..." -ForegroundColor Yellow
az group create --name $resourceGroup --location $location --output none
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Resource Group criado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao criar resource group" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Criar Storage Account
Write-Host "[2/5] Criando Storage Account..." -ForegroundColor Yellow
az storage account create `
  --name $storageAccount `
  --resource-group $resourceGroup `
  --location $location `
  --sku Standard_LRS `
  --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Storage Account criado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao criar storage" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Criar Function App
Write-Host "[3/5] Criando Azure Functions (pode levar 2-3 minutos)..." -ForegroundColor Yellow
az functionapp create `
  --name $functionApp `
  --resource-group $resourceGroup `
  --storage-account $storageAccount `
  --consumption-plan-location $location `
  --runtime python `
  --runtime-version 3.11 `
  --functions-version 4 `
  --os-type Linux `
  --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Function App criado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao criar function app" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Configurar Variaveis
Write-Host "[4/5] Configurando variaveis de ambiente..." -ForegroundColor Yellow
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings `
  "GITHUB_TOKEN=ghp_REDACTED" `
  "SOFIA_USE_CLOUD=true" `
  "GITHUB_MODEL=gpt-4o" `
  --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Variaveis configuradas" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao configurar variaveis" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Deploy Function App
Write-Host "[5/5] Fazendo deploy do Function App..." -ForegroundColor Yellow
Write-Host "  (Isso pode levar 2-3 minutos)" -ForegroundColor Gray

Push-Location sofia\azure_functions
func azure functionapp publish $functionApp --python
$deployResult = $LASTEXITCODE
Pop-Location

if ($deployResult -eq 0) {
    Write-Host "OK: Function App deployado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no deploy" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Obter URL do Functions
Write-Host "Obtendo informacoes dos recursos..." -ForegroundColor Yellow
$functionUrl = az functionapp show --name $functionApp --resource-group $resourceGroup --query "defaultHostName" -o tsv

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs da Aplicacao:" -ForegroundColor Cyan
Write-Host "  Backend API: https://$functionUrl/api/chat" -ForegroundColor Green
Write-Host "  Health Check: https://$functionUrl/api/health" -ForegroundColor Green
Write-Host ""
Write-Host "Custos Estimados:" -ForegroundColor Cyan
Write-Host "  Uso Baixo (<100 usuarios/dia):    US$ 0,00/mes" -ForegroundColor Green
Write-Host "  Uso Medio (100-500 usuarios/dia): US$ 1-3/mes" -ForegroundColor Yellow
Write-Host "  Uso Alto (>500 usuarios/dia):     US$ 5-10/mes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Configure Budget Alert no Azure Portal" -ForegroundColor White
Write-Host "  2. Teste a API: https://$functionUrl/api/health" -ForegroundColor White
Write-Host "  3. Monitore custos apos 1 semana" -ForegroundColor White
Write-Host ""
Write-Host "Para criar o Static Web App (frontend), execute:" -ForegroundColor Yellow
Write-Host "  az staticwebapp create --name sofia-web --resource-group sofia-rg --source https://github.com/SomBRaRCP/sofia --branch master --app-location /sofia/web --login-with-github" -ForegroundColor Gray
Write-Host ""
