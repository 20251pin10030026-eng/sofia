#!/bin/bash
# Script para configurar Sofia na VM Azure

echo "Configurando Sofia na VM..."

# 1. Criar .env com permissoes corretas
cd /home/sofiaadmin/sofia/sofia
cat > .env << 'ENVEOF'
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_REDACTED
GITHUB_MODEL=gpt-4o
ENVEOF

chown sofiaadmin:sofiaadmin .env

# 2. Criar servico systemd
cat > /etc/systemd/system/sofia.service << 'SVCEOF'
[Unit]
Description=Sofia - Assistente Virtual
After=network.target

[Service]
Type=simple
User=sofiaadmin
WorkingDirectory=/home/sofiaadmin/sofia/sofia
Environment=PATH=/home/sofiaadmin/sofia/venv/bin
Environment=SOFIA_USE_CLOUD=true
Environment=GITHUB_TOKEN=ghp_REDACTED
Environment=GITHUB_MODEL=gpt-4o
ExecStart=/home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF

# 3. Iniciar servico
systemctl daemon-reload
systemctl enable sofia
systemctl restart sofia

# 4. Aguardar e testar
sleep 5
systemctl status sofia
echo ""
echo "Testando servidor..."
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ola Sofia","session_id":"test"}' \
  2>/dev/null | head -c 300

echo ""
echo "Configuracao concluida!"
