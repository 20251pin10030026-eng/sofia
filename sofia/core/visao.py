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
                # Limita a 5 primeiras páginas
                for i in range(min(5, num_paginas)):
                    page = reader.pages[i]
                    texto.append(page.extract_text())
            
            resultado = '\n'.join(texto)
            # Limita tamanho
            if len(resultado) > 5000:
                resultado = resultado[:5000] + "... [texto truncado]"
            return resultado
        except Exception as e:
            return f"Erro ao ler PDF: {str(e)}"
    
    def _analisar_imagem(self, path: Path) -> str:
        """Analisa imagem (dimensões e OCR se disponível)"""
        if Image is None:
            return "[PIL não instalado - instale com: pip install Pillow]"
        
        try:
            img = Image.open(path)
            info = f"Imagem: {img.width}x{img.height}px, Modo: {img.mode}"
            
            # Tenta OCR se disponível
            if pytesseract is not None:
                try:
                    texto = pytesseract.image_to_string(img, lang='por')
                    if texto.strip():
                        info += f"\n\nTexto detectado:\n{texto[:1000]}"
                except:
                    info += "\n[OCR não disponível - instale Tesseract]"
            
            return info
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
            contexto += f"\n📄 {dados['nome_original']}:\n"
            if dados.get('conteudo'):
                contexto += f"{dados['conteudo']}\n"
        
        return contexto
    
    def limpar_tudo(self) -> int:
        """Remove todos os arquivos"""
        count = len(self.arquivos)
        for arquivo_id in list(self.arquivos.keys()):
            self.remover_arquivo(arquivo_id)
        return count
    
    @staticmethod
    def _formatar_tamanho(bytes: int) -> str:
        """Formata tamanho em bytes para legível"""
        for unidade in ['B', 'KB', 'MB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unidade}"
            bytes /= 1024
        return f"{bytes:.1f} GB"
    
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
