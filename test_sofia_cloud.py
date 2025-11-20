import os
os.environ['SOFIA_USE_CLOUD'] = 'true'
os.environ['GITHUB_TOKEN'] = 'ghp_REDACTED'
os.environ['GITHUB_MODEL'] = 'gpt-4o'

try:
    from sofia.core.cerebro_cloud import perguntar
except ImportError:
    print("[ERRO] Não foi possível importar 'perguntar' do caminho correto. Verifique o PYTHONPATH ou use importação relativa.")
    perguntar = None

if perguntar:
    print("Testando Sofia com GitHub Models...")
    resposta = perguntar("Ola, voce esta usando GPT-4o?", contexto="test")
    print(f"Resposta: {resposta}")
