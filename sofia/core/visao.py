"""
Sistema de Visão da Sofia
Permite upload e análise de imagens e PDFs (até 10 arquivos)
Exclusão automática após 30 minutos
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Importa analisador visual avançado
try:
    from .analisador_visual import analisador
except ImportError:
    analisador = None


class SistemaVisao:
    """Gerencia visualização temporária de arquivos (imagens e PDFs)"""
    
    LIMITE_ARQUIVOS = 10
    TEMPO_EXPIRACAO = 30 * 60  # 30 minutos em segundos
    FORMATOS_IMAGEM = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    FORMATOS_PDF = {'.pdf'}
    TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB por arquivo
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.temp_dir = self.base_dir / '.sofia_internal' / 'temp_files'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.temp_dir / 'metadata.json'
        self.arquivos = self._carregar_metadata()
        
        # Inicia thread de limpeza automática
        self._iniciar_limpeza_automatica()
    
    def _carregar_metadata(self) -> Dict:
        """Carrega metadata dos arquivos temporários"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _salvar_metadata(self):
        """Salva metadata dos arquivos"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.arquivos, f, ensure_ascii=False, indent=2)
    
    def _iniciar_limpeza_automatica(self):
        """Inicia thread que limpa arquivos expirados a cada minuto"""
        def limpar_loop():
            while True:
                time.sleep(60)  # Verifica a cada minuto
                self.limpar_expirados()
        
        thread = threading.Thread(target=limpar_loop, daemon=True)
        thread.start()
    
    def pode_adicionar(self) -> bool:
        """Verifica se pode adicionar mais arquivos"""
        self.limpar_expirados()
        return len(self.arquivos) < self.LIMITE_ARQUIVOS
    
    def adicionar_arquivo(self, arquivo_path: str, nome_original: str) -> Dict:
        """
        Adiciona arquivo ao sistema de visão temporária
        Returns: Dict com sucesso e informações do arquivo
        """
        if not self.pode_adicionar():
            return {
                'sucesso': False,
                'erro': f'Limite de {self.LIMITE_ARQUIVOS} arquivos atingido'
            }
        
        # Verifica extensão
        extensao = Path(nome_original).suffix.lower()
        if extensao not in (self.FORMATOS_IMAGEM | self.FORMATOS_PDF):
            return {
                'sucesso': False,
                'erro': f'Formato não suportado. Use: {", ".join(self.FORMATOS_IMAGEM | self.FORMATOS_PDF)}'
            }
        
        # Verifica tamanho
        tamanho = os.path.getsize(arquivo_path)
        if tamanho > self.TAMANHO_MAXIMO:
            return {
                'sucesso': False,
                'erro': f'Arquivo muito grande. Máximo: {self.TAMANHO_MAXIMO // (1024*1024)} MB'
            }
        
        # Gera ID único
        timestamp = int(time.time() * 1000)
        arquivo_id = f"{timestamp}_{nome_original}"
        destino = self.temp_dir / arquivo_id
        
        # Copia arquivo
        import shutil
        shutil.copy2(arquivo_path, destino)
        
        # Processa conteúdo
        conteudo = self._processar_arquivo(destino, extensao)
        
        # Salva metadata
        self.arquivos[arquivo_id] = {
            'nome_original': nome_original,
            'extensao': extensao,
            'tamanho': tamanho,
            'timestamp': timestamp,
            'expira_em': timestamp + (self.TEMPO_EXPIRACAO * 1000),
            'conteudo': conteudo,
            'path': str(destino)
        }
        self._salvar_metadata()
        
        return {
            'sucesso': True,
            'arquivo_id': arquivo_id,
            'nome': nome_original,
            'tipo': 'imagem' if extensao in self.FORMATOS_IMAGEM else 'pdf',
            'expira_em': self._formatar_tempo_expiracao(timestamp)
        }
    
    def _processar_arquivo(self, path: Path, extensao: str) -> str:
        """Extrai texto/descrição do arquivo"""
        try:
            if extensao in self.FORMATOS_PDF:
                return self._extrair_texto_pdf(path)
            elif extensao in self.FORMATOS_IMAGEM:
                # Usa analisador visual avançado se disponível
                if analisador is not None:
                    return analisador.analisar_imagem_completa(path)
                else:
                    return self._analisar_imagem(path)
        except Exception as e:
            return f"Erro ao processar: {str(e)}"
        return ""
    
    def _extrair_texto_pdf(self, path: Path) -> str:
        """Extrai texto de PDF"""
        if PyPDF2 is None:
            return "[PyPDF2 não instalado - instale com: pip install PyPDF2]"
        
        try:
            texto = []
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_paginas = len(reader.pages)
                # Lê TODAS as páginas
                for i in range(num_paginas):
                    page = reader.pages[i]
                    texto_pagina = page.extract_text()
                    if texto_pagina.strip():  # Só adiciona se tiver conteúdo
                        texto.append(f"=== Página {i+1} ===\n{texto_pagina}")
            
            resultado = '\n\n'.join(texto)
            
            # Se muito grande, resumo as estatísticas mas mantém todo o texto
            info = f"PDF com {num_paginas} páginas, {len(resultado)} caracteres extraídos\n\n"
            return info + resultado
        except Exception as e:
            return f"Erro ao ler PDF: {str(e)}"
    
    def _analisar_imagem(self, path: Path) -> str:
        """Analisa imagem (dimensões, cores, OCR e descrição detalhada)"""
        if Image is None:
            return "[PIL não instalado - instale com: pip install Pillow]"
        
        try:
            img = Image.open(path)
            analise = []
            
            # 1. Informações básicas
            analise.append(f"=== ANÁLISE DE IMAGEM ===")
            analise.append(f"Dimensões: {img.width}x{img.height} pixels")
            analise.append(f"Modo de cor: {img.mode}")
            analise.append(f"Formato: {img.format}")
            
            # 2. Análise de cores dominantes
            img_rgb = img.convert('RGB')
            img_small = img_rgb.resize((50, 50))  # Reduz para análise rápida
            pixels = list(img_small.getdata())  # type: ignore
            
            # Contar cores mais comuns
            from collections import Counter
            color_counts = Counter(pixels)
            top_colors = color_counts.most_common(5)
            
            analise.append("\n=== CORES DOMINANTES ===")
            for i, (color, count) in enumerate(top_colors, 1):
                percentage = (count / len(pixels)) * 100
                r, g, b = color
                analise.append(f"{i}. RGB({r}, {g}, {b}) - {percentage:.1f}%")
            
            # 3. Análise de brilho e contraste
            grayscale = img.convert('L')
            pixels_gray = list(grayscale.getdata())  # type: ignore
            avg_brightness = sum(pixels_gray) / len(pixels_gray)
            
            analise.append(f"\n=== LUMINOSIDADE ===")
            analise.append(f"Brilho médio: {avg_brightness:.1f}/255")
            
            if avg_brightness < 85:
                analise.append("Classificação: Imagem escura")
            elif avg_brightness > 170:
                analise.append("Classificação: Imagem clara")
            else:
                analise.append("Classificação: Brilho médio")
            
            # 4. Análise de complexidade (bordas/detalhes)
            try:
                from PIL import ImageFilter
                edges = img_rgb.filter(ImageFilter.FIND_EDGES)
                edge_data = edges.convert('L').getdata()
                edge_pixels = list(edge_data)  # type: ignore
                edge_density = sum(1 for p in edge_pixels if p > 30) / len(edge_pixels)
                
                analise.append(f"\n=== COMPLEXIDADE ===")
                analise.append(f"Densidade de bordas: {edge_density*100:.1f}%")
                
                if edge_density > 0.3:
                    analise.append("Classificação: Imagem detalhada/complexa")
                elif edge_density > 0.15:
                    analise.append("Classificação: Moderadamente detalhada")
                else:
                    analise.append("Classificação: Simples/uniforme")
            except:
                pass
            
            # 5. Detecção de texto com OCR (se disponível)
            analise.append("\n=== TEXTO DETECTADO ===")
            if pytesseract is not None:
                try:
                    texto = pytesseract.image_to_string(img, lang='por')
                    if texto.strip():
                        analise.append(f"Texto encontrado ({len(texto)} caracteres):")
                        analise.append(texto[:500])  # Primeiros 500 chars
                        if len(texto) > 500:
                            analise.append("... [texto continua]")
                    else:
                        analise.append("Nenhum texto detectado na imagem")
                except Exception as e:
                    analise.append(f"OCR não disponível: {str(e)}")
            else:
                analise.append("[Tesseract OCR não instalado]")
                analise.append("Para reconhecimento de texto, instale: pip install pytesseract")
                analise.append("E instale o Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
            
            # 6. Análise de regiões (quadrantes)
            analise.append("\n=== ANÁLISE POR QUADRANTES ===")
            w, h = img.width, img.height
            quadrantes = {
                'Superior Esquerdo': (0, 0, w//2, h//2),
                'Superior Direito': (w//2, 0, w, h//2),
                'Inferior Esquerdo': (0, h//2, w//2, h),
                'Inferior Direito': (w//2, h//2, w, h)
            }
            
            for nome, (x1, y1, x2, y2) in quadrantes.items():
                region = img_rgb.crop((x1, y1, x2, y2))
                region_small = region.resize((10, 10))
                region_pixels = [pixel for pixel in region_small.getdata()]
                avg_color = tuple(sum(c[i] for c in region_pixels) // len(region_pixels) for i in range(3))
                analise.append(f"{nome}: RGB{avg_color}")
            
            # 7. Metadados EXIF (se disponível)
            try:
                from PIL import Image as PILImage
                exif = img.getexif()
                if exif:
                    analise.append("\n=== METADADOS EXIF ===")
                    # IDs EXIF comuns
                    exif_tags = {
                        271: 'Fabricante',
                        272: 'Modelo',
                        306: 'Data/Hora',
                        36867: 'Data Original',
                        37378: 'Abertura',
                        37385: 'Flash',
                        42036: 'Lente'
                    }
                    for tag_id, tag_name in exif_tags.items():
                        if tag_id in exif:
                            analise.append(f"{tag_name}: {exif[tag_id]}")
            except:
                pass
            
            return '\n'.join(analise)
            
        except Exception as e:
            return f"Erro ao analisar imagem: {str(e)}"
    
    def listar_arquivos(self) -> List[Dict]:
        """Lista todos os arquivos ativos"""
        self.limpar_expirados()
        
        resultado = []
        for arquivo_id, dados in self.arquivos.items():
            resultado.append({
                'id': arquivo_id,
                'nome': dados['nome_original'],
                'tipo': 'imagem' if dados['extensao'] in self.FORMATOS_IMAGEM else 'pdf',
                'tamanho': self._formatar_tamanho(dados['tamanho']),
                'expira_em': self._formatar_tempo_expiracao(dados['timestamp'])
            })
        
        return resultado
    
    def remover_arquivo(self, arquivo_id: str) -> bool:
        """Remove arquivo específico"""
        if arquivo_id not in self.arquivos:
            return False
        
        # Remove arquivo físico
        try:
            path = Path(self.arquivos[arquivo_id]['path'])
            if path.exists():
                path.unlink()
        except:
            pass
        
        # Remove metadata
        del self.arquivos[arquivo_id]
        self._salvar_metadata()
        return True
    
    def limpar_expirados(self) -> int:
        """Remove arquivos expirados. Retorna quantidade removida"""
        agora = int(time.time() * 1000)
        expirados = [
            aid for aid, dados in self.arquivos.items()
            if dados['expira_em'] < agora
        ]
        
        for arquivo_id in expirados:
            self.remover_arquivo(arquivo_id)
        
        return len(expirados)
    
    def obter_contexto_visual(self) -> str:
        """Retorna contexto de todos os arquivos visualizados para o cérebro"""
        self.limpar_expirados()
        
        if not self.arquivos:
            return ""
        
        contexto = "\n\n=== ARQUIVOS VISUALIZADOS ===\n"
        for arquivo_id, dados in self.arquivos.items():
            tipo = dados['extensao']
            
            # Para PDFs, cria variável com o texto
            if tipo in self.FORMATOS_PDF:
                var_name = f"pdftex_{arquivo_id.split('_')[0]}"
                contexto += f"\n📄 PDF: {dados['nome_original']}\n"
                contexto += f"Variável criada: {var_name}\n"
                contexto += f"Conteúdo armazenado em {var_name}:\n"
                if dados.get('conteudo'):
                    contexto += f"{dados['conteudo']}\n"
            else:
                # Para imagens, usa análise visual
                contexto += f"\n🖼️ IMAGEM: {dados['nome_original']}\n"
                if dados.get('conteudo'):
                    contexto += f"{dados['conteudo']}\n"
        
        return contexto
    
    def obter_texto_pdf_para_prompt(self, usuario_prompt: str) -> str:
        """
        Retorna texto dos PDFs no formato: nome_variavel: pdftex + prompt
        """
        self.limpar_expirados()
        
        pdfs = []
        for arquivo_id, dados in self.arquivos.items():
            if dados['extensao'] in self.FORMATOS_PDF:
                # Cria nome da variável
                timestamp = arquivo_id.split('_')[0]
                var_name = f"pdftex_{timestamp}"
                
                # Extrai apenas o texto puro (sem cabeçalhos)
                texto_pdf = dados.get('conteudo', '')
                
                pdfs.append({
                    'variavel': var_name,
                    'nome_arquivo': dados['nome_original'],
                    'texto': texto_pdf
                })
        
        if not pdfs:
            return usuario_prompt
        
        # Monta o prompt com as variáveis
        prompt_final = ""
        for pdf in pdfs:
            prompt_final += f"\n{'='*60}\n"
            prompt_final += f"VARIÁVEL: {pdf['variavel']}\n"
            prompt_final += f"ARQUIVO: {pdf['nome_arquivo']}\n"
            prompt_final += f"{'='*60}\n"
            prompt_final += f"{pdf['texto']}\n\n"
        
        prompt_final += f"\n{'='*60}\n"
        prompt_final += f"PROMPT DO USUÁRIO:\n"
        prompt_final += f"{'='*60}\n"
        prompt_final += usuario_prompt
        
        return prompt_final
    
    def limpar_tudo(self) -> int:
        """Remove todos os arquivos"""
        count = len(self.arquivos)
        for arquivo_id in list(self.arquivos.keys()):
            self.remover_arquivo(arquivo_id)
        return count
    
    @staticmethod
    def _formatar_tamanho(bytes: int) -> str:
        """Formata tamanho em bytes para legível"""
        valor = float(bytes)
        for unidade in ['B', 'KB', 'MB']:
            if valor < 1024:
                return f"{valor:.1f} {unidade}"
            valor /= 1024
        return f"{valor:.1f} GB"
    
    @staticmethod
    def _formatar_tempo_expiracao(timestamp_ms: int) -> str:
        """Formata tempo de expiração"""
        expira_em = timestamp_ms + (SistemaVisao.TEMPO_EXPIRACAO * 1000)
        agora = int(time.time() * 1000)
        diferenca = (expira_em - agora) // 1000
        
        if diferenca <= 0:
            return "Expirado"
        
        minutos = diferenca // 60
        return f"{minutos} min restantes"


# Instância global
visao = SistemaVisao()
