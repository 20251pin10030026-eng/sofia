#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste COMPLETO: Verificar se Sofia retorna links válidos nas respostas
"""
import os
import sys

# Configurar ambiente
os.environ["PYTHONPATH"] = "D:\\A.I_GitHUB"
os.environ["SOFIA_MODO_WEB"] = "1"
os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
os.environ["SOFIA_USE_CLOUD"] = "true"  # Usar modelo cloud
if os.getenv("GITHUB_TOKEN"):
    os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN")
else:
    print("[ERRO] GITHUB_TOKEN não definido no ambiente. Ex.: set GITHUB_TOKEN=seu_token")
    raise SystemExit(1)
os.environ["GITHUB_MODEL"] = "gpt-4o"

print("="*80)
print("🧪 TESTE COMPLETO: Links nas Respostas da Sofia")
print("="*80)

# Importar módulos
print("\n1️⃣ Importando módulos...")
try:
    from sofia.core import web_search, cerebro_cloud as cerebro
    print("✅ Módulos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# Fazer busca web
print("\n2️⃣ Fazendo busca web...")
query = "Python linguagem programação"
resultados = web_search.buscar_web(query, num_resultados=3)

if not resultados:
    print("❌ Nenhum resultado encontrado")
    sys.exit(1)

print(f"✅ Encontrados {len(resultados)} resultados:")
for i, r in enumerate(resultados, 1):
    print(f"\n  [{i}] {r['titulo']}")
    print(f"      🔗 {r['link']}")

# Testar com pergunta real
print("\n3️⃣ Enviando pergunta para Sofia...")
print(f"Pergunta: Busque sobre {query}")
print("\nProcessando... (pode demorar alguns segundos)")

try:
    resposta = cerebro.perguntar(f"Busque sobre {query}")
    # Verificar se contém links
    tem_http = "http://" in resposta or "https://" in resposta
    print(f"  {'✅' if tem_http else '❌'} Contém URLs: {tem_http}")
    # Verificar se os links específicos estão presentes
    links_especificos = [r['link'] for r in resultados]
    links_encontrados = [link for link in links_especificos if link in resposta]
    print(f"\n  Links dos resultados encontrados na resposta:")
    for link in links_especificos:
        presente = link in resposta
        print(f"    {'✅' if presente else '❌'} {link}")
    # Verificar seção "Fontes"
    tem_secao_fontes = "Fonte" in resposta or "fonte" in resposta
    print(f"\n  {'✅' if tem_secao_fontes else '❌'} Tem seção de fontes: {tem_secao_fontes}")
    # Resultado final
    print("\n" + "="*80)
    print("📊 RESULTADO DO TESTE")
    print("="*80)
    if tem_http and len(links_encontrados) > 0 and tem_secao_fontes:
        print("✅ TESTE PASSOU! Sofia está retornando links válidos!")
        print(f"   - {len(links_encontrados)}/{len(links_especificos)} links específicos encontrados")
    elif tem_http and len(links_encontrados) > 0:
        print("⚠️  PARCIALMENTE OK - Links presentes mas sem seção 'Fontes'")
        print(f"   - {len(links_encontrados)}/{len(links_especificos)} links específicos encontrados")
    elif tem_http:
        print("⚠️  ATENÇÃO - Resposta tem URLs mas não são os links específicos da busca")
    else:
        print("❌ FALHOU - Resposta não contém links!")
        print("\n💡 Possíveis problemas:")
        print("   1. Modelo não está seguindo instruções")
        print("   2. Contexto web não foi incluído")
        print("   3. Modo web não foi ativado corretamente")
except Exception as e:
    print(f"\n❌ ERRO durante teste: {e}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)
print("\n" + "="*80)
