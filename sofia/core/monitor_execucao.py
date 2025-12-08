# monitor_execucao.py
import time
import json
import os
from functools import wraps
from typing import Any, Callable, Dict

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs_execucao")
os.makedirs(LOG_DIR, exist_ok=True)

def monitorar_execucao(nome: str) -> Callable:
    """
    Decorador para medir tempo de execução e registrar parâmetros
    e um resumo do resultado em um arquivo JSONL.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            erro = None
            resultado: Any = None

            try:
                resultado = func(*args, **kwargs)
                return resultado
            except Exception as e:
                erro = str(e)
                raise
            finally:
                fim = time.perf_counter()
                duracao = fim - inicio

                resumo_resultado: Dict[str, Any] = {}
                try:
                    if hasattr(resultado, "shape"):
                        resumo_resultado["shape"] = str(getattr(resultado, "shape", None))
                    elif isinstance(resultado, (list, tuple)):
                        resumo_resultado["len"] = len(resultado)
                except Exception:
                    pass

                registro = {
                    "funcao": nome,
                    "duracao_seg": duracao,
                    "args_tipo": [type(a).__name__ for a in args],
                    "kwargs": {k: type(v).__name__ for k, v in kwargs.items()},
                    "resumo_resultado": resumo_resultado,
                    "erro": erro,
                }

                path = os.path.join(LOG_DIR, f"{nome}_log.jsonl")
                try:
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
                except Exception:
                    pass

        return wrapper
    return decorator
