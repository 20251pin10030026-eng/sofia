# Deploy Economico Sofia no Azure
# Estrategia: Serverless + Cache = US$ 0-3/mes

Write-Host "Sofia - Deploy Economico no Azure" -ForegroundColor Magenta
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Azure CLI
Write-Host "Verificando Azure CLI..." -ForegroundColor Yellow
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Azure CLI nao instalado!" -ForegroundColor Red
    Write-Host "Instale com: winget install Microsoft.AzureCLI" -ForegroundColor Green
    exit 1
}
Write-Host "OK: Azure CLI instalado" -ForegroundColor Green
Write-Host ""

# Login no Azure
Write-Host "Fazendo login no Azure..." -ForegroundColor Yellow
Write-Host "(Uma janela do navegador ira abrir)" -ForegroundColor Gray
az login
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
$functionApp = "sofia-functions"
$staticWebApp = "sofia-web"

Write-Host "Configuracoes do Deploy:" -ForegroundColor Cyan
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
Write-Host "  Location: $location (mais barato)" -ForegroundColor White
Write-Host "  Storage: $storageAccount" -ForegroundColor White
Write-Host "  Functions: $functionApp" -ForegroundColor White
Write-Host "  Static Web: $staticWebApp" -ForegroundColor White
Write-Host ""

# Confirmar
$confirm = Read-Host "Continuar com o deploy? (s/n)"
if ($confirm -ne "s") {
    Write-Host "Deploy cancelado" -ForegroundColor Red
    exit 0
}
Write-Host ""

# Criar Resource Group
Write-Host "1/5 - Criando Resource Group..." -ForegroundColor Yellow
az group create --name $resourceGroup --location $location --output none
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao criar resource group" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Resource Group criado" -ForegroundColor Green
Write-Host ""

# Criar Storage Account
Write-Host "2/5 - Criando Storage Account..." -ForegroundColor Yellow
az storage account create `
  --name $storageAccount `
  --resource-group $resourceGroup `
  --location $location `
  --sku Standard_LRS `
  --output none
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao criar storage" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Storage Account criado" -ForegroundColor Green
Write-Host ""

# Criar Function App
Write-Host "3/5 - Criando Azure Functions (Consumption)..." -ForegroundColor Yellow
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
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao criar function app" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Function App criado" -ForegroundColor Green
Write-Host ""

# Configurar Variaveis
Write-Host "4/5 - Configurando variaveis de ambiente..." -ForegroundColor Yellow
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings `
  "GITHUB_TOKEN=ghp_REDACTED" `
  "SOFIA_USE_CLOUD=true" `
  "GITHUB_MODEL=gpt-4o" `
  --output none
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao configurar variaveis" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Variaveis configuradas" -ForegroundColor Green
Write-Host ""

# Deploy Function App
Write-Host "5/5 - Deploy do Function App..." -ForegroundColor Yellow
Write-Host "(Isso pode levar 2-3 minutos)" -ForegroundColor Gray

# Verificar func
if (!(Get-Command func -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Azure Functions Core Tools nao instalado!" -ForegroundColor Red
    Write-Host "Instale com: npm install -g azure-functions-core-tools@4" -ForegroundColor Green
    exit 1
}

Push-Location sofia\azure_functions
func azure functionapp publish $functionApp --python
$deployResult = $LASTEXITCODE
Pop-Location

if ($deployResult -ne 0) {
    Write-Host "ERRO no deploy" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Function App deployado" -ForegroundColor Green
Write-Host ""

# Criar Static Web App
Write-Host "Criando Static Web App..." -ForegroundColor Yellow
Write-Host "(Isso abrira o navegador para autenticar com GitHub)" -ForegroundColor Gray

az staticwebapp create `
  --name $staticWebApp `
  --resource-group $resourceGroup `
  --location $location `
  --source https://github.com/SomBRaRCP/sofia `
  --branch master `
  --app-location "/sofia/web" `
  --login-with-github

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao criar static web app" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Static Web App criado" -ForegroundColor Green
Write-Host ""

# Obter URLs
Write-Host "Obtendo informacoes dos recursos..." -ForegroundColor Yellow
$functionUrl = az functionapp show --name $functionApp --resource-group $resourceGroup --query "defaultHostName" -o tsv
$staticUrl = az staticwebapp show --name $staticWebApp --resource-group $resourceGroup --query "defaultHostname" -o tsv

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs da Aplicacao:" -ForegroundColor Cyan
Write-Host "  Frontend: https://$staticUrl" -ForegroundColor Green
Write-Host "  Backend:  https://$functionUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Custos Estimados:" -ForegroundColor Cyan
Write-Host "  Uso Baixo (<100 usuarios/dia):    US$ 0,00/mes" -ForegroundColor Green
Write-Host "  Uso Medio (100-500 usuarios/dia): US$ 1-3/mes" -ForegroundColor Yellow
Write-Host "  Uso Alto (>500 usuarios/dia):     US$ 5-10/mes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Acesse a URL do frontend" -ForegroundColor White
Write-Host "  2. Teste o chat e o metaverso" -ForegroundColor White
Write-Host "  3. Configure Budget Alert no Portal Azure" -ForegroundColor White
Write-Host "  4. Monitore custos apos 1 semana" -ForegroundColor White
Write-Host ""
Write-Host "Sofia esta online!" -ForegroundColor Magenta
