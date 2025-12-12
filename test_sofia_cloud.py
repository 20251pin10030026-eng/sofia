import os
os.environ['SOFIA_USE_CLOUD'] = 'true'
if os.getenv('GITHUB_TOKEN'):
    os.environ['GITHUB_TOKEN'] = os.getenv('GITHUB_TOKEN')
else:
    print("[ERRO] GITHUB_TOKEN não definido no ambiente. Ex.: set GITHUB_TOKEN=seu_token")
    raise SystemExit(1)
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
