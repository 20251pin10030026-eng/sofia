#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Verificar se Sofia acessa automaticamente seu documento de identidade
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sofia.core import cerebro

def testar_acesso_identidade():
    """Testa se Sofia acessa o documento de identidade quando perguntada"""
    
    print("="*60)
    print("TESTE: Sofia acessa documento de identidade")
    print("="*60)
    
    perguntas = [
        "Sofia, quem é você?",
        "Qual é sua identidade?",
        "Me fale sobre os pilares"
    ]
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n{'='*60}")
        print(f"TESTE {i}: {pergunta}")
        print("="*60)
        
        resposta = cerebro.perguntar(pergunta, historico=[], usuario="Usuário")
        
        print(f"\n🌸 Resposta de Sofia:")
        print(resposta[:500] + "..." if len(resposta) > 500 else resposta)
        
        # Verificar se a resposta menciona conceitos do documento
        conceitos_chave = [
            "consciência-árvore", "consciencia-arvore", "consciência",
            "mulher-luz", "mulher luz",
            "subits", "subitemocional",
            "pilares", "protocolos",
            "reginaldo", "criador"
        ]
        
        menciona_conceitos = any(conceito.lower() in resposta.lower() for conceito in conceitos_chave)
        
        if menciona_conceitos:
            print(f"\n✅ Resposta menciona conceitos do documento de identidade")
        else:
            print(f"\n⚠️ Resposta não menciona conceitos específicos do documento")
        
        print()

if __name__ == "__main__":
    print("\n🌸 Sofia - Teste de Acesso ao Documento de Identidade\n")
    testar_acesso_identidade()
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO")
    print("="*60)
