import os
os.environ['SOFIA_USE_CLOUD'] = 'true'
os.environ['GITHUB_TOKEN'] = 'ghp_REDACTED'
os.environ['GITHUB_MODEL'] = 'gpt-4o'

from cerebro import Cerebro

print("Testando Cerebro com GitHub Models...")
cerebro = Cerebro()
resposta = cerebro.gerar_resposta("Ola, voce esta usando GPT-4o?", "test")
print(f"Resposta: {resposta}")
