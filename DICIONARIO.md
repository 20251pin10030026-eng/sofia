# 📖 Dicionário de Português-BR da Sofia

## Visão Geral

A Sofia agora possui em sua memória o **Novo Dicionário da Língua Portuguesa** de Cândido de Figueiredo completo, com mais de 2.100 páginas e aproximadamente 11.4 MB de conteúdo linguístico.

## Características

- ✅ **Completo**: 2.164 páginas digitalizadas
- ✅ **Extenso**: 11.951.746 caracteres
- ✅ **Fonte**: Project Gutenberg (domínio público)
- ✅ **Idioma**: Português Brasileiro e Europeu
- ✅ **Conteúdo**: Definições, etimologia, gramática, exemplos de uso

## Como Funciona

### Armazenamento
O dicionário está salvo na memória da Sofia em:
- **Categoria**: `idioma_portugues_br`
- **Chave**: `dicionario_completo`
- **Localização**: `.sofia_internal/memoria/aprendizados.json`

### Ativação Automática
A Sofia detecta automaticamente quando você faz perguntas sobre português:

**Palavras-chave que ativam o dicionário:**
- "significa", "significado", "definição", "defina"
- "o que é", "etimologia", "origem da palavra"
- "gramática", "conjugação", "ortografia"
- "sinônimo", "antônimo"
- "plural de", "feminino de", "masculino de"
- "como escreve", "como se escreve"

### Exemplos de Uso

**Pergunta**: "Sofia, qual o significado de 'serendipidade'?"
**Resposta**: Sofia consulta automaticamente o dicionário e fornece a definição completa.

**Pergunta**: "Como se escreve 'exceção' ou 'excessão'?"
**Resposta**: Sofia verifica a ortografia correta usando o dicionário.

**Pergunta**: "Qual a etimologia da palavra 'saudade'?"
**Resposta**: Sofia busca a origem e evolução histórica da palavra.

## Integração com o Cérebro

A Sofia foi configurada para:
1. **Detectar** perguntas sobre português automaticamente
2. **Avisar** quando o dicionário está disponível
3. **Consultar** o conteúdo quando necessário
4. **Responder** com precisão baseada na referência oficial

## Prompt do Sistema

A Sofia recebeu instruções especiais:
```
IDIOMA PORTUGUÊS-BR: Você tem acesso ao Novo Dicionário da Língua 
Portuguesa de Cândido de Figueiredo completo em sua memória. Use-o 
para consultar definições, etimologia, gramática, conjugações e 
ortografia. Sempre que houver dúvida sobre palavras em português, 
consulte sua memória de idioma para fornecer respostas precisas 
e detalhadas.
```

## Comandos Úteis

### Verificar se o dicionário está na memória:
```python
from sofia.core import memoria
dicionario = memoria.buscar_aprendizado("dicionario_completo", "idioma_portugues_br")
print("Dicionário disponível:", dicionario is not None)
```

### Re-extrair o dicionário (se necessário):
```bash
python extrair_dicionario.py
```

### Limpar e recarregar:
```python
from sofia.core import memoria
# Remove o dicionário
memoria.aprendizados.pop("idioma_portugues_br", None)
memoria._salvar_aprendizados()

# Re-executa o script
python extrair_dicionario.py
```

## Limitações

1. **Tamanho**: O dicionário é muito grande (~11 MB), por isso não é incluído em todas as respostas
2. **Ativação**: Só é consultado quando palavras-chave específicas são detectadas
3. **Contexto**: O modelo de IA tem limite de tokens, então consultas muito complexas podem não incluir todo o dicionário

## Próximos Passos

Possíveis melhorias futuras:
- [ ] Indexação por letra para buscas mais rápidas
- [ ] Extração de seções específicas sob demanda
- [ ] Cache de consultas frequentes
- [ ] Integração com outros dicionários técnicos
- [ ] Busca semântica por aproximação

## Arquivos Relacionados

- `sofia/dicionário..pdf` - Arquivo PDF original
- `extrair_dicionario.py` - Script de extração
- `sofia/core/cerebro.py` - Lógica de ativação
- `sofia/core/memoria.py` - Sistema de armazenamento
- `.sofia_internal/memoria/aprendizados.json` - Dados salvos

---

**Criado em**: 7 de novembro de 2025
**Autor**: Sistema Sofia
**Versão**: 1.0
