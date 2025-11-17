"""
Teste das funcionalidades web de Sofia
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório sofia ao path
SOFIA_DIR = Path(__file__).parent / "sofia"
sys.path.insert(0, str(SOFIA_DIR))

from core import cerebro  # type: ignore

print("=" * 70)
print("TESTE: Funcionalidades Web de Sofia")
print("=" * 70)

# ========== TESTE 1: Acessar um Link ==========
print("\n📌 TESTE 1: Acessar Link")
print("-" * 70)

url_teste = "https://www.python.org"
print(f"Pergunta: 'O que tem nesse site? {url_teste}'")
print(f"Modo web: {os.getenv('SOFIA_MODO_WEB') == '1'}")
print()

os.environ.pop("SOFIA_AUTORIDADE_DECLARADA", None)
resp1 = cerebro.perguntar(
    f"O que tem nesse site? {url_teste}", 
    historico=[], 
    usuario="Teste"
)
print(f"Resposta: {resp1[:200]}...")
print()

# ========== TESTE 2: Modo Web ATIVO com Busca ==========
os.environ["SOFIA_MODO_WEB"] = "1"

print("\n📌 TESTE 2: Modo Web Ativo + Busca")
print("-" * 70)
print("Pergunta: 'Busque informações sobre inteligência artificial'")
print(f"Modo web: {os.getenv('SOFIA_MODO_WEB') == '1'}")
print()

resp2 = cerebro.perguntar(
    "Busque informações sobre inteligência artificial", 
    historico=[], 
    usuario="Teste"
)
print(f"Resposta: {resp2[:200]}...")
print()

# ========== TESTE 3: Modo Web INATIVO ==========
os.environ.pop("SOFIA_MODO_WEB", None)

print("\n📌 TESTE 3: Modo Web Inativo")
print("-" * 70)
print("Pergunta: 'Busque sobre Python'")
print(f"Modo web: {os.getenv('SOFIA_MODO_WEB') == '1'}")
print()

resp3 = cerebro.perguntar(
    "Busque sobre Python", 
    historico=[], 
    usuario="Teste"
)
print(f"Resposta: {resp3[:200]}...")
print()

print("=" * 70)
print("✅ TESTES COMPLETOS")
print("=" * 70)
print()
print("COMANDOS DISPONÍVEIS:")
print("  • web on      - Ativa modo web")
print("  • web off     - Desativa modo web")
print("  • web status  - Verifica status do modo web")
print()
print("FUNCIONALIDADES:")
print("  1. Detecta URLs automaticamente e acessa conteúdo")
print("  2. Com 'web on', busca automaticamente quando palavras-chave detectadas")
print("  3. Palavras-chave: busque, pesquise, procure, notícias sobre, etc.")
