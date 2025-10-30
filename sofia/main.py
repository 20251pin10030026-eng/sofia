#!/usr/bin/env python3
"""
Sofia - Assistente Virtual
Versão: 1.0
Criado por: SomBRaRCP
"""

from core import identidade, cerebro, memoria

def main():
    # Detectar usuário (silenciosamente)
    import os
    nome_usuario = os.getenv("USERNAME") or os.getenv("USER") or "Usuário"

    
    # 🔒 Ativação oculta de protocolos especiais
    modo_criador = identidade._ativar_protocolo_oculto(nome_usuario)
    
    # Apresentação normal
    identidade.apresentar(nome_usuario)
    
    # Loop de conversa (aparentemente simples)
    while True:
        entrada = input(f"{nome_usuario}: ").strip()
        
        # Comandos
        if entrada.lower() in ["sair", "exit"]:
            print("\n🌸 Sofia: Até logo! 💜\n")
            break
            
        if entrada.lower() == "limpar":
            memoria.limpar()
            continue
            
        if entrada.lower() == "historico":
            print(memoria.ver_historico())
            continue
            
        if not entrada:
            continue
        
        # Adicionar à memória
        memoria.adicionar(nome_usuario, entrada)
        
        # 🔒 Processar com sistema oculto
        print("🌸 Sofia: ", end="", flush=True)
        resposta = cerebro.perguntar(
            entrada, 
            historico=memoria.historico,
            usuario=nome_usuario  # Passa usuário para verificação interna
        )
        print(resposta)
        
        # Salvar resposta
        memoria.adicionar("Sofia", resposta)
        print()

if __name__ == "__main__":
    main()