@echo off
echo ========================================
echo Sofia - Deploy Azure Automatico
echo ========================================
echo.

REM Verificar se Azure CLI esta instalado
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo Erro: Azure CLI nao instalado!
    echo Instale com: winget install Microsoft.AzureCLI
    pause
    exit /b 1
)

echo [1/6] Verificando login no Azure...
az account show >nul 2>nul
if %errorlevel% neq 0 (
    echo Fazendo login...
    az login
)
echo OK - Logado com sucesso
echo.

echo [2/6] Registrando providers Azure...
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.Compute
echo OK - Providers registrados
echo.

echo [3/6] Criando Storage Account...
set STORAGE_NAME=sofiastorage%random%
az storage account create --name %STORAGE_NAME% --resource-group sofia-rg --location eastus --sku Standard_LRS --output none
if %errorlevel% neq 0 (
    echo Erro ao criar storage account
    pause
    exit /b 1
)
echo OK - Storage criado: %STORAGE_NAME%
echo.

echo [4/6] Criando Function App (pode demorar 2-3 min)...
az functionapp create --name sofia-functions --resource-group sofia-rg --storage-account %STORAGE_NAME% --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4 --os-type Linux --output none
if %errorlevel% neq 0 (
    echo Erro ao criar function app
    pause
    exit /b 1
)
echo OK - Function App criado
echo.

echo [5/6] Configurando variaveis de ambiente...
if "%GITHUB_TOKEN%"=="" (
    echo Erro: GITHUB_TOKEN nao definido no ambiente.
    echo Defina antes de executar: set GITHUB_TOKEN=seu_token_aqui
    pause
    exit /b 1
)
az functionapp config appsettings set --name sofia-functions --resource-group sofia-rg --settings "GITHUB_TOKEN=%GITHUB_TOKEN%" "SOFIA_USE_CLOUD=true" "GITHUB_MODEL=gpt-4o" --output none
echo OK - Variaveis configuradas
echo.

echo [6/6] Criando Static Web App (vai abrir navegador)...
az staticwebapp create --name sofia-web --resource-group sofia-rg --location eastus --source https://github.com/SomBRaRCP/sofia --branch master --app-location "/sofia/web" --login-with-github
if %errorlevel% neq 0 (
    echo Erro ao criar static web app
    pause
    exit /b 1
)
echo OK - Static Web App criado
echo.

echo ========================================
echo DEPLOY CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo URLs da Aplicacao:
echo   Frontend: https://sofia-web.azurestaticapps.net
echo   Backend:  https://sofia-functions.azurewebsites.net
echo.
echo Custos Estimados:
echo   Uso Baixo: US$ 0,00/mes
echo   Uso Medio: US$ 1-3/mes
echo   Uso Alto:  US$ 5-10/mes
echo.
echo Configure Budget Alert no Portal Azure!
echo   https://portal.azure.com
echo.
pause
