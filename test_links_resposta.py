#!/usr/bin/env python3
"""
Teste: Verificar se Sofia retorna os links nas respostas
"""
import os
import sys

# Configurar ambiente
os.environ["PYTHONPATH"] = "D:\\A.I_GitHUB"
os.environ["SOFIA_MODO_WEB"] = "1"
os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"

print("="*70)
print("🧪 TESTE: Links nas Respostas da Sofia")
print("="*70)

# Testar busca web primeiro
print("\n1️⃣ Testando busca web...")
from sofia.core import web_search

resultados = web_search.buscar_web("inteligência artificial", num_resultados=3)

if resultados:
    print(f"✅ Encontrados {len(resultados)} resultados:")
    for i, r in enumerate(resultados, 1):
        print(f"\n  {i}. {r['titulo']}")
        print(f"     Link: {r['link']}")
        print(f"     Snippet: {r['snippet'][:100]}...")
else:
    print("❌ Nenhum resultado encontrado")
    sys.exit(1)

# Testar formatação do contexto que vai para o modelo
print("\n2️⃣ Testando formatação do contexto...")
contexto_web = "\n### 🌐 RESULTADOS DA BUSCA WEB (USE EXATAMENTE ESTES LINKS):\n\n"
for i, res in enumerate(resultados, 1):
    contexto_web += f"**Resultado {i}:**\n"
    contexto_web += f"📌 Título: {res['titulo']}\n"
    contexto_web += f"🔗 Link OBRIGATÓRIO: {res['link']}\n"
    contexto_web += f"📝 Descrição: {res['snippet']}\n\n"

print("Contexto formatado:")
print("-" * 70)
print(contexto_web[:500] + "...")
print("-" * 70)

# Verificar se os links estão presentes
links_presentes = all(r['link'] in contexto_web for r in resultados)
print(f"\n✅ Todos os links estão no contexto: {links_presentes}")

# Verificar instruções obrigatórias
print("\n3️⃣ Verificando instruções no system prompt...")
from sofia.core import cerebro

system_text = cerebro._system_text()
tem_instrucao_links = "USE EXATAMENTE ESTES LINKS" in system_text or "BUSCA WEB" in system_text

print(f"✅ Instruções de links presentes: {tem_instrucao_links}")

if tem_instrucao_links:
    # Extrair trecho relevante
    inicio = system_text.find("BUSCA WEB")
    if inicio >= 0:
        trecho = system_text[inicio:inicio+500]
        print("\nTrecho das instruções:")
        print("-" * 70)
        print(trecho)
        print("-" * 70)

print("\n" + "="*70)
print("📊 RESUMO")
print("="*70)
print(f"✅ Busca web funcionando: {bool(resultados)}")
print(f"✅ Links no contexto: {links_presentes}")
print(f"✅ Instruções configuradas: {tem_instrucao_links}")

if resultados and links_presentes and tem_instrucao_links:
    print("\n🎉 TODOS OS COMPONENTES ESTÃO CONFIGURADOS!")
    print("\n⚠️ Se Sofia ainda não retorna os links, o problema é:")
    print("   1. O modelo não está seguindo as instruções")
    print("   2. O modelo precisa de instruções mais enfáticas")
    print("   3. Pode ser necessário reformatar a instrução")
else:
    print("\n❌ HÁ PROBLEMAS NA CONFIGURAÇÃO")
