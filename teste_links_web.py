#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Verificar se Sofia fornece links nas buscas web
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
os.environ["SOFIA_MODO_WEB"] = "1"  # Ativa modo web

from sofia.core import cerebro

def testar_busca_com_links():
    """Testa se Sofia fornece os links utilizados na busca"""
    
    print("="*60)
    print("TESTE: Sofia deve fornecer links nas buscas web")
    print("="*60)
    
    pergunta = "Busque sobre inteligência artificial na medicina"
    
    print(f"\n📝 Pergunta: {pergunta}")
    print("\nProcessando...")
    
    resposta = cerebro.perguntar(pergunta, historico=[], usuario="Usuário")
    
    print("\n" + "="*60)
    print("🌸 Resposta de Sofia:")
    print("="*60)
    print(resposta)
    print("="*60)
    
    # Verificar se há links na resposta
    tem_http = "http" in resposta.lower()
    tem_https = "https" in resposta.lower()
    tem_link_palavra = "link" in resposta.lower() or "fonte" in resposta.lower()
    
    print("\n" + "="*60)
    print("ANÁLISE:")
    print("="*60)
    
    if tem_http or tem_https:
        print("✅ Resposta contém URLs (http/https)")
    else:
        print("❌ Resposta NÃO contém URLs")
    
    if tem_link_palavra:
        print("✅ Resposta menciona 'link' ou 'fonte'")
    else:
        print("⚠️ Resposta não menciona explicitamente 'link' ou 'fonte'")
    
    if (tem_http or tem_https) and tem_link_palavra:
        print("\n✅ TESTE PASSOU: Sofia forneceu os links!")
    else:
        print("\n⚠️ ATENÇÃO: Verifique se os links estão visíveis na resposta")

if __name__ == "__main__":
    testar_busca_com_links()
