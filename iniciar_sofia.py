#!/usr/bin/env python3
"""
🌸 Sofia - Iniciador da API Web
Inicia o servidor FastAPI com WebSocket para a interface web da Sofia
"""

import os
import sys
import subprocess
from pathlib import Path

def iniciar_api():
    """Inicia a API da Sofia com uvicorn"""
    
    print("=" * 60)
    print("🌸 SOFIA - INICIANDO API WEB")
    print("=" * 60)
    
    # Garantir que estamos no diretório correto
    pasta_raiz = Path(__file__).parent
    os.chdir(pasta_raiz)
    
    print(f"\n📁 Diretório: {pasta_raiz}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Verificar se uvicorn está instalado
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError:
        print("\n❌ ERRO: uvicorn não está instalado!")
        print("\nInstale com: pip install uvicorn")
        sys.exit(1)
    
    # Verificar se FastAPI está instalado
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("\n❌ ERRO: FastAPI não está instalado!")
        print("\nInstale com: pip install fastapi")
        sys.exit(1)
    
    # Verificar se o arquivo da API existe
    api_file = pasta_raiz / "sofia" / "api_web.py"
    if not api_file.exists():
        print(f"\n❌ ERRO: Arquivo não encontrado: {api_file}")
        sys.exit(1)
    
    print(f"✅ API encontrada: sofia/api_web.py")
    
    # Configurações do servidor
    host = "0.0.0.0"
    port = 8000
    
    print(f"\n🌐 Servidor:")
    print(f"   Host: {host}")
    print(f"   Porta: {port}")
    print(f"   URL: http://localhost:{port}")
    print(f"   WebSocket: ws://localhost:{port}/ws/{{session_id}}")
    
    print(f"\n🔄 Modo: Auto-reload ativado")
    print(f"\n{'=' * 60}")
    print("Pressione Ctrl+C para parar o servidor")
    print("=" * 60 + "\n")
    
    try:
        # Iniciar uvicorn
        subprocess.run([
            sys.executable,
            "-m", "uvicorn",
            "sofia.api_web:app",
            "--reload",
            "--host", host,
            "--port", str(port)
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 Servidor parado pelo usuário")
        print("=" * 60)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n\n❌ ERRO ao iniciar servidor: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    iniciar_api()
