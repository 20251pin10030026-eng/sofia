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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            conteudo = '\n\n'.join([p.get_text().strip() for p in paragrafos if p.get_text().strip()])
            
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


def buscar_web(query: str, num_resultados: int = 3) -> Optional[List[Dict[str, str]]]:
    """
    Busca na web usando DuckDuckGo
    
    Args:
        query: Termo de busca
        num_resultados: Número de resultados a retornar
        
    Returns:
        Lista de dicionários com título, link e snippet
    """
    try:
        # Usar ddgs (nova versão do pacote)
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            # Converter iterator para lista
            resultados_raw = list(ddgs.text(query, max_results=num_resultados))
        
        resultados = []
        for resultado in resultados_raw:
            resultados.append({
                'titulo': resultado.get('title', ''),
                'link': resultado.get('href', ''),
                'snippet': resultado.get('body', '')
            })
        
        return resultados if resultados else None
        
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
        conteudo_final += "\n\n**INSTRUÇÃO**: Ao responder sobre este(s) conteúdo(s), SEMPRE mencione o(s) link(s) de origem na sua resposta.\n"
    
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
        'busque', 'pesquise', 'procure na internet', 'procure na web',
        'o que aconteceu', 'notícias sobre', 'última novidade',
        'pesquisa sobre', 'informações sobre', 'buscar sobre'
    ]
    
    texto_lower = texto.lower()
    return any(keyword in texto_lower for keyword in keywords_busca)
