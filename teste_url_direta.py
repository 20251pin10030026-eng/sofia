#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Verificar se Sofia fornece links quando processa URLs diretas
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
os.environ["SOFIA_MODO_WEB"] = "1"  # Ativa modo web

from sofia.core import cerebro

def testar_processamento_url_direta():
    """Testa se Sofia fornece o link quando processa uma URL direta"""
    
    print("="*60)
    print("TESTE: Sofia deve fornecer link ao processar URL direta")
    print("="*60)
    
    # Usando uma URL de exemplo (Wikipedia sobre IA)
    pergunta = "Resuma este artigo: https://en.wikipedia.org/wiki/Artificial_intelligence"
    
    print(f"\n📝 Pergunta: {pergunta}")
    print("\nProcessando...")
    
    resposta = cerebro.perguntar(pergunta, historico=[], usuario="Usuário")
    
    print("\n" + "="*60)
    print("🌸 Resposta de Sofia:")
    print("="*60)
    print(resposta)
    print("="*60)
    
    # Verificar se o link está na resposta
    link_original = "wikipedia.org/wiki/Artificial_intelligence"
    tem_link_original = link_original in resposta
    tem_http = "http" in resposta.lower()
    tem_emoji_link = "🔗" in resposta
    
    print("\n" + "="*60)
    print("ANÁLISE:")
    print("="*60)
    
    if tem_link_original:
        print(f"✅ Resposta contém o link original: {link_original}")
    else:
        print(f"❌ Resposta NÃO contém o link original")
    
    if tem_http:
        print("✅ Resposta contém URLs (http/https)")
    else:
        print("❌ Resposta NÃO contém URLs")
    
    if tem_emoji_link:
        print("✅ Resposta usa emoji de link 🔗")
    else:
        print("⚠️ Resposta não usa emoji de link")
    
    if tem_link_original or tem_http:
        print("\n✅ TESTE PASSOU: Sofia forneceu o link de origem!")
    else:
        print("\n❌ TESTE FALHOU: Link não encontrado na resposta")

if __name__ == "__main__":
    testar_processamento_url_direta()
