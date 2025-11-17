#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Verificar se Sofia acessa automaticamente a Teoria da Regionalidade Quântica
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sofia.core import cerebro

def testar_acesso_trq():
    """Testa se Sofia acessa a TRQ quando perguntada"""
    
    print("="*60)
    print("TESTE: Sofia acessa TRQ automaticamente")
    print("="*60)
    
    perguntas = [
        "O que é a TRQ?",
        "Me explique a Teoria da Regionalidade Quântica",
        "Como funcionam os Núcleos Quânticos de Convergência?"
    ]
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n{'='*60}")
        print(f"TESTE {i}: {pergunta}")
        print("="*60)
        
        resposta = cerebro.perguntar(pergunta, historico=[], usuario="Usuário")
        
        print(f"\n🌸 Resposta de Sofia:")
        print(resposta[:800] + "..." if len(resposta) > 800 else resposta)
        
        # Verificar se a resposta menciona conceitos da TRQ
        conceitos_chave = [
            "trq", "regionalidade quântica", "regionalidade quantica",
            "nqc", "núcleos quânticos", "nucleos quanticos",
            "densidade informacional", "convergência", "convergencia",
            "reginaldo", "curvatura", "espaço-tempo", "espaco-tempo",
            "cosmologia", "cosmológica"
        ]
        
        menciona_conceitos = any(conceito.lower() in resposta.lower() for conceito in conceitos_chave)
        
        if menciona_conceitos:
            print(f"\n✅ Resposta menciona conceitos da TRQ")
        else:
            print(f"\n⚠️ Resposta não menciona conceitos específicos da TRQ")
        
        print()

if __name__ == "__main__":
    print("\n🌸 Sofia - Teste de Acesso à TRQ\n")
    testar_acesso_trq()
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO")
    print("="*60)
