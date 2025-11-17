# Sofia - Deploy em Azure VM
# Script simplificado para criar VM Linux com Sofia

$ErrorActionPreference = "Stop"
$azPath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

Write-Host "Sofia - Deploy em Azure VM" -ForegroundColor Magenta
Write-Host "===========================" -ForegroundColor Magenta
Write-Host ""

# Configuracoes
$resourceGroup = "sofia-rg"
$vmName = "sofia-vm"
$location = "eastus"
$vmSize = "Standard_B1s"
$image = "Ubuntu2204"
$adminUser = "sofiaadmin"

Write-Host "Configuracoes:" -ForegroundColor Cyan
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
Write-Host "  VM Name: $vmName" -ForegroundColor White
Write-Host "  Location: $location" -ForegroundColor White
Write-Host "  Size: $vmSize (USD 7.59/mes)" -ForegroundColor White
Write-Host "  OS: Ubuntu 22.04 LTS" -ForegroundColor White
Write-Host "  Admin User: $adminUser" -ForegroundColor White
Write-Host ""

# Perguntar senha
Write-Host "Digite a senha para o usuario sofiaadmin:" -ForegroundColor Yellow
Write-Host "(minimo 12 caracteres, letras maiusculas, minusculas e numeros)" -ForegroundColor Gray
$password = Read-Host -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

if ($passwordPlain.Length -lt 12) {
    Write-Host "ERRO: Senha deve ter no minimo 12 caracteres!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "CUSTO ESTIMADO: USD 8/mes rodando 24/7" -ForegroundColor Yellow
Write-Host "Deseja continuar? (S/N)" -ForegroundColor Yellow
$confirm = Read-Host
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Deploy cancelado" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "[1/5] Verificando Resource Group..." -ForegroundColor Yellow
$rgExists = & $azPath group exists --name $resourceGroup
if ($rgExists -eq "false") {
    Write-Host "Criando Resource Group..." -ForegroundColor Cyan
    & $azPath group create --name $resourceGroup --location $location --output none
}
Write-Host "OK - Resource Group pronto" -ForegroundColor Green
Write-Host ""

Write-Host "[2/5] Criando Maquina Virtual..." -ForegroundColor Yellow
Write-Host "Aguarde 3-5 minutos..." -ForegroundColor Cyan
& $azPath vm create `
    --resource-group $resourceGroup `
    --name $vmName `
    --image $image `
    --size $vmSize `
    --admin-username $adminUser `
    --admin-password $passwordPlain `
    --location $location `
    --public-ip-sku Standard `
    --output table

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao criar VM" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "OK - VM criada" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Abrindo porta 5000..." -ForegroundColor Yellow
& $azPath vm open-port --resource-group $resourceGroup --name $vmName --port 5000 --priority 1001 --output none
Write-Host "OK - Porta 5000 aberta" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] Obtendo IP publico..." -ForegroundColor Yellow
$publicIp = & $azPath vm show --resource-group $resourceGroup --name $vmName --show-details --query publicIps --output tsv
Write-Host "OK - IP Publico: $publicIp" -ForegroundColor Green
Write-Host ""

Write-Host "[5/5] Instalando Sofia na VM..." -ForegroundColor Yellow
Write-Host "Aguarde 5-10 minutos..." -ForegroundColor Cyan

# Criar script de instalacao
$installScript = @'
#!/bin/bash
set -e
echo "Atualizando sistema..."
sudo apt-get update -qq
sudo apt-get install -y python3.11 python3.11-venv python3-pip git -qq

echo "Clonando repositorio..."
cd /home/sofiaadmin
git clone https://github.com/SomBRaRCP/sofia.git

echo "Criando ambiente virtual..."
cd sofia
python3.11 -m venv venv
source venv/bin/activate
pip install -r sofia/requirements.txt -q

echo "Configurando servico..."
sudo tee /etc/systemd/system/sofia.service > /dev/null <<EOF
[Unit]
Description=Sofia - Assistente Virtual
After=network.target

[Service]
Type=simple
User=sofiaadmin
WorkingDirectory=/home/sofiaadmin/sofia/sofia
Environment=PATH=/home/sofiaadmin/sofia/venv/bin
ExecStart=/home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable sofia
sudo systemctl start sofia

echo "Sofia instalada com sucesso!"
'@

# Salvar script temporario
$tempFile = [System.IO.Path]::GetTempFileName()
$installScript | Out-File -FilePath $tempFile -Encoding ASCII

# Executar na VM
& $azPath vm run-command invoke `
    --resource-group $resourceGroup `
    --name $vmName `
    --command-id RunShellScript `
    --scripts "@$tempFile"

Remove-Item $tempFile -Force

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "   DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Informacoes da VM:" -ForegroundColor Cyan
Write-Host "  Nome: $vmName" -ForegroundColor White
Write-Host "  IP Publico: $publicIp" -ForegroundColor White
Write-Host "  Usuario SSH: $adminUser" -ForegroundColor White
Write-Host ""
Write-Host "URLs de Acesso:" -ForegroundColor Cyan
Write-Host "  API Sofia: http://${publicIp}:5000" -ForegroundColor White
Write-Host "  Web Interface: http://${publicIp}:5000/web" -ForegroundColor White
Write-Host ""
Write-Host "Comandos Uteis:" -ForegroundColor Cyan
Write-Host "  Conectar SSH:" -ForegroundColor White
Write-Host "    ssh ${adminUser}@${publicIp}" -ForegroundColor Gray
Write-Host ""
Write-Host "  Ver logs Sofia:" -ForegroundColor White
Write-Host "    ssh ${adminUser}@${publicIp} 'sudo journalctl -u sofia -f'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Parar VM (economizar):" -ForegroundColor White
Write-Host "    az vm deallocate --resource-group $resourceGroup --name $vmName" -ForegroundColor Gray
Write-Host ""
Write-Host "  Iniciar VM:" -ForegroundColor White
Write-Host "    az vm start --resource-group $resourceGroup --name $vmName" -ForegroundColor Gray
Write-Host ""
Write-Host "  Deletar VM:" -ForegroundColor White
Write-Host "    az vm delete --resource-group $resourceGroup --name $vmName --yes" -ForegroundColor Gray
Write-Host ""

pause
