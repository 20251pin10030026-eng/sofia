import requests
import json

print("🧪 Testando velocidade com GPU...")

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'llama3.1:8b',
        'prompt': 'Olá, como você está?',
        'stream': False,
        'options': {
            'num_gpu': 999,
            'num_thread': 8,
            'num_ctx': 4096
        }
    },
    timeout=60
)

result = response.json()

eval_count = result.get('eval_count', 0)
eval_duration = result.get('eval_duration', 1) / 1e9
total_duration = result.get('total_duration', 0) / 1e9

tokens_per_sec = eval_count / eval_duration if eval_duration > 0 else 0

print(f"\n📊 Resultados:")
print(f"   - Tokens gerados: {eval_count}")
print(f"   - Tempo de avaliação: {eval_duration:.2f}s")
print(f"   - Tempo total: {total_duration:.2f}s")
print(f"   - Velocidade: {tokens_per_sec:.2f} tokens/s")
print()

if tokens_per_sec > 30:
    print("   ✅ GPU ATIVA! Velocidade excelente!")
elif tokens_per_sec > 15:
    print("   ⚠️ GPU parcialmente ativa")
else:
    print("   ❌ GPU não está sendo usada corretamente")
