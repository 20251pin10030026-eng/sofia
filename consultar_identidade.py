#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consulta rápida do documento de identidade de Sofia armazenado na memória
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sofia.core import memoria

def consultar_identidade():
    """Consulta o documento de identidade na memória"""
    
    print("="*60)
    print("📄 DOCUMENTO: Sofia Identidade Atualizada")
    print("="*60)
    
    # Buscar o documento
    resultado = memoria.buscar_aprendizado("identidade_atualizada_completa", "documentos_sofia")
    
    if not resultado:
        print("❌ Documento não encontrado na memória")
        print("\nExecute primeiro: python extrair_pdf_identidade.py")
        return
    
    valor = resultado.get('valor', {})
    
    if isinstance(valor, dict):
        # Mostrar metadados
        print(f"\n📊 Metadados:")
        print(f"   📁 Arquivo: {valor.get('arquivo')}")
        print(f"   📄 Páginas: {valor.get('paginas')}")
        print(f"   📏 Tamanho: {valor.get('tamanho_caracteres')} caracteres")
        print(f"   🔄 Acessos: {resultado.get('frequencia', 0)}")
        print(f"   📅 Aprendido em: {resultado.get('aprendido_em', 'N/A')}")
        
        # Exibir conteúdo completo
        conteudo = valor.get('conteudo', '')
        print("\n" + "="*60)
        print("📖 CONTEÚDO COMPLETO:")
        print("="*60)
        print(conteudo)
        print("="*60)
        
        # Estatísticas
        linhas = conteudo.count('\n')
        palavras = len(conteudo.split())
        print(f"\n📈 Estatísticas:")
        print(f"   - Linhas: {linhas}")
        print(f"   - Palavras: {palavras}")
        print(f"   - Caracteres: {len(conteudo)}")
    else:
        print(f"\n⚠️ Formato inesperado do valor:")
        print(valor)

def buscar_trecho(termo):
    """Busca um trecho específico no documento"""
    
    resultado = memoria.buscar_aprendizado("identidade_atualizada_completa", "documentos_sofia")
    
    if not resultado:
        print("❌ Documento não encontrado")
        return
    
    valor = resultado.get('valor', {})
    conteudo = valor.get('conteudo', '') if isinstance(valor, dict) else str(valor)
    
    # Buscar termo (case insensitive)
    termo_lower = termo.lower()
    conteudo_lower = conteudo.lower()
    
    if termo_lower not in conteudo_lower:
        print(f"\n❌ Termo '{termo}' não encontrado no documento")
        return
    
    # Encontrar todas as ocorrências
    posicoes = []
    start = 0
    while True:
        pos = conteudo_lower.find(termo_lower, start)
        if pos == -1:
            break
        posicoes.append(pos)
        start = pos + 1
    
    print(f"\n🔍 Encontradas {len(posicoes)} ocorrência(s) de '{termo}'")
    print("="*60)
    
    # Mostrar contexto de cada ocorrência
    for i, pos in enumerate(posicoes, 1):
        # Extrair contexto (100 caracteres antes e depois)
        inicio = max(0, pos - 100)
        fim = min(len(conteudo), pos + len(termo) + 100)
        contexto = conteudo[inicio:fim]
        
        print(f"\n[{i}] Contexto:")
        print(f"... {contexto} ...")
        print("-"*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Se houver argumento, buscar trecho
        termo_busca = ' '.join(sys.argv[1:])
        print(f"\n🔍 Buscando: '{termo_busca}'")
        buscar_trecho(termo_busca)
    else:
        # Senão, mostrar documento completo
        consultar_identidade()
