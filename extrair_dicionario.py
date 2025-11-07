#!/usr/bin/env python3
"""
Script para extrair texto do dicionário PDF e adicionar na memória da Sofia
"""
import sys
import PyPDF2
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from sofia.core import memoria

def extrair_dicionario():
    """Extrai todo o texto do dicionário PDF"""
    pdf_path = Path(__file__).parent / "sofia" / "dicionário..pdf"
    
    print(f"📖 Abrindo dicionário: {pdf_path.name}")
    
    texto_completo = []
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        total_paginas = len(reader.pages)
        
        print(f"📄 Total de páginas: {total_paginas}")
        print("🔄 Extraindo texto...")
        
        for i, page in enumerate(reader.pages):
            if i % 100 == 0:
                print(f"   Progresso: {i}/{total_paginas} páginas ({i*100//total_paginas}%)")
            
            texto_pagina = page.extract_text()
            if texto_pagina.strip():
                texto_completo.append(texto_pagina)
        
        print(f"✅ Extração concluída!")
    
    return '\n\n'.join(texto_completo)

def adicionar_na_memoria():
    """Adiciona o dicionário na memória da Sofia"""
    print("\n" + "="*60)
    print("ADICIONANDO DICIONÁRIO NA MEMÓRIA DA SOFIA")
    print("="*60 + "\n")
    
    # Extrai texto
    texto_dicionario = extrair_dicionario()
    
    total_chars = len(texto_dicionario)
    print(f"\n📊 Total de caracteres extraídos: {total_chars:,}")
    print(f"📊 Tamanho aproximado: {total_chars / (1024*1024):.2f} MB")
    
    # Prepara o fato importante para adicionar
    fato = f"""DICIONÁRIO DE PORTUGUÊS BRASILEIRO - REFERÊNCIA LINGUÍSTICA

Este é o Novo Dicionário da Língua Portuguesa de Cândido de Figueiredo.
Contém definições completas, etimologia, exemplos de uso e gramática do português brasileiro e europeu.

CONTEÚDO DO DICIONÁRIO:
{texto_dicionario}

---
INSTRUÇÕES DE USO:
- Use este dicionário para consultar significados, etimologia e gramática
- Sempre que houver dúvida sobre uma palavra, consulte este recurso
- Para questões de idioma português-BR, este é sua referência primária
- O dicionário contém variantes brasileiras e europeias do português
"""
    
    print("\n💾 Salvando na memória...")
    
    # Adiciona como aprendizado na categoria "idioma"
    memoria.aprender("dicionario_completo", fato, categoria="idioma_portugues_br")
    
    print("✅ Dicionário adicionado com sucesso à memória da Sofia!")
    print("\n📋 Estatísticas da memória:")
    aprendizados = memoria.listar_aprendizados()
    print(f"   - Aprendizados totais: {len(aprendizados)}")
    print(f"   - Dicionário salvo em: idioma_portugues_br/dicionario_completo")
    
    print("\n" + "="*60)
    print("Sofia agora tem acesso ao dicionário completo de português!")
    print("="*60)

if __name__ == "__main__":
    try:
        adicionar_na_memoria()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
