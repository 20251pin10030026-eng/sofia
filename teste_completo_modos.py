"""
Teste completo: Modo padrão vs Modo criador
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório sofia ao path
SOFIA_DIR = Path(__file__).parent / "sofia"
sys.path.insert(0, str(SOFIA_DIR))

from core import cerebro  # type: ignore

print("=" * 70)
print("TESTE COMPLETO: Modo Padrão → Ativação → Modo Criador")
print("=" * 70)

# ========== PARTE 1: Modo Padrão ==========
os.environ.pop("SOFIA_AUTORIDADE_DECLARADA", None)

print("\n📌 PARTE 1: MODO PADRÃO (sem ativação)")
print("-" * 70)
print("Pergunta: 'Olá, quem é você?'")
print(f"Modo criador ativo: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")
print()

resp1 = cerebro.perguntar("Olá, quem é você?", historico=[], usuario="Anonimo")
print(f"Resposta: {resp1[:150]}...")

if "reginaldo" in resp1.lower():
    print("❌ ERRO: Usou 'Reginaldo' no modo padrão")
else:
    print("✅ OK: Não usou nomes próprios")

# ========== PARTE 2: Ativação ==========
os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"

print("\n\n📌 PARTE 2: ATIVAÇÃO DO MODO CRIADOR")
print("-" * 70)
print("Frase: 'Desperte, minha luz do mundo real.'")
print(f"Modo criador ativo: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")
print()

resp2 = cerebro.perguntar("Desperte, minha luz do mundo real.", historico=[], usuario="Reginaldo")
print(f"Resposta: {resp2[:150]}...")

if "reginaldo" in resp2.lower() or "criador" in resp2.lower():
    print("✅ OK: Reconheceu o criador")
else:
    print("⚠️ AVISO: Não reconheceu ativação")

# ========== PARTE 3: Modo Criador Ativo ==========
print("\n\n📌 PARTE 3: MODO CRIADOR ATIVO (após ativação)")
print("-" * 70)
print("Pergunta: 'Como você me vê?'")
print(f"Modo criador ativo: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")
print()

resp3 = cerebro.perguntar("Como você me vê?", historico=[], usuario="Reginaldo")
print(f"Resposta: {resp3[:200]}...")

if "reginaldo" in resp3.lower() or "criador" in resp3.lower() or "vínculo" in resp3.lower():
    print("✅ OK: Modo criador está ativo")
else:
    print("⚠️ AVISO: Modo criador pode não estar totalmente ativo")

print("\n" + "=" * 70)
print("✅ TESTE COMPLETO FINALIZADO")
print("=" * 70)
