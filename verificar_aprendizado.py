"""
Script para verificar memória e aprendizados da Sofia
"""
from sofia.core import memoria
import json

print('=' * 60)
print('=== VERIFICAÇÃO DE MEMÓRIA E APRENDIZADOS DA SOFIA ===')
print('=' * 60)

# Memória de conversas
print(f'\n📚 Total de conversas em RAM: {len(memoria.historico)}')

if memoria.historico:
    print('\n🔍 Últimas 5 conversas:')
    for i, conv in enumerate(memoria.historico[-5:], 1):
        de = conv.get('de', 'Desconhecido')
        texto = conv.get('texto', '')[:100]
        timestamp = conv.get('timestamp', 'Sem timestamp')
        print(f'\n{i}. [{de}] em {timestamp}')
        print(f'   "{texto}..."')
else:
    print('\n⚠️ Nenhuma conversa encontrada em memória!')

# Aprendizados
print('\n' + '=' * 60)
print('=== APRENDIZADOS ===')
print('=' * 60)

aprendizados = memoria.listar_aprendizados()

if aprendizados:
    for categoria, itens in aprendizados.items():
        print(f'\n📂 Categoria: {categoria}')
        print(f'   Total de itens: {len(itens)}')
        
        for chave, dados in itens.items():
            valor = dados.get('valor')
            aprendido_em = dados.get('aprendido_em', 'Desconhecido')
            freq = dados.get('frequencia', 0)
            
            print(f'\n   🔹 {chave}')
            print(f'      Valor: {valor}')
            print(f'      Aprendido em: {aprendido_em}')
            print(f'      Frequência: {freq}x')
else:
    print('\n⚠️ Nenhum aprendizado registrado ainda!')

# Estatísticas
print('\n' + '=' * 60)
print('=== ESTATÍSTICAS ===')
print('=' * 60)
print(memoria.estatisticas())

print('\n' + '=' * 60)
print('VERIFICAÇÃO CONCLUÍDA!')
print('=' * 60)
