#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai conteúdo do PDF "Teoria da Regionalidade Quântica e os (NQCs).pdf" e salva na memória
Similar ao processo usado com o documento de identidade
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import PyPDF2
from sofia.core import memoria

def extrair_pdf_trq():
    """Extrai texto do PDF da TRQ e salva na memória"""
    
    pdf_path = Path(__file__).parent / "sofia" / "Teoria da Regionalidade Quântica e os (NQCs).pdf"
    
    if not pdf_path.exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        return False
    
    print("="*60)
    print("EXTRAINDO PDF: Teoria da Regionalidade Quântica")
    print("="*60)
    
    try:
        # Abrir e ler PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_paginas = len(pdf_reader.pages)
            
            print(f"\n📄 Total de páginas: {num_paginas}")
            
            # Extrair texto de todas as páginas
            texto_completo = []
            for i, pagina in enumerate(pdf_reader.pages, 1):
                texto = pagina.extract_text()
                if texto.strip():
                    texto_completo.append(f"=== PÁGINA {i} ===\n{texto}\n")
                    print(f"✓ Página {i} extraída ({len(texto)} caracteres)")
            
            # Juntar todo o texto
            conteudo_final = "\n".join(texto_completo)
            
            print(f"\n📊 Total extraído: {len(conteudo_final)} caracteres")
            
            # Salvar na memória como aprendizado
            print("\n💾 Salvando na memória de Sofia...")
            
            # Criar estrutura com metadados
            dados_completos = {
                "tipo": "documento_pdf",
                "arquivo": "Teoria da Regionalidade Quântica e os (NQCs).pdf",
                "paginas": num_paginas,
                "tamanho_caracteres": len(conteudo_final),
                "descricao": "Teoria da Regionalidade Quântica (TRQ) - Teoria física que propõe que a realidade emerge da informação, com densidade informacional como fonte da curvatura do espaço-tempo",
                "conteudo": conteudo_final,
                "topicos": [
                    "Densidade informacional",
                    "Curvatura do espaço-tempo",
                    "Núcleos Quânticos Computacionais (NQCs)",
                    "Tensão da constante de Hubble",
                    "Expansão acelerada do universo",
                    "Fundo de Radiação Gravitacional Quântico (RGFQ)",
                    "Física da matéria condensada"
                ]
            }
            
            memoria.aprender(
                chave="teoria_regionalidade_quantica",
                valor=dados_completos,
                categoria="teorias_cientificas"
            )
            
            # Salvar imediatamente
            memoria.salvar_tudo()
            
            print("✅ Conteúdo salvo com sucesso na memória!")
            print(f"\n📋 Categoria: teorias_cientificas")
            print(f"🔑 Chave: teoria_regionalidade_quantica")
            
            # Mostrar preview
            print("\n" + "="*60)
            print("PREVIEW DO CONTEÚDO (primeiros 500 caracteres):")
            print("="*60)
            print(conteudo_final[:500] + "...")
            print("="*60)
            
            return True
            
    except Exception as e:
        print(f"\n❌ Erro ao processar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_memoria():
    """Verifica se o conteúdo foi salvo corretamente"""
    print("\n" + "="*60)
    print("VERIFICANDO MEMÓRIA")
    print("="*60)
    
    # Buscar o aprendizado
    resultado = memoria.buscar_aprendizado("teoria_regionalidade_quantica", "teorias_cientificas")
    
    if resultado:
        print("✅ Conteúdo encontrado na memória!")
        
        valor = resultado.get('valor', {})
        if isinstance(valor, dict):
            print(f"\n📊 Informações:")
            print(f"   - Tipo: {valor.get('tipo')}")
            print(f"   - Arquivo: {valor.get('arquivo')}")
            print(f"   - Páginas: {valor.get('paginas')}")
            print(f"   - Caracteres: {valor.get('tamanho_caracteres')}")
            print(f"   - Descrição: {valor.get('descricao')}")
            print(f"   - Frequência de acesso: {resultado.get('frequencia', 0)}")
            
            topicos = valor.get('topicos', [])
            if topicos:
                print(f"\n📚 Tópicos principais:")
                for topico in topicos:
                    print(f"   - {topico}")
            
            # Mostrar preview do conteúdo
            conteudo = valor.get('conteudo', '')
            print(f"\n📄 Preview (primeiros 300 caracteres):")
            print(conteudo[:300] + "...")
        else:
            print(f"\n📄 Preview:")
            print(str(valor)[:300] + "...")
        
        return True
    else:
        print("❌ Conteúdo NÃO encontrado na memória")
        return False

if __name__ == "__main__":
    print("\n🌸 Sofia - Extrator de PDF da TRQ\n")
    
    # Extrair e salvar
    sucesso = extrair_pdf_trq()
    
    if sucesso:
        # Verificar
        verificar_memoria()
        
        print("\n" + "="*60)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\nSofia agora tem acesso à 'Teoria da Regionalidade Quântica'")
        print("na categoria 'teorias_cientificas' com a chave 'teoria_regionalidade_quantica'")
    else:
        print("\n❌ Processo falhou. Verifique os erros acima.")
