"""
Analisador Visual Avançado para Sofia
Processa imagens pixel por pixel e gera descrições detalhadas
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

# Initialize to None to ensure it's always defined
Image = None
ImageDraw = None
ImageFilter = None
ImageStat = None

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageStat
except ImportError:
    pass

try:
    import pytesseract
except ImportError:
    pytesseract = None


class AnalisadorVisual:
    """Análise avançada de imagens para IA"""
    
    def __init__(self):
        self.descricao_completa = []
    
    def analisar_imagem_completa(self, path: Path) -> str:
        """
        Análise completa da imagem retornando descrição detalhada
        que permite à IA 'ver' o conteúdo
        """
        if Image is None:
            return "[Pillow não instalado]"
        
        try:
            img = Image.open(path)
            self.descricao_completa = []
            
            # Análises em sequência
            self._analisar_propriedades_basicas(img)
            self._analisar_composicao_cores(img)
            self._analisar_distribuicao_luminosidade(img)
            self._analisar_padroes_visuais(img)
            self._analisar_regioes_interesse(img)
            self._detectar_formas_geometricas(img)
            self._analisar_textura(img)
            self._extrair_texto(img)
            self._analisar_simetria(img)
            
            return '\n\n'.join(self.descricao_completa)
        except Exception as e:
            return f"[Erro ao analisar imagem: {str(e)}]"
            
    def _analisar_propriedades_basicas(self, img: Any):
        """Propriedades fundamentais da imagem"""
        info = [
            "═══ PROPRIEDADES DA IMAGEM ═══",
            f"📐 Dimensões: {img.width} × {img.height} pixels ({img.width * img.height:,} pixels totais)",
            f"🎨 Modo de cor: {img.mode}",
            f"📄 Formato: {img.format}",
        ]
        
        # Orientação
        if img.width > img.height:
            ratio = img.width / img.height
            info.append(f"📱 Orientação: Paisagem (horizontal) - proporção {ratio:.2f}:1")
        elif img.height > img.width:
            ratio = img.height / img.width
            info.append(f"📱 Orientação: Retrato (vertical) - proporção 1:{ratio:.2f}")
        else:
            info.append("📱 Orientação: Quadrada (1:1)")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _analisar_composicao_cores(self, img: Any):
        """Análise detalhada de cores"""
        info = ["═══ COMPOSIÇÃO DE CORES ═══"]
        
        img_rgb = img.convert('RGB')
        
        # Reduz para análise eficiente
        img_sample = img_rgb.resize((100, 100))
        pixels = np.array(img_sample)
        
        # Cores dominantes (clustering simples)
        pixels_flat = pixels.reshape(-1, 3)
        
        # Agrupa cores similares
        from collections import defaultdict
        color_groups = defaultdict(int)
        
        for pixel in pixels_flat:
            # Agrupa em blocos de 32 cores
            grouped = tuple((pixel // 32) * 32)
            color_groups[grouped] += 1
        
        # Top 5 cores
        top_colors = sorted(color_groups.items(), key=lambda x: x[1], reverse=True)[:5]
        total_pixels = len(pixels_flat)
        
        info.append("\n🎨 Cores dominantes:")
        for i, (color, count) in enumerate(top_colors, 1):
            percentage = (count / total_pixels) * 100
            r, g, b = color
            color_name = self._nomear_cor(r, g, b)
            info.append(f"  {i}. {color_name} RGB({r}, {g}, {b}) - {percentage:.1f}%")
        
        # Análise de temperatura de cor
        avg_color = pixels_flat.mean(axis=0)
        r_avg, g_avg, b_avg = avg_color
        
        if r_avg > g_avg and r_avg > b_avg:
            temperatura = "quente (tons avermelhados)"
        elif b_avg > r_avg and b_avg > g_avg:
            temperatura = "fria (tons azulados)"
        else:
            temperatura = "neutra (equilibrada)"
        
        info.append(f"\n🌡️ Temperatura de cor: {temperatura}")
        info.append(f"   Cor média geral: RGB({int(r_avg)}, {int(g_avg)}, {int(b_avg)})")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _analisar_distribuicao_luminosidade(self, img: Any):
        """Análise de brilho e contraste"""
        info = ["═══ LUMINOSIDADE E CONTRASTE ═══"]
        
        grayscale = img.convert('L')
        pixels_array = np.array(grayscale)
        
        mean_brightness = pixels_array.mean()
        std_brightness = pixels_array.std()
        min_brightness = pixels_array.min()
        max_brightness = pixels_array.max()
        
        info.append(f"💡 Brilho médio: {mean_brightness:.1f}/255")
        info.append(f"📊 Contraste (desvio padrão): {std_brightness:.1f}")
        info.append(f"🔲 Range: {min_brightness} - {max_brightness}")
        
        # Classificação
        if mean_brightness < 85:
            classificacao = "escura/sombria"
        elif mean_brightness > 170:
            classificacao = "clara/brilhante"
        else:
            classificacao = "média"
        
        if std_brightness < 40:
            contraste = "baixo contraste (uniforme)"
        elif std_brightness > 70:
            contraste = "alto contraste (dramático)"
        else:
            contraste = "contraste moderado"
        
        info.append(f"🎭 Classificação: Imagem {classificacao} com {contraste}")
        
        # Histograma simplificado
        hist, _ = np.histogram(pixels_array, bins=5, range=(0, 256))
        hist_pct = (hist / hist.sum() * 100).astype(int)
        
        info.append("\n📊 Distribuição de tons:")
        tonalidades = ["Muito escuro", "Escuro", "Médio", "Claro", "Muito claro"]
        for i, (tom, pct) in enumerate(zip(tonalidades, hist_pct)):
            bar = "█" * (pct // 5)
            info.append(f"  {tom:14s}: {bar} {pct}%")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _analisar_padroes_visuais(self, img: Any):
        """Detecta padrões e texturas"""
        info = ["═══ PADRÕES E DETALHES ═══"]
        
        if ImageFilter is None:
            info.append("🔍 (Análise de padrões não disponível - Pillow necessário)")
            self.descricao_completa.append('\n'.join(info))
            return
        
        try:
            # Detecção de bordas
            img_gray = img.convert('L')
            edges = img_gray.filter(ImageFilter.FIND_EDGES)
            edges_array = np.array(edges)
            
            edge_density = (edges_array > 30).sum() / edges_array.size
            
            info.append(f"🔍 Densidade de bordas: {edge_density*100:.1f}%")
            
            if edge_density > 0.3:
                info.append("   Interpretação: Imagem muito detalhada com muitos elementos")
            elif edge_density > 0.15:
                info.append("   Interpretação: Moderadamente detalhada")
            else:
                info.append("   Interpretação: Poucos detalhes, áreas uniformes")
            
            # Análise de nitidez
            laplacian = img_gray.filter(ImageFilter.Kernel((3, 3), 
                [-1, -1, -1, -1, 8, -1, -1, -1, -1], scale=1))
            sharpness = np.array(laplacian).std()
            
            info.append(f"\n🎯 Nitidez: {sharpness:.1f}")
            if sharpness > 20:
                info.append("   Classificação: Imagem nítida")
            elif sharpness > 10:
                info.append("   Classificação: Nitidez moderada")
            else:
                info.append("   Classificação: Imagem suave/desfocada")
                
        except Exception as e:
            info.append(f"   (Análise de padrões limitada: {e})")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _analisar_regioes_interesse(self, img: Any):
        """Analisa diferentes regiões da imagem"""
        info = ["═══ ANÁLISE POR REGIÕES ═══"]
        
        img_rgb = img.convert('RGB')
        w, h = img.width, img.height
        
        # Divide em 9 regiões (grid 3x3)
        regioes = {
            'Centro': (w//3, h//3, 2*w//3, 2*h//3),
            'Topo': (w//3, 0, 2*w//3, h//3),
            'Base': (w//3, 2*h//3, 2*w//3, h),
            'Esquerda': (0, h//3, w//3, 2*h//3),
            'Direita': (2*w//3, h//3, w, 2*h//3),
        }
        
        info.append("📍 Características por região:")
        
        for nome, (x1, y1, x2, y2) in regioes.items():
            region = img_rgb.crop((x1, y1, x2, y2))
            region_array = np.array(region)
            
            avg_color = region_array.mean(axis=(0, 1)).astype(int)
            brightness = np.array(region.convert('L')).mean()
            
            color_name = self._nomear_cor(*avg_color)
            bright_desc = "escura" if brightness < 85 else "clara" if brightness > 170 else "média"
            
            info.append(f"  {nome:10s}: {color_name:20s} (brilho {bright_desc})")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _detectar_formas_geometricas(self, img: Any):
        """Tentativa básica de detectar formas"""
        info = ["═══ ANÁLISE DE FORMAS ═══"]
        
        if ImageFilter is None:
            info.append("📐 (Análise geométrica não disponível - Pillow necessário)")
            self.descricao_completa.append('\n'.join(info))
            return
        
        try:
            # Simplifica a imagem
            img_small = img.convert('L').resize((50, 50))
            edges = img_small.filter(ImageFilter.FIND_EDGES)
            edges_array = np.array(edges)
            
            # Análise de concentração
            h_profile = edges_array.mean(axis=1)
            v_profile = edges_array.mean(axis=0)
            
            h_variance = h_profile.std()
            v_variance = v_profile.std()
            
            if h_variance < 5 and v_profile < 5:
                info.append("📐 Composição: Elementos uniformemente distribuídos")
            elif h_variance > v_variance * 1.5:
                info.append("📐 Composição: Elementos concentrados horizontalmente")
            elif v_variance > h_variance * 1.5:
                info.append("📐 Composição: Elementos concentrados verticalmente")
            else:
                info.append("📐 Composição: Distribuição balanceada")
                
        except Exception:
            info.append("📐 (Análise geométrica não disponível)")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _analisar_textura(self, img: Any):
        """Análise de textura da imagem"""
        info = ["═══ TEXTURA ═══"]
        
        try:
            gray = img.convert('L').resize((100, 100))
            array = np.array(gray)
            
            # Variação local
            diff_h = np.diff(array, axis=1)
            diff_v = np.diff(array, axis=0)
            
            texture_h = np.abs(diff_h).mean()
            texture_v = np.abs(diff_v).mean()
            texture_avg = (texture_h + texture_v) / 2
            
            info.append(f"🌾 Rugosidade: {texture_avg:.1f}")
            
            if texture_avg < 5:
                info.append("   Classificação: Superfície muito lisa/gradiente suave")
            elif texture_avg < 15:
                info.append("   Classificação: Textura moderada")
            else:
                info.append("   Classificação: Textura rugosa/granulada")
                
        except Exception:
            info.append("🌾 (Análise de textura não disponível)")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _extrair_texto(self, img: Any):
        """Extração de texto via OCR"""
        info = ["═══ TEXTO NA IMAGEM ═══"]
        
        if pytesseract is None:
            info.append("📝 OCR não disponível")
            info.append("   Instale: pip install pytesseract")
            info.append("   + Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        else:
            try:
                texto = pytesseract.image_to_string(img, lang='por')
                if texto.strip():
                    palavras = len(texto.split())
                    info.append(f"📝 Texto detectado: {palavras} palavras, {len(texto)} caracteres")
                    info.append("\nConteúdo do texto:")
                    info.append(texto[:800])
                    if len(texto) > 800:
                        info.append("... [texto continua]")
                else:
                    info.append("📝 Nenhum texto detectado na imagem")
            except Exception as e:
                info.append(f"📝 Erro no OCR: {str(e)}")
        
        self.descricao_completa.append('\n'.join(info))
    
    def _analisar_simetria(self, img: Any):
        """Analisa simetria horizontal e vertical"""
        info = ["═══ SIMETRIA ═══"]
        
        try:
            img_small = img.convert('L').resize((50, 50))
            array = np.array(img_small)
            
            # Simetria horizontal
            top_half = array[:25, :]
            bottom_half = np.flipud(array[25:, :])
            h_similarity = 100 - (np.abs(top_half - bottom_half).mean() / 2.55)
            
            # Simetria vertical
            left_half = array[:, :25]
            right_half = np.fliplr(array[:, 25:])
            v_similarity = 100 - (np.abs(left_half - right_half).mean() / 2.55)
            
            info.append(f"↔️ Simetria horizontal: {h_similarity:.0f}%")
            info.append(f"↕️ Simetria vertical: {v_similarity:.0f}%")
            
            if max(h_similarity, v_similarity) > 80:
                info.append("   Observação: Imagem altamente simétrica")
            elif max(h_similarity, v_similarity) > 60:
                info.append("   Observação: Alguma simetria presente")
            else:
                info.append("   Observação: Composição assimétrica")
                
        except Exception:
            info.append("(Análise de simetria não disponível)")
        
        self.descricao_completa.append('\n'.join(info))
    
    @staticmethod
    def _nomear_cor(r: int, g: int, b: int) -> str:
        """Retorna nome aproximado da cor RGB"""
        # Define cores básicas
        if r < 50 and g < 50 and b < 50:
            return "Preto"
        if r > 200 and g > 200 and b > 200:
            return "Branco"
        if r > 200 and g < 100 and b < 100:
            return "Vermelho"
        if r < 100 and g > 200 and b < 100:
            return "Verde"
        if r < 100 and g < 100 and b > 200:
            return "Azul"
        if r > 200 and g > 200 and b < 100:
            return "Amarelo"
        if r > 200 and g < 100 and b > 200:
            return "Magenta"
        if r < 100 and g > 200 and b > 200:
            return "Ciano"
        if r > 150 and g > 100 and b < 100:
            return "Laranja"
        if r > 100 and g < 100 and b > 100:
            return "Roxo"
        if r > 150 and g > 100 and b > 100:
            return "Rosa"
        if r > 100 and g > 150 and b < 100:
            return "Verde-Amarelado"
        if 100 < r < 150 and 50 < g < 100 and b < 50:
            return "Marrom"
        if abs(r - g) < 30 and abs(g - b) < 30:
            if r < 100:
                return "Cinza escuro"
            elif r < 180:
                return "Cinza médio"
            else:
                return "Cinza claro"
        
        return f"Tom misto"


# Instância global
analisador = AnalisadorVisual()
