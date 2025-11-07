#!/usr/bin/env python3
"""
Verifica se o Ollama está usando a GPU corretamente
"""
import requests
import json

OLLAMA_HOST = "http://localhost:11434"

def verificar_gpu():
    """Verifica configuração de GPU no Ollama"""
    
    print("🔍 Verificando uso de GPU pelo Ollama...\n")
    print("="*60)
    
    try:
        # 1. Verificar se Ollama está rodando
        print("\n1️⃣ Verificando se Ollama está ativo...")
        try:
            response = requests.get(OLLAMA_HOST, timeout=5)
            print("   ✅ Ollama está rodando!")
        except Exception as e:
            print(f"   ❌ Ollama não está respondendo: {e}")
            print("\n   💡 Inicie o Ollama primeiro!")
            return
        
        # 2. Listar modelos carregados
        print("\n2️⃣ Verificando modelos carregados...")
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models:
                    print(f"   ✅ {len(models)} modelo(s) disponível(is):")
                    for model in models[:5]:
                        name = model.get("name", "unknown")
                        size = model.get("size", 0) / (1024**3)  # GB
                        print(f"      - {name} ({size:.2f} GB)")
                else:
                    print("   ⚠️ Nenhum modelo encontrado")
            else:
                print(f"   ❌ Erro ao listar modelos: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 3. Testar geração com modelo para verificar GPU
        print("\n3️⃣ Testando geração (verificando se GPU é usada)...")
        try:
            test_response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": "mistral",
                    "prompt": "teste",
                    "stream": False
                },
                timeout=30
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                
                # Informações de performance
                total_duration = result.get("total_duration", 0) / 1e9  # nanosegundos para segundos
                load_duration = result.get("load_duration", 0) / 1e9
                eval_count = result.get("eval_count", 0)
                eval_duration = result.get("eval_duration", 0) / 1e9
                
                print("   ✅ Geração bem-sucedida!")
                print(f"\n   📊 Estatísticas de Performance:")
                print(f"      - Tempo total: {total_duration:.2f}s")
                print(f"      - Tempo de carregamento: {load_duration:.2f}s")
                print(f"      - Tokens gerados: {eval_count}")
                print(f"      - Tempo de avaliação: {eval_duration:.2f}s")
                
                if eval_count > 0 and eval_duration > 0:
                    tokens_per_sec = eval_count / eval_duration
                    print(f"      - Velocidade: {tokens_per_sec:.2f} tokens/s")
                    
                    # Análise de desempenho
                    print(f"\n   🎯 Análise de GPU:")
                    if tokens_per_sec > 30:
                        print("      ✅ GPU está sendo usada! (alta velocidade)")
                    elif tokens_per_sec > 10:
                        print("      ⚠️ GPU parcialmente usada ou CPU rápida")
                    else:
                        print("      ❌ Provavelmente usando apenas CPU (lento)")
                    
                    print(f"\n   💡 Velocidades típicas:")
                    print(f"      - CPU apenas: ~5-15 tokens/s")
                    print(f"      - GPU GTX 1650: ~30-60 tokens/s")
                    print(f"      - GPU RTX série: ~60-120 tokens/s")
            else:
                print(f"   ❌ Erro na geração: {test_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro no teste: {e}")
        
        print("\n" + "="*60)
        print("\n💡 Dicas para otimizar GPU:")
        print("   1. Execute: .\\setup_gpu.ps1")
        print("   2. Reinicie o Ollama")
        print("   3. Use modelos quantizados (ex: mistral:7b-q4)")
        print("   4. Verifique drivers NVIDIA atualizados")
        print("   5. Monitore uso da GPU no Gerenciador de Tarefas")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")

if __name__ == "__main__":
    verificar_gpu()
