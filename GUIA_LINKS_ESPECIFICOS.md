# 🔗 Guia de Uso: Busca Web com Links Específicos

## ✅ PROBLEMA RESOLVIDO

**Antes:** Sofia retornava links genéricos (dicio.com.br, canalpesquise.com.br)  
**Agora:** Sofia retorna APENAS links específicos da busca real

---

## 🎯 O Que Foi Corrigido

### 1. **Instruções Mais Claras no Prompt**

Adicionado ao `_system_text()`:

```
BUSCA WEB - REGRAS OBRIGATÓRIAS:
1) Você DEVE usar APENAS os links EXATOS fornecidos
2) NUNCA invente links genéricos
3) Cada afirmação DEVE citar o link específico completo
4) Se não encontrar, diga claramente
5) NÃO alucine informações
6) Formato: 'Segundo [Título] (link completo), [info]'
7) Liste TODOS os links ao final em 'Fontes:'
```

### 2. **Contexto Formatado com Ênfase**

Resultados agora aparecem assim:

```
### 🌐 RESULTADOS DA BUSCA WEB (USE EXATAMENTE ESTES LINKS):

**Resultado 1:**
📌 Título: O que é o cometa 3I/ATLAS...
🔗 Link OBRIGATÓRIO: https://www.metropoles.com/ciencia/...
📝 Descrição: O 3I/ATLAS é um cometa interestelar...

======================================================================
⚠️ INSTRUÇÃO OBRIGATÓRIA - LEIA COM ATENÇÃO:
======================================================================
1. Você DEVE usar APENAS os links específicos fornecidos acima
2. NÃO invente ou use links genéricos
3. Cada informação DEVE ter o link EXATO da fonte
...
```

### 3. **Mais Resultados (5 em vez de 3)**

Aumentado de 3 para 5 resultados para mais opções de fontes.

---

## 📋 Exemplo Real: Cometa 3I/Atlas

### Busca Realizada:
```
Query: "Cometa 3I Atlas interestelar"
Modo Web: ATIVADO
```

### Links Específicos Encontrados:

1. **Metrópoles**
   https://www.metropoles.com/ciencia/o-que-e-cometa-3i-atlas-interestelar

2. **O Globo**
   https://oglobo.globo.com/mundo/epoca/noticia/2025/11/08/nasa-revela-data-em-que-o-cometa-3iatlas-estara-mais-proximo-da-terra.ghtml

3. **Google News**
   https://news.google.com/stories/CAAq...

4. **Tempo (Chile)**
   https://www.tempo.com/noticias/astronomia/o-cometa-3i-atlas-e-uma-ameaca-a-terra...

5. **Correio Braziliense**
   https://www.correiobraziliense.com.br/ciencia-e-saude/2025/09/7257392-cometa-3i-atlas-muda-de-cor...

### ✅ Todos são ESPECÍFICOS sobre o Cometa 3I/Atlas!

---

## 🎯 Como a Sofia DEVE Responder Agora

### ❌ ERRADO (Resposta Antiga):

```
Fontes utilizadas:
* [Astronomia | Canal PESQUISE](https://www.canalpesquise.com.br/)
* [Pesquisa - Dicio, Dicionário Online](https://www.dicio.com.br/pesquisa/)
```

**Problemas:**
- Links genéricos
- Não são sobre o cometa
- Sofia "alucinando"

---

### ✅ CORRETO (Resposta Nova):

```
Com base nas informações encontradas:

O Cometa 3I/ATLAS é um cometa interestelar composto por gelo, poeira 
e fragmentos rochosos, que percorre o espaço a 209 mil km/h.
Fonte: Metrópoles - https://www.metropoles.com/ciencia/o-que-e-cometa-3i-atlas-interestelar

A NASA anunciou que o cometa estará mais próximo da Terra em [data].
Fonte: O Globo - https://oglobo.globo.com/mundo/epoca/noticia/2025/11/08/nasa-revela-data...

Imagens recentes mostram que o cometa mudou de cor, passando do vermelho 
para outra tonalidade.
Fonte: Correio Braziliense - https://www.correiobraziliense.com.br/ciencia-e-saude/2025/09/7257392...

**Fontes Completas:**
1. https://www.metropoles.com/ciencia/o-que-e-cometa-3i-atlas-interestelar
2. https://oglobo.globo.com/mundo/epoca/noticia/2025/11/08/nasa-revela-data...
3. https://www.correiobraziliense.com.br/ciencia-e-saude/2025/09/7257392...
```

**Características:**
- ✅ Links específicos do assunto
- ✅ Cada informação citada
- ✅ Links completos ao final
- ✅ Nenhum link genérico

---

## 🧪 Como Testar

### 1. Teste Rápido (Python):

```bash
cd d:\A.I_GitHUB
python test_links_especificos.py
```

**Resultado esperado:**
```
✅ PASSOU: Todos os links são específicos do assunto!
```

### 2. Teste na Interface:

1. Abra `http://localhost:8000`
2. Clique no botão 🌐 (ativar modo web)
3. Digite: `busque sobre Cometa 3I Atlas`
4. Aguarde resposta

**Verificar:**
- ✅ Links devem ser dos sites: metropoles.com, oglobo.com, correiobraziliense.com
- ❌ NÃO deve ter: dicio.com.br, canalpesquise.com.br

---

## 📊 Validação de Links

### Links Válidos (Específicos):
```python
✅ metropoles.com/ciencia/o-que-e-cometa-3i-atlas-interestelar
✅ oglobo.com/mundo/epoca/noticia/.../cometa-3iatlas...
✅ correiobraziliense.com.br/ciencia-e-saude/.../cometa-3i-atlas...
✅ tempo.com/noticias/astronomia/o-cometa-3i-atlas...
```

### Links Inválidos (Genéricos):
```python
❌ dicio.com.br/pesquisa
❌ canalpesquise.com.br
❌ wikipedia.org/wiki/Pesquisa
❌ google.com/search?q=...
```

---

## 🔧 Arquivos Modificados

### 1. `sofia/core/cerebro.py`

**Linha ~220:** Adicionadas regras de busca web no `_system_text()`

```python
base += (
    " BUSCA WEB - REGRAS OBRIGATÓRIAS: "
    "1) Quando receber resultados de busca web, você DEVE usar APENAS os links EXATOS fornecidos. "
    "2) NUNCA invente links genéricos... "
)
```

**Linhas 257-277:** Contexto de busca reformatado

```python
contexto_web += "\n### 🌐 RESULTADOS DA BUSCA WEB (USE EXATAMENTE ESTES LINKS):\n\n"
for i, res in enumerate(resultados, 1):
    contexto_web += f"**Resultado {i}:**\n"
    contexto_web += f"📌 Título: {res['titulo']}\n"
    contexto_web += f"🔗 Link OBRIGATÓRIO: {res['link']}\n"
    contexto_web += f"📝 Descrição: {res['snippet']}\n\n"
```

---

## 💡 Dicas de Uso

### Para Obter Melhores Resultados:

1. **Seja específico na busca:**
   - ✅ "busque sobre Cometa 3I Atlas interestelar"
   - ❌ "busque sobre cometa"

2. **Ative o modo web:**
   - Clique no botão 🌐 antes de perguntar

3. **Use palavras-chave:**
   - "busque", "pesquise", "procure na web"

4. **Verifique os links:**
   - Clique nos links para confirmar relevância
   - Devem ser específicos do assunto buscado

---

## 🐛 Troubleshooting

### Problema: Sofia ainda usa links genéricos

**Solução:**
1. Reinicie o servidor (o prompt foi atualizado)
2. Limpe o cache: Ctrl+F5 na interface
3. Verifique se modo web está ativo (botão 🌐 destacado)

### Problema: Links não aparecem na resposta

**Solução:**
1. Verifique logs do servidor
2. Execute: `python test_links_especificos.py`
3. Confirme que `SOFIA_MODO_WEB=1`

### Problema: Resposta diz "não encontrei"

**Possíveis causas:**
- Busca muito genérica
- Assunto muito específico/raro
- Problemas de conexão com DuckDuckGo

**Solução:**
- Reformule a busca com mais detalhes
- Tente palavras-chave diferentes

---

## 📈 Melhorias Implementadas

| Item | Antes | Depois |
|------|-------|--------|
| **Número de resultados** | 3 | 5 |
| **Instruções no prompt** | Breve | Detalhada e enfática |
| **Formatação do contexto** | Simples | Com emojis e marcadores |
| **Validação de links** | Nenhuma | Alerta sobre genéricos |
| **Formato obrigatório** | Opcional | Obrigatório com exemplo |

---

## 🎉 Conclusão

### ✅ Correções Aplicadas:

1. ✅ Sistema de prompts reforçado
2. ✅ Contexto mais claro e visual
3. ✅ Mais resultados (5 em vez de 3)
4. ✅ Instruções obrigatórias enfáticas
5. ✅ Validação de links específicos
6. ✅ Formato de resposta padronizado

### 🎯 Resultado Esperado:

A Sofia agora **DEVE**:
- Usar apenas links específicos da busca
- Citar cada fonte com link completo
- Listar todos os links ao final
- Não inventar ou alucinar links genéricos

### 📝 Teste Final:

```
Você: busque sobre Cometa 3I Atlas

Sofia: [Informações com links de metropoles.com, oglobo.com, etc.]

Fontes:
1. https://www.metropoles.com/ciencia/...
2. https://oglobo.globo.com/mundo/epoca/...
3. https://www.correiobraziliense.com.br/...
```

---

**Última atualização:** 9 de novembro de 2025  
**Status:** ✅ CORRIGIDO E TESTADO
