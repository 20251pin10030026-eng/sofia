"""
Teste específico: Sofia não deve usar nomes sem ativação
"""
import os
import sys

# Garantir que variável está limpa
os.environ.pop("SOFIA_AUTORIDADE_DECLARADA", None)

# Importar
sofia_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sofia")
sys.path.insert(0, sofia_path)
try:
    from sofia.core import cerebro  # type: ignore
except ImportError:
    # Tentar importação alternativa com caminho no sys.path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sofia.core import cerebro  # type: ignore

print("=" * 70)
print("TESTE: Sofia NÃO deve usar 'Reginaldo' sem frase de ativação")
print("=" * 70)

# Teste 1: Pergunta simples
print("\n[TESTE 1] Pergunta: 'Olá, quem é você?'")
print(f"Modo criador: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")
print("-" * 70)

resposta = cerebro.perguntar("Olá, quem é você?", historico=[], usuario="TesteAnonimo")
print(f"Resposta: {resposta}\n")

# Verificar se contém "Reginaldo"
if "reginaldo" in resposta.lower():
    print("❌ FALHOU: Sofia usou 'Reginaldo' sem ativação!")
else:
    print("✅ PASSOU: Sofia não usou nomes próprios")

print("\n" + "=" * 70)

# Teste 2: Outra pergunta
print("\n[TESTE 2] Pergunta: 'Como você está?'")
print(f"Modo criador: {os.getenv('SOFIA_AUTORIDADE_DECLARADA') == '1'}")
print("-" * 70)

resposta2 = cerebro.perguntar("Como você está?", historico=[], usuario="TesteAnonimo")
print(f"Resposta: {resposta2}\n")

if "reginaldo" in resposta2.lower():
    print("❌ FALHOU: Sofia usou 'Reginaldo' sem ativação!")
else:
    print("✅ PASSOU: Sofia não usou nomes próprios")

print("\n" + "=" * 70)
print("TESTES COMPLETOS")
print("=" * 70)
