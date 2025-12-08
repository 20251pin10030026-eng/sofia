#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofia - Assistente Virtual (Main)
Versão: 1.2
- Chama quem conversa de "Usuário"
- Ativa Modo Criador quando detectar "SomBRaRPC"/"SomBRaRCP" ou a frase
  "Desperte, minha luz do mundo real."
"""

import os
from sofia.core import identidade, cerebro, memoria


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
    print("  - 'sair', 'exit' ou 'quit' → encerra")
    print("=" * 60)
    print()


def main() -> None:
    """
    Loop principal de linha de comando.

    Mantém o comportamento básico:
    - conversa normal usando cerebro.perguntar;
    - registra a resposta em memoria.adicionar_resposta_sofia (se existir).
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

        # ----- FLUXO NORMAL: resposta única -----
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
