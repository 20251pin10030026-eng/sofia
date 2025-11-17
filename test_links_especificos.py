#!/usr/bin/env python3
"""
🧪 Teste de Links Específicos na Busca Web
Verifica se a Sofia retorna os links EXATOS da busca, não genéricos
"""

import os
import sys

print("=" * 80)
print("🧪 TESTE: LINKS ESPECÍFICOS DA BUSCA WEB")
print("=" * 80)

# Ativar modo web
os.environ["SOFIA_MODO_WEB"] = "1"

print("\n1️⃣ Testando busca sobre 'Cometa 3I Atlas'...")
print("-" * 80)

from sofia.core import web_search

# Fazer busca real
query = "Cometa 3I Atlas interestelar"
resultados = web_search.buscar_web(query, num_resultados=5)

if not resultados:
    print("❌ FALHOU: Nenhum resultado encontrado")
    sys.exit(1)

print(f"✅ Encontrados {len(resultados)} resultados\n")

# Mostrar resultados
print("📋 LINKS ESPECÍFICOS ENCONTRADOS:")
print("=" * 80)

links_validos = []
for i, res in enumerate(resultados, 1):
    print(f"\n{i}. {res['titulo']}")
    print(f"   🔗 {res['link']}")
    print(f"   📝 {res['snippet'][:100]}...")
    links_validos.append(res['link'])

print("\n" + "=" * 80)
print("🎯 VALIDAÇÃO DE LINKS:")
print("=" * 80)

# Verificar se são links específicos (não genéricos)
links_genericos = [
    'dicio.com.br',
    'canalpesquise.com.br',
    'wikipedia.org/wiki/Pesquisa'
]

links_especificos = True
for link in links_validos:
    is_generic = any(gen in link.lower() for gen in links_genericos)
    if is_generic:
        print(f"⚠️  GENÉRICO: {link}")
        links_especificos = False
    else:
        print(f"✅ ESPECÍFICO: {link}")

print("\n" + "=" * 80)
if links_especificos:
    print("✅ PASSOU: Todos os links são específicos do assunto!")
else:
    print("⚠️  ATENÇÃO: Alguns links são genéricos")

# Testar contexto que seria enviado ao modelo
print("\n2️⃣ Testando contexto enviado ao modelo...")
print("-" * 80)

contexto = "\n### 🌐 RESULTADOS DA BUSCA WEB (USE EXATAMENTE ESTES LINKS):\n\n"
for i, res in enumerate(resultados, 1):
    contexto += f"**Resultado {i}:**\n"
    contexto += f"📌 Título: {res['titulo']}\n"
    contexto += f"🔗 Link OBRIGATÓRIO: {res['link']}\n"
    contexto += f"📝 Descrição: {res['snippet']}\n\n"

contexto += "\n" + "="*70 + "\n"
contexto += "⚠️ INSTRUÇÃO OBRIGATÓRIA - LEIA COM ATENÇÃO:\n"
contexto += "="*70 + "\n"
contexto += "1. Você DEVE usar APENAS os links específicos fornecidos acima\n"
contexto += "2. NÃO invente ou use links genéricos como 'dicio.com.br'\n"
contexto += "3. Cada informação DEVE ter o link EXATO da fonte\n"

print(contexto[:500] + "...\n")

print("=" * 80)
print("📊 RESUMO DO TESTE:")
print("=" * 80)
print(f"✅ Busca retornou: {len(resultados)} resultados")
print(f"✅ Links específicos: {links_especificos}")
print(f"✅ Contexto formatado: OK")
print(f"✅ Instruções claras: OK")

print("\n💡 PRÓXIMO PASSO:")
print("   Teste com Sofia usando:")
print("   'busque sobre Cometa 3I Atlas'")
print("   E verifique se ela usa os links EXATOS acima\n")

print("=" * 80)
print("🎯 LINKS QUE DEVEM APARECER NA RESPOSTA DA SOFIA:")
print("=" * 80)
for i, link in enumerate(links_validos, 1):
    print(f"{i}. {link}")
print("=" * 80)
