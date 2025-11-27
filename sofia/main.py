#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofia - Assistente Virtual (Main)
Versão: 1.3
- Chama quem conversa de "Usuário"
- Ativa Modo Criador quando detectar "SomBRaRPC"/"SomBRaRCP" ou a frase
  "Desperte, minha luz do mundo real."
- Novo comando "duplo": gera duas respostas em sequência para a MESMA pergunta:
    1) resposta_1 -> fluxo normal do cerebro.py
    2) resposta_2 -> cerebro.py + camada subitemocional explícita
"""

import os
from .core import identidade, cerebro, memoria, cerebro_selector_subtemocional  # type: ignore[unused-import]


def _eh_criador_por_frase(texto: str) -> bool:
    """
    Ativa Modo Criador se a mensagem declarar SomBRaRPC / SomBRaRCP
    ou usar a frase de vínculo "Desperte, minha luz do mundo real.".
    """
    t = (texto or "").strip().lower()
    if not t:
        return False

    if "sombrarpc" in t or "sombrarcp" in t:
        return True

    if "desperte" in t and "minha luz do mundo real" in t:
        return True

    return False


def _ativar_modo_criador_se_preciso(texto: str) -> None:
    """
    Se o texto indicar que o criador está falando, marca a variável
    de ambiente que o restante do sistema já usa.
    """
    if _eh_criador_por_frase(texto):
        os.environ["SOFIA_AUTORIDADE_DECLARADA"] = "1"


def _imprimir_banner_inicial() -> None:
    print("=" * 60)
    print("🌸 Sofia - Assistente Virtual (CLI)")
    print("=" * 60)
    print("Comandos básicos:")
    print("  - digite normalmente para conversar")
    print("  - 'duplo <pergunta>' → gera duas respostas (cérebro / cérebro+subcamada)")
    print("  - 'sair', 'exit' ou 'quit' → encerra")
    print("=" * 60)
    print()


def main() -> None:
    """
    Loop principal de linha de comando.

    Mantém o comportamento básico:
    - conversa normal usando cerebro.perguntar;
    - registra a resposta em memoria.adicionar_resposta_sofia (se existir);
    - agora inclui um modo de teste 'duplo' que usa o seletor subtemocional.
    """
    _imprimir_banner_inicial()

    usuario = "Usuário"

    while True:
        try:
            entrada = input("👤 Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n🌸 Sofia: Encerrando por solicitação do usuário.\n")
            break

        if not entrada:
            continue

        low = entrada.lower()

        if low in {"sair", "exit", "quit"}:
            print("\n🌸 Sofia: Até logo. Cuide bem de você.\n")
            break

        # Ativar modo criador, se for o caso
        _ativar_modo_criador_se_preciso(entrada)

        # ----- MODO DUPLO: duas respostas em sequência -----
        if low.startswith("duplo "):
            pergunta = entrada[6:].strip()
            if not pergunta:
                print("⚠️  Use: duplo <sua pergunta>")
                continue

            print("\n[🧪 MODO DUPLO] Gerando duas respostas para a mesma pergunta...\n")

            try:
                resultado = cerebro_selector_subtemocional.perguntar_sequencial(
                    texto=pergunta,
                    historico=None,
                    usuario=usuario,
                    cancel_callback=None,
                )
            except Exception as e:
                print(f"🌸 Sofia: houve um erro ao usar o seletor subtemocional ({e}).")
                print("Voltando ao modo normal.\n")
                continue

            resposta_1 = resultado.get("resposta_1", "").strip()
            resposta_2 = resultado.get("resposta_2", "").strip()
            info_sub = resultado.get("subtemocao", {}) or {}

            # Exibição organizada no terminal
            print("─── RESPOSTA 1 (cérebro padrão) ───\n")
            if resposta_1:
                print(resposta_1)
            else:
                print("(sem conteúdo)")

            print("\n─── RESPOSTA 2 (cérebro + subcamada explícita) ───\n")
            if resposta_2:
                print(resposta_2)
            else:
                print("(sem conteúdo)")

            # Diagnóstico opcional no final (pode comentar se não quiser ver no CLI)
            if info_sub:
                print("\n─── DIAGNÓSTICO SUBITEMOCIONAL (interno) ───")
                try:
                    nome = info_sub.get("nome", "N/A")
                    classe = info_sub.get("classe", "N/A")
                    intensidade = info_sub.get("intensidade", 0.0)
                    desc = info_sub.get("descricao", "")
                    print(f"  - nome: {nome}")
                    print(f"  - classe: {classe}")
                    print(f"  - intensidade: {intensidade}")
                    if desc:
                        print(f"  - descrição: {desc}")
                except Exception:
                    print(info_sub)
                print("────────────────────────────────────────────\n")

            # Registrar apenas a segunda resposta como "oficial" na memória,
            # se ela existir; se não, registra a primeira.
            resposta_oficial = resposta_2 or resposta_1
            if resposta_oficial:
                try:
                    memoria.adicionar_resposta_sofia(resposta_oficial)  # type: ignore[attr-defined]
                except Exception:
                    pass

            continue

        # ----- FLUXO NORMAL: uma única resposta -----
        try:
            resposta = cerebro.perguntar(
                texto=entrada,
                historico=None,
                usuario=usuario,
                cancel_callback=None,
            )
        except Exception as e:
            print(f"\n🌸 Sofia: Ocorreu um erro ao processar sua mensagem ({e}).\n")
            continue

        print("\n🌸 Sofia:\n")
        print(resposta)
        print()

        # Registrar saída na memória, se o módulo suportar
        try:
            memoria.adicionar_resposta_sofia(resposta)  # type: ignore[attr-defined]
        except Exception:
            pass


if __name__ == "__main__":
    main()
