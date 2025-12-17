#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resumo do que foi extraído e armazenado na memória de Sofia
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sofia.core import memoria

print("="*70)
print("📚 RESUMO DOS DOCUMENTOS NA MEMÓRIA DE SOFIA")
print("="*70)

# Listar documentos de Sofia
docs_sofia = memoria.listar_aprendizados("documentos_sofia")
teorias = memoria.listar_aprendizados("teorias_cientificas")

todos_docs = {}
if docs_sofia:
    todos_docs.update({"documentos_sofia": docs_sofia})
if teorias:
    todos_docs.update({"teorias_cientificas": teorias})

if not todos_docs:
    print("\n❌ Nenhum documento encontrado")
    print("\nExecute:")
    print("  - python extrair_pdf_identidade.py")
    print("  - python extrair_pdf_trq.py")
else:
    total_docs = sum(len(docs) for docs in todos_docs.values())
    print(f"\n✅ {total_docs} documento(s) encontrado(s):\n")
    
    for categoria, docs in todos_docs.items():
        print(f"\n{'='*70}")
        print(f"📂 CATEGORIA: {categoria}")
        print(f"{'='*70}")
        
        for chave, dados in docs.items():
            print(f"\n🔑 Chave: {chave}")
            print(f"{'-'*70}")
            valor = dados.get('valor', {})
            if isinstance(valor, dict):
                print(f"\n📋 Metadados:")
                print(f"   📁 Arquivo: {valor.get('arquivo', 'N/A')}")
                print(f"   📄 Tipo: {valor.get('tipo', 'N/A')}")
                print(f"   📏 Tamanho: {valor.get('tamanho_caracteres', 0):,} caracteres")
                print(f"   📃 Páginas: {valor.get('paginas', 'N/A')}")
                print(f"   📝 Descrição: {valor.get('descricao', 'N/A')}")
                conteudo = valor.get('conteudo', '')
                palavras = len(conteudo.split()) if conteudo else 0
                linhas = conteudo.count('\n') if conteudo else 0
                print(f"\n📊 Estatísticas:")
                print(f"   - Caracteres: {len(conteudo):,}")
                print(f"   - Palavras: {palavras:,}")
                print(f"   - Linhas: {linhas:,}")
                print(f"\n🔄 Acesso:")
                print(f"   - Salvo em: {dados.get('aprendido_em', 'N/A')}")
                print(f"   - Frequência: {dados.get('frequencia', 0)} consulta(s)")
                print(f"\n📖 Preview (200 caracteres):")
                preview = conteudo[:200]
                print(f"   {preview}...")
            else:
                print(f"\n❌ valor não é um dicionário válido: {valor}")
                conteudo = str(valor)
                print(f"\n📖 Preview (200 caracteres):")
                preview = conteudo[:200]
                print(f"   {preview}...")
        

# Resumo geral
print("="*70)
print("📈 RESUMO GERAL")
print("="*70)

todos_aprendizados = memoria.listar_aprendizados()
total_categorias = len(todos_aprendizados)
total_itens = sum(len(itens) for itens in todos_aprendizados.values())

print(f"\n✅ Total de categorias: {total_categorias}")
print(f"✅ Total de aprendizados: {total_itens}")

print(f"\n📂 Categorias disponíveis:")
for categoria, itens in todos_aprendizados.items():
    print(f"   - {categoria}: {len(itens)} item(ns)")

print("\n" + "="*70)
print("🌸 Sofia tem acesso completo a todos esses documentos!")
print("="*70)
