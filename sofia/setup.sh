#!/bin/bash

echo "🌸 Instalando Sofia - Assistente Virtual"
echo "========================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    exit 1
fi

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar Ollama
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "⚠️  Ollama não encontrado!"
    echo "Instale com: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
else
    echo "✅ Ollama encontrado"
    
    # Baixar modelo
    echo "🧠 Baixando modelo Mistral..."
    ollama pull mistral
fi

echo ""
echo "✅ Instalação completa!"
echo ""
echo "Para usar:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""