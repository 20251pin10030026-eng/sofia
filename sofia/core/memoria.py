"""
Memória simples de conversas
"""

historico = []

def adicionar(usuario, mensagem):
    """Adiciona uma mensagem ao histórico"""
    historico.append({
        "de": usuario,
        "texto": mensagem
    })
    
    # Limita a 20 mensagens para não sobrecarregar
    if len(historico) > 20:
        historico.pop(0)

def ver_historico():
    """Mostra o histórico de conversas"""
    if not historico:
        return "📭 Nenhuma conversa ainda."
    
    texto = "\n📚 Últimas conversas:\n" + "-"*40 + "\n"
    for msg in historico[-5:]:  # Últimas 5
        texto += f"{msg['de']}: {msg['texto']}\n"
    return texto

def limpar():
    """Limpa o histórico"""
    global historico
    historico = []
    print("🧹 Memória limpa!")