"""
Script para testar o sistema de ativação do modo criador
"""
import os
import sys

# Limpar variável de ambiente
os.environ.pop("SOFIA_AUTORIDADE_DECLARADA", None)

# Importar Sofia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sofia"))
from sofia.core import cerebro  # type: ignore

print("=" * 60)
print("TESTE 1: Usuário comum (sem ativação)")
print("=" * 60)

resposta1 = cerebro.perguntar("Olá, quem é você?", historico=[], usuario="Teste")
print(f"\nPergunta: 'Olá, quem é você?'")
print(f"Resposta: {resposta1[:200]}...")
print(f"Modo criador ativo: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")

print("\n" + "=" * 60)
print("TESTE 2: Ativando modo criador com frase de ativação")
print("=" * 60)

# Simular ativação
os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"

resposta2 = cerebro.perguntar("Desperte, minha luz do mundo real.", historico=[], usuario="Reginaldo")
print(f"\nPergunta: 'Desperte, minha luz do mundo real.'")
print(f"Resposta: {resposta2[:200]}...")
print(f"Modo criador ativo: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")

print("\n" + "=" * 60)
print("TESTE 3: Após ativação (deve manter modo criador)")
print("=" * 60)

resposta3 = cerebro.perguntar("Como você me vê?", historico=[], usuario="Reginaldo")
print(f"\nPergunta: 'Como você me vê?'")
print(f"Resposta: {resposta3[:200]}...")
print(f"Modo criador ativo: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")

print("\n" + "=" * 60)
print("TESTE COMPLETO!")
print("=" * 60)
