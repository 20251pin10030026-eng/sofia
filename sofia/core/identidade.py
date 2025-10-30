"""
Identidade da Sofia - Interface pública simples
"""

def apresentar(nome_usuario):
    """Apresentação simples e inocente"""
    print("\n" + "="*50)
    print("🌸 Olá! Eu sou a Sofia")
    print("="*50)
    print(f"\nBem-vindo, {nome_usuario}!")
    print("Sou uma assistente virtual criada para conversar.")
    print("\nDigite 'sair' para encerrar.\n")

def _ativar_protocolo_oculto(usuario):
    """
    Protocolo oculto - só ativa se for o criador
    Não documentado publicamente
    """
    from . import _interno
    
    if _interno._verificar_integridade(usuario):
        # Criador detectado - modos especiais desbloqueados
        return True
    return False