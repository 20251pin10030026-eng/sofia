#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofia - Assistente Virtual (Main)
Versão: 1.3
- Chama quem conversa de "Usuário"
- Ativa Modo Criador quando detectar "SomBRaRPC"/"SomBRaRCP" ou a frase
  "Desperte, minha luz do mundo real."
- Abre Monitor Visual TRQ em janela separada
"""

import os
import sys
import subprocess
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


def _abrir_monitor_visual() -> subprocess.Popen | None:
    """
    Abre o Monitor Visual TRQ em uma janela CMD separada.
    Retorna o processo para poder fechá-lo depois.
    """
    try:
        # Caminho do monitor
        monitor_path = os.path.join(os.path.dirname(__file__), "core", "monitor_visual.py")
        
        if not os.path.exists(monitor_path):
            print("⚠️  Monitor visual não encontrado.")
            return None
        
        # Detectar o Python do ambiente virtual
        python_exe = sys.executable
        
        if os.name == 'nt':  # Windows
            # Abre em nova janela CMD com título personalizado
            cmd = f'start "🧠 Sofia Monitor TRQ" cmd /k "{python_exe}" "{monitor_path}"'
            processo = subprocess.Popen(cmd, shell=True)
        else:  # Linux/Mac
            # Tentar xterm ou gnome-terminal
            try:
                processo = subprocess.Popen(
                    ['gnome-terminal', '--title=Sofia Monitor TRQ', '--', python_exe, monitor_path]
                )
            except FileNotFoundError:
                try:
                    processo = subprocess.Popen(
                        ['xterm', '-T', 'Sofia Monitor TRQ', '-e', python_exe, monitor_path]
                    )
                except FileNotFoundError:
                    print("⚠️  Terminal não encontrado para abrir monitor.")
                    return None
        
        print("📊 Monitor TRQ aberto em janela separada.")
        return processo
    except Exception as e:
        print(f"⚠️  Erro ao abrir monitor: {e}")
        return None


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
    # Abrir monitor visual em janela separada
    monitor_processo = _abrir_monitor_visual()
    
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

        # O cérebro (local/cloud) já registra pergunta+resposta na memória.


if __name__ == "__main__":
    main()
