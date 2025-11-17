# 🌐 Sofia Pública via ngrok - Guia Rápido

## 🎯 O que é ngrok?
Um túnel que torna seu servidor local acessível publicamente via HTTPS.

## ⚡ Setup Rápido (5 minutos)

### 1️⃣ Baixar ngrok
1. Acesse: https://ngrok.com/download
2. Baixe para Windows
3. Extraia `ngrok.exe` para `C:\ngrok\`

### 2️⃣ Criar conta e configurar
1. Crie conta em: https://dashboard.ngrok.com/signup
2. Copie seu **Authtoken** do dashboard
3. Abra PowerShell e execute:
```powershell
C:\ngrok\ngrok.exe authtoken SEU_TOKEN_AQUI
```

### 3️⃣ Iniciar Sofia
```powershell
cd d:\A.I_GitHUB
.\iniciar_sofia_publico.ps1
```

### 4️⃣ Pronto! 🎉
Você verá algo como:
```
✅ SOFIA ESTÁ NO AR!
🌐 URL Pública: https://abc123.ngrok.io
```

## 🌟 Vantagens

✅ **Grátis** - Sem custo algum
✅ **HTTPS automático** - Seguro
✅ **Funciona em qualquer lugar** - Compartilhe com amigos
✅ **Sem configuração de rede** - Bypassa firewall/NAT
✅ **Dashboard** - http://localhost:4040 (veja requisições)

## ⚠️ Limitações (plano grátis)

- URL muda toda vez que reiniciar
- Limite de 40 conexões/minuto
- Sessão expira após 8 horas de inatividade
- 1 túnel por vez

## 📊 Monitoramento

Enquanto rodando, acesse:
- **Dashboard ngrok:** http://localhost:4040
- **Status Sofia:** http://localhost:8000/status

## 🛑 Parar

Pressione `Ctrl+C` no PowerShell

## 💡 Dicas

### URL Permanente (opcional - plano pago)
Se quiser URL fixa tipo `sofia.ngrok.io`:
- Upgrade para plano Personal ($8/mês)
- Configure domínio customizado

### Compartilhar
Envie a URL pública para qualquer pessoa:
```
https://abc123.ngrok.io
```

Eles acessam direto no navegador! 🌐

## 🔐 Segurança

✅ HTTPS automático
✅ Token de autenticação
✅ Pode adicionar senha (ver ngrok docs)

### Adicionar senha (opcional)
```powershell
C:\ngrok\ngrok.exe http 8000 --basic-auth "usuario:senha"
```

## 🚀 Alternativas Futuras

Quando conseguir Azure:
- Migrate para Azure Static Web Apps
- URL permanente grátis
- Sem limite de conexões
- Melhor performance

## ❓ Problemas Comuns

### "ngrok not found"
- Certifique que está em `C:\ngrok\`
- Ou ajuste caminho no script

### "Failed to authenticate"
- Configure authtoken: `ngrok authtoken SEU_TOKEN`

### "Address already in use"
- Porta 8000 ocupada
- Mude porta no script ou pare outro processo

## 📞 Suporte

- Docs ngrok: https://ngrok.com/docs
- Dashboard: https://dashboard.ngrok.com

---

**Pronto para começar? Execute:**
```powershell
cd d:\A.I_GitHUB
.\iniciar_sofia_publico.ps1
```

🌸 **Sofia estará acessível no mundo todo!** 🌍
