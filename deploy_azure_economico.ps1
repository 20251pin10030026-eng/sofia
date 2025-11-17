# 💰 Deploy Econômico Sofia no Azure
# Estratégia: Serverless + Cache = US$ 0-3/mês

Write-Host "Sofia - Deploy Economico no Azure" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Verificar Azure CLI
Write-Host "📋 Verificando Azure CLI..." -ForegroundColor Yellow
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI não instalado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale com:" -ForegroundColor Yellow
    Write-Host "  winget install Microsoft.AzureCLI" -ForegroundColor Green
    Write-Host ""
    Write-Host "OU baixe: https://aka.ms/installazurecliwindows" -ForegroundColor Green
    exit 1
}
Write-Host "✅ Azure CLI instalado" -ForegroundColor Green
Write-Host ""

# Login no Azure
Write-Host "🔐 Fazendo login no Azure..." -ForegroundColor Yellow
az login
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer login" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Login realizado" -ForegroundColor Green
Write-Host ""

# Configurações
$resourceGroup = "sofia-rg"
$location = "eastus"  # Mais barato que brazilsouth
$storageAccount = "sofiastorage$(Get-Random -Minimum 1000 -Maximum 9999)"
$functionApp = "sofia-functions"
$staticWebApp = "sofia-web"

Write-Host "📊 Configurações:" -ForegroundColor Cyan
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
Write-Host "  Location: $location (US$ mais barato)" -ForegroundColor White
Write-Host "  Storage: $storageAccount" -ForegroundColor White
Write-Host "  Functions: $functionApp" -ForegroundColor White
Write-Host "  Static Web: $staticWebApp" -ForegroundColor White
Write-Host ""

# Confirmar
$confirm = Read-Host "Continuar com o deploy? (s/n)"
if ($confirm -ne "s") {
    Write-Host "❌ Deploy cancelado" -ForegroundColor Red
    exit 0
}
Write-Host ""

# Criar Resource Group
Write-Host "📦 Criando Resource Group..." -ForegroundColor Yellow
az group create `
  --name $resourceGroup `
  --location $location `
  --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar resource group" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Resource Group criado" -ForegroundColor Green
Write-Host ""

# Criar Storage Account
Write-Host "💾 Criando Storage Account..." -ForegroundColor Yellow
az storage account create `
  --name $storageAccount `
  --resource-group $resourceGroup `
  --location $location `
  --sku Standard_LRS `
  --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar storage" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Storage Account criado" -ForegroundColor Green
Write-Host ""

# Criar Function App (Consumption Plan)
Write-Host "⚡ Criando Azure Functions (Consumption)..." -ForegroundColor Yellow
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
    Write-Host "❌ Erro ao criar function app" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Function App criado" -ForegroundColor Green
Write-Host ""

# Configurar Variáveis de Ambiente
Write-Host "🔧 Configurando variáveis de ambiente..." -ForegroundColor Yellow
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings `
  "GITHUB_TOKEN=ghp_REDACTED" `
  "SOFIA_USE_CLOUD=true" `
  "GITHUB_MODEL=gpt-4o" `
  --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao configurar variáveis" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Variáveis configuradas" -ForegroundColor Green
Write-Host ""

# Deploy do Function App
Write-Host "🚀 Fazendo deploy do Function App..." -ForegroundColor Yellow
Write-Host "  (Isso pode levar 2-3 minutos)" -ForegroundColor Gray

# Verificar se Azure Functions Core Tools está instalado
if (!(Get-Command func -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure Functions Core Tools não instalado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale com:" -ForegroundColor Yellow
    Write-Host "  npm install -g azure-functions-core-tools@4" -ForegroundColor Green
    Write-Host ""
    Write-Host "Depois, execute novamente este script." -ForegroundColor Yellow
    exit 1
}

cd sofia\azure_functions
func azure functionapp publish $functionApp --python
cd ..\..

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Function App deployado" -ForegroundColor Green
Write-Host ""

# Criar Static Web App
Write-Host "🌐 Criando Static Web App..." -ForegroundColor Yellow
Write-Host "  (Isso abrirá o navegador para autenticar com GitHub)" -ForegroundColor Gray

az staticwebapp create `
  --name $staticWebApp `
  --resource-group $resourceGroup `
  --location $location `
  --source https://github.com/SomBRaRCP/sofia `
  --branch master `
  --app-location "/sofia/web" `
  --login-with-github

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar static web app" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Static Web App criado" -ForegroundColor Green
Write-Host ""

# Obter URLs
Write-Host "📊 Obtendo informações dos recursos..." -ForegroundColor Yellow
$functionUrl = az functionapp show --name $functionApp --resource-group $resourceGroup --query "defaultHostName" -o tsv
$staticUrl = az staticwebapp show --name $staticWebApp --resource-group $resourceGroup --query "defaultHostname" -o tsv

Write-Host ""
Write-Host "🎉 Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URLs da Aplicação:" -ForegroundColor Cyan
Write-Host "  Frontend: https://$staticUrl" -ForegroundColor Green
Write-Host "  Backend:  https://$functionUrl" -ForegroundColor Green
Write-Host ""
Write-Host "💰 Custos Estimados:" -ForegroundColor Cyan
Write-Host "  Uso Baixo (<100 usuários/dia):    US$ 0,00/mês" -ForegroundColor Green
Write-Host "  Uso Médio (100-500 usuários/dia): US$ 1-3/mês" -ForegroundColor Yellow
Write-Host "  Uso Alto (>500 usuários/dia):     US$ 5-10/mês" -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Monitorar Custos:" -ForegroundColor Cyan
Write-Host "  Portal Azure: https://portal.azure.com" -ForegroundColor White
Write-Host "  Cost Management: https://portal.azure.com/#view/Microsoft_Azure_CostManagement" -ForegroundColor White
Write-Host ""
Write-Host "🔔 Configurar Budget Alert:" -ForegroundColor Cyan
Write-Host "  1. Acesse: Cost Management + Billing" -ForegroundColor White
Write-Host "  2. Clique em: Budgets" -ForegroundColor White
Write-Host "  3. Crie um alerta para US$ 10/mês" -ForegroundColor White
Write-Host ""
Write-Host "✅ Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Acesse a URL do frontend" -ForegroundColor White
Write-Host "  2. Teste o chat e o metaverso" -ForegroundColor White
Write-Host "  3. Configure o Budget Alert" -ForegroundColor White
Write-Host "  4. Monitore custos após 1 semana" -ForegroundColor White
Write-Host ""
Write-Host "Sofia esta online! Aproveite!" -ForegroundColor Magenta
