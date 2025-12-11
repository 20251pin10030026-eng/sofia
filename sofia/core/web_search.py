"""
Módulo de Busca Web para Sofia
Permite buscar informações na internet e acessar links fornecidos
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any
import os

def _is_url(texto: str) -> bool:
    """Verifica se o texto contém uma URL válida"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(url_pattern.search(texto))


def _extrair_urls(texto: str) -> List[str]:
    """Extrai todas as URLs de um texto"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(texto)


def acessar_link(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Acessa um link e extrai o conteúdo principal
    
    Args:
        url: URL para acessar
        timeout: Timeout em segundos
        
    Returns:
        Dict com título, descrição e conteúdo, ou None se falhar
    """
    try:
        # Headers para parecer um navegador real
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair título
        titulo = soup.find('title')
        titulo_texto = titulo.get_text().strip() if titulo else "Sem título"
        
        # Extrair meta descrição
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            descricao = str(content).strip() if content else ""
        else:
            descricao = ""
        
        # Remover scripts e estilos
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extrair texto principal
        # Prioriza elementos main, article, ou pega todo o body
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            # Pega parágrafos
            paragrafos = main_content.find_all('p')
            conteudo = '\n\n'.join(
                [p.get_text().strip() for p in paragrafos if p.get_text().strip()]
            )
            
            # Limita tamanho (primeiros 3000 caracteres)
            if len(conteudo) > 3000:
                conteudo = conteudo[:3000] + "..."
        else:
            conteudo = "Não foi possível extrair o conteúdo principal."
        
        return {
            'url': url,
            'titulo': titulo_texto,
            'descricao': descricao,
            'conteudo': conteudo,
            'sucesso': True
        }
        
    except requests.exceptions.Timeout:
        return {
            'url': url,
            'erro': 'Timeout ao acessar o link',
            'sucesso': False
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'erro': f'Erro ao acessar: {str(e)}',
            'sucesso': False
        }
    except Exception as e:
        return {
            'url': url,
            'erro': f'Erro inesperado: {str(e)}',
            'sucesso': False
        }


# ---------------------- FILTRO DE RELEVÂNCIA ---------------------- #

# Stopwords bem simples PT/EN, para sobrar só o que importa na consulta
_STOPWORDS = {
    # PT – palavras muito genéricas
    "o", "a", "os", "as", "um", "uma",
    "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas",
    "por", "para", "pra", "com",
    "sobre", "que", "e", "ou", "se",
    "é", "foi", "ser",
    "atualizacoes", "atualização", "atualizações", "atualizacao",
    "informacoes", "informação", "informações",
    "noticias", "notícia", "notícias",
    "recentes", "novas", "ultimas", "últimas",

    # Termos de busca genéricos que NÃO devem influenciar relevância
    "busque", "buscar", "busca", "buscas",
    "pesquise", "pesquisa", "pesquisas", "pesquisando",
    "procurar", "procure", "procurando",
    "link", "links",
    "web", "internet", "online",
    "me", "mostre", "mostrar",

    # EN
    "the", "of", "in", "on", "for",
    "and", "or", "is", "are", "to",
    "about", "with", "latest", "news",
    "update", "updates",
}

def _tokenizar_consulta(query: str) -> List[str]:
    """
    Quebra a consulta em tokens relevantes (sem stopwords).
    Ex.: 'Busque atualizações sobre o 3I Atlas' -> ['3i', 'atlas']
    """
    tokens = re.findall(r'\w+', query.lower())
    tokens_filtrados = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
    return tokens_filtrados or tokens  # se tudo virar stopword, volta tokens brutos


def _pontuar_resultado(resultado: Dict[str, str], tokens: List[str]) -> int:
    """
    Dá uma pontuação de relevância a um resultado com base na presença
    dos tokens da consulta no título/snippet.
    """
    titulo = resultado.get('title', '') or resultado.get('titulo', '')
    corpo = resultado.get('body', '') or resultado.get('snippet', '')
    texto_alvo = (titulo + " " + corpo).lower()
    score = 0
    for t in tokens:
        if t in texto_alvo:
            score += 1
    return score


def _dominio_irrelevante(link: str) -> bool:
    """
    Filtra domínios claramente irrelevantes para a nossa busca,
    incluindo dicionários e conjugadores que estavam aparecendo
    quando a intenção era buscar conteúdo técnico/científico.

    Exemplos:
    - Dicionários e conjugadores (quando a consulta é sobre algoritmos, física etc.).
    - Sites genéricos de sinônimos/gramática.
    - Zhihu (resultados em chinês fora de contexto).
    """
    try:
        dominio = urlparse(link).netloc.lower()
    except Exception:
        return False

    # Lista simples de domínios a evitar
    blacklist = [
        "zhihu.com",
        # Dicionários / conjugação / sinônimos que apareceram no seu teste
        "conjugacao.com.br",
        "sinonimos.com.br",
        "infopedia.pt",
        "glosbe.com",
        "dicionarioinformal.com.br",
    ]
    return any(bad in dominio for bad in blacklist)

def buscar_web(query: str, num_resultados: int = 3) -> Optional[List[Dict[str, str]]]:
    """
    Busca na web usando DuckDuckGo, com filtro de relevância.

    Lógica nova:
    - Extrai as palavras importantes da consulta (sem stopwords).
    - Busca na web.
    - Mantém só resultados cujo título/snippet contenham pelo menos
      um desses tokens relevantes.
    - Descarta domínios obviamente fora de contexto (ex.: zhihu).
    - Se nada passar no filtro → retorna None (sem inventar link lixo).
    """
    try:
        # Tentar usar o novo pacote 'ddgs' primeiro
        try:
            from ddgs import DDGS
        except ImportError:
            # Fallback para o pacote antigo
            from duckduckgo_search import DDGS
        
        tokens = _tokenizar_consulta(query)
        
        ddgs = DDGS()
        resultados_raw = list(ddgs.text(query, max_results=num_resultados * 3))
        
        if not resultados_raw:
            return None

        resultados_filtrados: List[Dict[str, str]] = []

        for r in resultados_raw:
            titulo = r.get('title', '') or ''
            link = r.get('href', '') or ''
            snippet = r.get('body', '') or ''

            if not link:
                continue

            # Filtrar domínios irrelevantes
            if _dominio_irrelevante(link):
                continue

            score = _pontuar_resultado(r, tokens)

            # Se nenhum token relevante aparece no título/snippet,
            # provavelmente é resultado genérico ou fora de contexto
            if score <= 0:
                continue

            resultados_filtrados.append({
                'titulo': titulo,
                'link': link,
                'snippet': snippet
            })

        if not resultados_filtrados:
            # Melhor assumir "não achei nada útil" do que inventar coisa errada
            return None

        # Limitar ao número pedido, já com filtro
        return resultados_filtrados[:num_resultados]
        
    except ImportError:
        print("⚠️ Biblioteca duckduckgo-search não instalada. Instale com: pip install duckduckgo-search")
        return None
    except Exception as e:
        print(f"⚠️ Erro ao buscar na web: {e}")
        return None


def processar_urls_no_texto(texto: str) -> Optional[str]:
    """
    Processa URLs encontradas no texto e retorna um resumo do conteúdo
    
    Args:
        texto: Texto que pode conter URLs
        
    Returns:
        String com resumo dos conteúdos acessados, ou None se não houver URLs
    """
    urls = _extrair_urls(texto)
    
    if not urls:
        return None
    
    resumos = []
    for url in urls:
        resultado = acessar_link(url)
        
        if resultado and resultado.get('sucesso'):
            resumo = f"""
📄 **{resultado['titulo']}**
🔗 Link: {resultado['url']}

{resultado.get('descricao', '')}

**Conteúdo:**
{resultado['conteudo'][:500]}...
"""
            resumos.append(resumo)
        else:
            resumos.append(f"❌ Não foi possível acessar: {url}")
    
    conteudo_final = "\n\n---\n\n".join(resumos) if resumos else None
    
    # Adicionar instrução para mencionar os links na resposta
    if conteudo_final:
        conteudo_final += (
            "\n\n**INSTRUÇÃO**: Ao responder sobre este(s) conteúdo(s), "
            "SEMPRE mencione o(s) link(s) de origem na sua resposta.\n"
        )
    
    return conteudo_final


def modo_web_ativo() -> bool:
    """Verifica se o modo web está ativo via variável de ambiente"""
    return os.getenv("SOFIA_MODO_WEB", "0") == "1"


def deve_buscar_web(texto: str) -> bool:
    """
    Determina se deve fazer uma busca web baseado no texto
    
    Critérios:
    - Perguntas sobre eventos atuais
    - Solicitações explícitas de busca
    - Perguntas sobre informações factuais recentes
    """
    # Palavras-chave que indicam necessidade de busca
    keywords_busca = [
        # Comandos diretos de busca
        'busque', 'pesquise', 'procure', 'encontre',
        'procure na internet', 'procure na web',
        'busca online', 'buscas online', 'modo web', 'buscador',
        'buscar sobre', 'pesquisa sobre',
        
        # Pedidos de links/fontes
        'me dê links', 'me dê link', 'me passe links', 'me mande links',
        'compartilhe links', 'envie links', 'manda links', 'links sobre',
        'sites sobre', 'páginas sobre', 'fontes sobre',
        
        # Notícias e atualidades
        'o que aconteceu', 'notícias sobre', 'última novidade',
        'atualizações sobre', 'atualizacoes sobre', 'novidades sobre',
        'últimas notícias', 'notícias recentes', 'acontecimentos',
        
        # Informações atuais
        'informações sobre', 'informacoes sobre',
        'mais recentes', 'mais atuais', 'atual sobre',
        'preço atual', 'cotação', 'valor atual',
        
        # Eventos específicos
        'hoje', 'ontem', 'esta semana', 'este mês', 'este ano',
        '2025', '2024',  # Anos recentes
    ]
    
    texto_lower = texto.lower()
    return any(keyword in texto_lower for keyword in keywords_busca)
