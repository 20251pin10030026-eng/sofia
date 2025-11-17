# ============================================================
# Script: Simplificar VM para Servidor Web Estático
# ============================================================
# Remove Sofia da VM e instala apenas nginx para servir o site
# Usa sua máquina local para processamento (mais potente)
# VM fica apenas como servidor web público (muito leve)
# ============================================================

$azPath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
$resourceGroup = "sofia-rg"
$vmName = "sofia-vm"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SIMPLIFICAR VM PARA SERVIDOR WEB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Esta VM tem:" -ForegroundColor Yellow
Write-Host "  - 1 vCPU" -ForegroundColor Yellow
Write-Host "  - 1 GB RAM" -ForegroundColor Yellow
Write-Host "  - Custo: USD 8.09/mes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Configuracao proposta:" -ForegroundColor Green
Write-Host "  - VM: Apenas nginx (servidor web estatico)" -ForegroundColor Green
Write-Host "  - Seu PC: Sofia com GPT-4o (processamento)" -ForegroundColor Green
Write-Host "  - Conexao: Tunel ngrok ou Cloudflare Tunnel" -ForegroundColor Green
Write-Host ""

$confirma = Read-Host "Deseja continuar? (S/N)"
if ($confirma -ne "S" -and $confirma -ne "s") {
    Write-Host "Operacao cancelada." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "[1/4] Parando servicos Python na VM..." -ForegroundColor Cyan

$script1 = @'
# Parar e desabilitar Sofia
systemctl stop sofia 2>/dev/null || true
systemctl disable sofia 2>/dev/null || true
rm -f /etc/systemd/system/sofia.service

# Matar processos Python
pkill -f "python.*api.py" || true

# Remover arquivos desnecessarios
rm -rf /home/sofiaadmin/sofia

echo "Sofia removida da VM"
'@

& $azPath vm run-command invoke `
    --resource-group $resourceGroup `
    --name $vmName `
    --command-id RunShellScript `
    --scripts $script1

Write-Host "OK - Servicos Python removidos" -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Instalando nginx..." -ForegroundColor Cyan

$script2 = @'
# Atualizar pacotes
apt-get update -qq

# Instalar nginx
apt-get install -y nginx

# Habilitar nginx
systemctl enable nginx
systemctl start nginx

echo "Nginx instalado e rodando"
'@

& $azPath vm run-command invoke `
    --resource-group $resourceGroup `
    --name $vmName `
    --command-id RunShellScript `
    --scripts $script2

Write-Host "OK - Nginx instalado" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Configurando nginx para servir o site..." -ForegroundColor Cyan

$script3 = @'
# Criar diretorio web
mkdir -p /var/www/sofia

# Configurar nginx
cat > /etc/nginx/sites-available/sofia << 'NGINXEOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/sofia;
    index index.html;
    
    server_name _;
    
    # Logs
    access_log /var/log/nginx/sofia_access.log;
    error_log /var/log/nginx/sofia_error.log;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache para arquivos estaticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Compressao gzip
    gzip on;
    gzip_types text/css application/javascript application/json;
}
NGINXEOF

# Ativar site
ln -sf /etc/nginx/sites-available/sofia /etc/nginx/sites-enabled/sofia
rm -f /etc/nginx/sites-enabled/default

# Testar configuracao
nginx -t

# Recarregar nginx
systemctl reload nginx

echo "Nginx configurado"
'@

& $azPath vm run-command invoke `
    --resource-group $resourceGroup `
    --name $vmName `
    --command-id RunShellScript `
    --scripts $script3

Write-Host "OK - Nginx configurado" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Ajustando porta 80..." -ForegroundColor Cyan

& $azPath vm open-port `
    --resource-group $resourceGroup `
    --name $vmName `
    --port 80 `
    --priority 1000

Write-Host "OK - Porta 80 aberta" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  VM SIMPLIFICADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Enviar arquivos do site para VM:" -ForegroundColor White
Write-Host "   scp -r sofia/web/* sofiaadmin@52.226.167.30:/var/www/sofia/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Configurar Sofia no seu PC local:" -ForegroundColor White
Write-Host "   - Sofia rodara localmente com GPT-4o" -ForegroundColor Gray
Write-Host "   - Use ngrok para expor a API" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Atualizar site para usar API local:" -ForegroundColor White
Write-Host "   - script.js: const API_URL = 'https://seu-ngrok.app'" -ForegroundColor Gray
Write-Host ""
Write-Host "Site estara em: http://52.226.167.30" -ForegroundColor Cyan
Write-Host ""
