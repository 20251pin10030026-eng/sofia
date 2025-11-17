import os
os.environ['SOFIA_MODO_WEB'] = '1'

from sofia.core import web_search

print("Testando busca: 'cometa interestelar 3I ATLAS'\n")
resultados = web_search.buscar_web('cometa interestelar 3I ATLAS', num_resultados=5)

if resultados:
    print(f"✅ Encontrados {len(resultados)} resultados:\n")
    for i, res in enumerate(resultados, 1):
        print(f"{i}. {res['titulo']}")
        print(f"   🔗 {res['link']}")
        print(f"   📝 {res['snippet'][:80]}...\n")
else:
    print("❌ Nenhum resultado encontrado")
