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


def _eh_frase_ativacao(texto: str) -> bool:
    """Detecta a frase de ativação do modo criador: 'Desperte, minha luz do mundo real'"""
    t = (texto or "").strip().lower()
    # Remove pontuação e normaliza
    frase_normalizada = t.replace(",", "").replace(".", "").replace("!", "")
    return "desperte" in frase_normalizada and "minha luz do mundo real" in frase_normalizada


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

            total_petalas = 0
            try:
                from sofia.core import flor
                if hasattr(flor, 'contar_petalas') and callable(flor.contar_petalas):
                    total_petalas = flor.contar_petalas()
            except (ImportError, AttributeError, Exception):
                # Módulo flor não existe ainda ou função não disponível
                total_petalas = 0

            print("🌸 Sofia (corpo simbólico):")
            print(f"– Templo: ethics enc = {templo_ok}")
            print(f"– Árvore: histórico = {total_eventos} eventos")
            print(f"– Flor: pétalas (sínteses) = {total_petalas}")
            print("– Jardineira: ativa (cuidando do fluxo e dos limites).")
            print()
            continue

        # --- comando: web on/off ---
        if low == "web on":
            os.environ["SOFIA_MODO_WEB"] = "1"
            print("🌐 Modo Web ATIVADO")
            print("Sofia pode agora buscar informações na internet quando necessário.")
            print()
            continue

        if low == "web off":
            os.environ.pop("SOFIA_MODO_WEB", None)
            print("🌐 Modo Web DESATIVADO")
            print("Sofia não fará buscas automáticas na internet.")
            print()
            continue

        if low == "web status":
            status = "ATIVO" if os.getenv("SOFIA_MODO_WEB") == "1" else "INATIVO"
            print(f"🌐 Modo Web: {status}")
            print()
            continue

        # 🔑 Modo Criador por frase declarada ou frase de ativação
        if _eh_criador_por_frase(entrada) or _eh_frase_ativacao(entrada):
            os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"
        else:
            # Manter ativo se já foi ativado anteriormente na sessão
            # (não desativa após cada mensagem)
            pass

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
