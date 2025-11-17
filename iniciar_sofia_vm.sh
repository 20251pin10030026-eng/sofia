#!/bin/bash
cd /home/sofiaadmin/sofia

# Criar arquivo .env
cat > sofia/.env << 'EOF'
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_REDACTED
GITHUB_MODEL=gpt-4o
EOF

# Criar systemd service
sudo tee /etc/systemd/system/sofia.service > /dev/null << 'EOF'
[Unit]
Description=Sofia - Assistente Virtual
After=network.target

[Service]
Type=simple
User=sofiaadmin
WorkingDirectory=/home/sofiaadmin/sofia/sofia
Environment="SOFIA_USE_CLOUD=true"
Environment="GITHUB_TOKEN=ghp_REDACTED"
Environment="GITHUB_MODEL=gpt-4o"
ExecStart=/home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable sofia
sudo systemctl restart sofia

# Aguardar
sleep 10

# Verificar status
sudo systemctl status sofia --no-pager

# Testar
echo "---TESTE---"
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ola Sofia, voce esta usando GPT-4o?","session_id":"test"}'
