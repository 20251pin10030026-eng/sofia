# 🌸 Sofia - Projeto de IA

Repositório do projeto Sofia - Uma assistente virtual inteligente com memória persistente e interface web moderna.

## 📁 Estrutura do Projeto

```
A.I_GitHUB/
├── iniciar_sofia_web.bat    # Atalho rápido para Windows
└── sofia/                    # Projeto principal
    ├── api.py               # Servidor web (Flask)
    ├── start_web.bat        # Iniciar servidor
    ├── main.py              # Interface CLI
    ├── requirements.txt     # Dependências Python
    ├── README.md            # Documentação completa
    ├── INICIO_RAPIDO.md     # Guia rápido
    │
    ├── core/                # Núcleo da Sofia
    │   ├── cerebro.py       # Integração Ollama + memória
    │   ├── identidade.py    # Personalidade
    │   ├── memoria.py       # Sistema de memória 5GB
    │   └── seguranca.py     # Criptografia
    │
    ├── ethics/              # Leis, Pilares e Protocolos
    │   ├── leis.enc         # Leis criptografadas
    │   ├── pilares.enc      # Pilares criptografados
    │   └── protocolos.enc   # Protocolos criptografados
    │
    ├── web/                 # Interface Web
    │   ├── index.html       # Página principal
    │   ├── style.css        # Estilos
    │   ├── script.js        # Lógica frontend
    │   └── README.md        # Doc da interface
    │
    └── .sofia_internal/     # Dados privados (não versionado)
        └── memoria/         # Histórico e aprendizados
```

## 🚀 Início Rápido

### Pré-requisitos

1. **Python 3.8+** instalado
2. **Ollama** instalado e rodando ([ollama.ai](https://ollama.ai))
3. **Modelo Mistral** baixado: `ollama pull mistral`

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/SomBRaRCP/sofia.git
cd sofia

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variável de ambiente (opcional)
set SOFIA_CREATOR_SECRET=reginaldo
```

### Usar Interface Web (Recomendado)

```bash
# Windows - Da raiz do projeto:
iniciar_sofia_web.bat

# OU, de dentro de sofia/:
cd sofia
python api.py

# Então abra sofia/web/index.html no navegador
```

### Usar Interface CLI (Terminal)

```bash
cd sofia
python -m sofia.main
```

## 📚 Documentação

- **[sofia/README.md](sofia/README.md)** - Documentação completa do projeto
- **[sofia/INICIO_RAPIDO.md](sofia/INICIO_RAPIDO.md)** - Guia rápido de início
- **[sofia/web/README.md](sofia/web/README.md)** - Documentação da interface web

## ✨ Recursos Principais

- 🌐 **Interface Web Moderna** - Chat visual com design elegante
- 🧠 **Memória de 5GB** - Armazena conversas e aprende
- 💭 **Aprendizado Automático** - Detecta e salva informações importantes
- 🎭 **Personalidade Única** - Sofia se vê como entidade feminina com corpo de subits
- 🔒 **Sistema de Segurança** - Leis, Pilares e Protocolos criptografados
- 📊 **Estatísticas** - Visualização de uso e métricas
- 🔍 **Busca** - Pesquisar conversas antigas

## 🎯 Modos de Uso

### Interface Web
```bash
cd sofia
python api.py
# Abra web/index.html
```

### CLI (Terminal)
```bash
cd sofia
python -m sofia.main
```

## 🛠️ Tecnologias

- **Python 3.8+** - Linguagem principal
- **Ollama + Mistral** - Motor de IA local
- **Flask** - API REST
- **HTML/CSS/JS** - Interface web
- **JSON** - Armazenamento de dados

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/SomBRaRCP/sofia/issues)
- **Criador**: [@SomBRaRCP](https://github.com/SomBRaRCP)

## 📄 Licença

Projeto pessoal de Reginaldo (@SomBRaRCP)

---

**Criado com 💜 por Reginaldo**
