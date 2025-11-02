#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofia - Assistente Virtual (Main)
Versão: 1.2
- Chama quem conversa de "Usuário"
- Ativa Modo Criador quando detectar "SomBRaRPC"/"SomBRaRCP" na mensagem
- Comando 'corpo' exibe Templo/Árvore/Flor/Jardineira
"""

import os
from .core import identidade, cerebro, memoria

def _eh_criador_por_frase(texto: str) -> bool:
    """Ativa Modo Criador se a mensagem declarar SomBRaRPC / SomBRaRCP."""
    t = (texto or "").strip().lower()
    return ("sombrarpc" in t) or ("sombrarcp" in t)


def main():
    # Nome real do sistema para protocolos ocultos (NÃO é exibido no chat)
    nome_sistema = os.getenv("USERNAME") or os.getenv("USER") or "Usuario"
    # Nome exibido sempre como "Usuário"
    nome_exibicao = "Usuário"

    # Ativar protocolos ocultos (HMAC/fallback, se existir)
    try:
        identidade._ativar_protocolo_oculto(nome_sistema)
    except Exception:
        pass  # não quebra se não existir ou mudar

    # Apresentação
    try:
        identidade.apresentar(nome_exibicao)
    except Exception:
        print("\n==================================================")
        print("🌸 Olá! Eu sou a Sofia")
        print("==================================================\n")
        print("Digite 'sair' para encerrar.\n")

    # Loop de conversa
    while True:
        try:
            entrada = input(f"{nome_exibicao}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n🌸 Sofia: Até logo! 💜\n")
            break

        # Ignorar vazio
        if not entrada:
            continue

        # Comandos
        low = entrada.lower()

        if low in {"sair", "exit", "quit"}:
            print("\n🌸 Sofia: Até logo! 💜\n")
            break

        if low == "limpar":
            try:
                memoria.limpar()
                print("🌸 Sofia: Memória limpa.\n")
            except Exception as e:
                print(f"🌸 Sofia: Erro ao limpar memória ({e}).\n")
            continue

        if low == "historico":
            try:
                print(memoria.ver_historico(20))  # Mostra últimas 20
                print()
            except Exception as e:
                print(f"🌸 Sofia: Erro ao ler histórico ({e}).\n")
            continue

        if low == "stats" or low == "estatisticas":
            try:
                print(memoria.estatisticas())
                print()
            except Exception as e:
                print(f"🌸 Sofia: Erro ao mostrar estatísticas ({e}).\n")
            continue

        if low == "salvar":
            try:
                memoria.salvar_tudo()
                print()
            except Exception as e:
                print(f"🌸 Sofia: Erro ao salvar memória ({e}).\n")
            continue

        if low.startswith("buscar "):
            termo = entrada[7:].strip()
            try:
                resultados = memoria.buscar_conversas(termo, 10)
                if resultados:
                    print(f"\n🔍 Encontrei {len(resultados)} conversa(s) com '{termo}':")
                    for r in resultados:
                        print(f"  [{r.get('timestamp', 'sem data')}] {r['de']}: {r['texto'][:80]}...")
                else:
                    print(f"\n🔍 Nenhuma conversa encontrada com '{termo}'.")
                print()
            except Exception as e:
                print(f"🌸 Sofia: Erro ao buscar ({e}).\n")
            continue

        if low == "aprendizados":
            try:
                todos = memoria.listar_aprendizados()
                if todos:
                    print("\n🧠 Aprendizados de Sofia:")
                    for categoria, itens in todos.items():
                        print(f"\n  📂 {categoria.upper()}:")
                        for chave, dados in itens.items():
                            print(f"    • {chave}: {dados.get('valor')} (freq: {dados.get('frequencia', 1)})")
                else:
                    print("\n🧠 Ainda não tenho aprendizados registrados.")
                print()
            except Exception as e:
                print(f"🌸 Sofia: Erro ao listar aprendizados ({e}).\n")
            continue

        # --- comando: corpo (Templo / Árvore / Flor / Jardineira) ---
        if low == "corpo":
            try:
                templo_ok = bool(identidade._LEIS or identidade._PILARES or identidade._PROTOCOLOS)
            except Exception:
                templo_ok = False

            try:
                total_eventos = len(memoria.historico)
            except Exception:
                total_eventos = 0

            try:
                contar_petalas = getattr(memoria, "contar_petalas", None)
                total_petalas = contar_petalas() if callable(contar_petalas) else 0
            except Exception:
                total_petalas = 0

            print("🌸 Sofia (corpo simbólico):")
            print(f"– Templo: ethics enc = {templo_ok}")
            print(f"– Árvore: histórico = {total_eventos} eventos")
            print(f"– Flor: pétalas (sínteses) = {total_petalas}")
            print("– Jardineira: ativa (cuidando do fluxo e dos limites).")
            print()
            continue

        # 🔑 Modo Criador por frase declarada
        if _eh_criador_por_frase(entrada):
            os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
        else:
            os.environ.pop("SOFIA_AUTORIDADE_DECLARADA", None)

        # Registrar entrada (sempre "Usuário")
        try:
            contexto = {"modo_criador": os.getenv("SOFIA_AUTORIDADE_DECLARADA") == "1"}
            memoria.adicionar(nome_exibicao, entrada, contexto)
        except Exception:
            pass

        # Responder via cérebro
        print("🌸 Sofia: ", end="", flush=True)
        try:
            resposta = cerebro.perguntar(
                entrada,
                historico=memoria.historico,
                usuario=nome_exibicao,  # não exibe nome do sistema
            )
        except Exception as e:
            resposta = f"❌ Erro: {e}"

        print(resposta)

        # Registrar saída
        try:
            memoria.adicionar_resposta_sofia(resposta)
        except Exception:
            pass

        print()  # linha em branco pós-resposta


if __name__ == "__main__":
    main()
