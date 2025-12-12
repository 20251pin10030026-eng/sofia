# GUIA RAPIDO - Configurar Sofia na VM

## Passo 1: Conectar via SSH
```bash
ssh sofiaadmin@52.226.167.30
# Digite a senha quando solicitado
```

## Passo 2: Configurar .env
```bash
cd /home/sofiaadmin/sofia/sofia
cat > .env << 'EOF'
SOFIA_USE_CLOUD=true
GITHUB_TOKEN=ghp_seu_token_aqui
GITHUB_MODEL=gpt-4o
EOF
```

## Passo 3: Criar script wrapper
```bash
cd /home/sofiaadmin/sofia
cat > start-sofia.sh << 'EOF'
#!/bin/bash
export SOFIA_USE_CLOUD=true
export GITHUB_TOKEN=ghp_seu_token_aqui
export GITHUB_MODEL=gpt-4o
cd /home/sofiaadmin/sofia/sofia
exec /home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000
EOF
chmod +x start-sofia.sh
```

## Passo 4: Criar serviço systemd
```bash
sudo tee /etc/systemd/system/sofia.service > /dev/null << 'EOF'
[Unit]
Description=Sofia - Assistente Virtual
After=network.target

[Service]
Type=simple
User=sofiaadmin
WorkingDirectory=/home/sofiaadmin/sofia/sofia
ExecStart=/home/sofiaadmin/sofia/start-sofia.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

## Passo 5: Iniciar serviço
```bash
sudo systemctl daemon-reload
sudo systemctl enable sofia
sudo systemctl restart sofia
```

## Passo 6: Verificar
```bash
sudo systemctl status sofia
```

## Passo 7: Testar
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ola Sofia","session_id":"test"}'
```

Se tudo estiver OK, você verá uma resposta do GPT-4o!

## Troubleshooting

**Ver logs em tempo real:**
```bash
sudo journalctl -u sofia -f
```

**Reiniciar se necessário:**
```bash
sudo systemctl restart sofia
```
