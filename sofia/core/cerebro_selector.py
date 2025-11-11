"""
🌸 Sofia - Seletor de Cérebro
Escolhe automaticamente entre Ollama (local) ou GitHub Models (cloud)
baseado nas variáveis de ambiente
"""

import os

# Detectar ambiente
USE_CLOUD = os.getenv("SOFIA_USE_CLOUD", "false").lower() == "true"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Importar cerebro apropriado
if USE_CLOUD or GITHUB_TOKEN:
    print("🌐 Sofia rodando em modo CLOUD (GitHub Models)")
    from .cerebro_cloud import perguntar
else:
    print("🏠 Sofia rodando em modo LOCAL (Ollama)")
    from .cerebro import perguntar

# Exportar função perguntar
__all__ = ['perguntar']
