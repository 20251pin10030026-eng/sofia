# Links nas Buscas Web - Sofia

## Descrição

Sofia agora **sempre fornece os links** utilizados nas buscas web e no processamento de URLs. Essa funcionalidade garante transparência e permite que o usuário verifique as fontes das informações.

## Como Funciona

### 1. Busca Web Automática

Quando o modo web está ativo e você solicita uma busca:

```
Usuário: Busque sobre inteligência artificial na medicina
```

**Sofia responde com:**
- Informações encontradas
- **Links das fontes** utilizadas (no formato de lista ou inline)

Exemplo de resposta:
```
Fontes:
*   [Inteligência Artificial em Medicina](https://www.who.int/...)
*   [A IA na Medicina: Abordagem Personalizada](https://www.ncbi.nlm.nih.gov/...)
*   [IA em Saúde: Oportunidades](https://www.sciencedirect.com/...)
```

### 2. Processamento de URL Direta

Quando você fornece um link para Sofia processar:

```
Usuário: Resuma este artigo: https://example.com/artigo
```

**Sofia responde com:**
- Resumo do conteúdo
- **Link de origem** claramente identificado

Exemplo de resposta:
```
**Resumo do Conteúdo:**
[Informações extraídas do artigo...]

**Fonte:** Título do Artigo (https://example.com/artigo)
```

## Implementação Técnica

### Modificações Realizadas

#### 1. cerebro.py - Instrução Explícita
```python
# Adiciona instrução para que Sofia sempre mencione os links
contexto_web += "\n**INSTRUÇÃO**: Ao responder, SEMPRE mencione e forneça os links de referência usados."
```

#### 2. web_search.py - Formatação Clara
```python
# Inclui emoji 🔗 e formato consistente
resumo = f"""
📄 **{resultado['titulo']}**
🔗 Link: {resultado['url']}
"""
```

## Ativação do Modo Web

Para usar a busca web, ative o modo web:

### Via Terminal
```bash
python -m sofia.main
```
Depois digite:
```
web on
```

### Via Interface Web
Clique no botão 🌐 ao lado do botão de enviar.

## Testes

Dois scripts de teste estão disponíveis:

### Teste 1: Busca Web
```bash
python teste_links_web.py
```
Verifica se Sofia fornece links em buscas web.

### Teste 2: URL Direta
```bash
python teste_url_direta.py
```
Verifica se Sofia fornece o link ao processar URLs diretas.

## Benefícios

✅ **Transparência**: Usuário sempre sabe de onde vêm as informações  
✅ **Verificabilidade**: Links permitem conferir as fontes  
✅ **Credibilidade**: Respostas baseadas em fontes identificáveis  
✅ **Rastreabilidade**: Fácil retornar às fontes originais

## Exemplos de Uso

### Exemplo 1: Notícias
```
Usuário: Busque as últimas novidades sobre IA
Sofia: [Informações...]

Fontes:
- Artigo 1 (https://...)
- Artigo 2 (https://...)
```

### Exemplo 2: Pesquisa Acadêmica
```
Usuário: Procure sobre machine learning na medicina
Sofia: [Resumo da pesquisa...]

Referências:
1. Título (link)
2. Título (link)
```

### Exemplo 3: Link Específico
```
Usuário: Analise este artigo: https://example.com/paper.pdf
Sofia: [Análise...]

Fonte: Nome do Artigo (https://example.com/paper.pdf)
```

## Status

✅ **Implementado e Testado**
- Buscas web incluem links ✓
- URLs diretas incluem link de origem ✓
- Formato consistente e claro ✓
- Testes automatizados passando ✓

---

**Versão**: 1.0  
**Data**: 07/11/2025  
**Autor**: Sistema Sofia
