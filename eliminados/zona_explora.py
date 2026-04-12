#!/usr/bin/env python3
"""
Explorador de zonas para VTES
=====================================================

Usa las 3 zonas mínimas para encontrar zonas óptimas automáticamente.

Uso:
  python zona_explora.py --carta carta_vtes/jpg/abaddong7.jpg
  python zona_explora.py --carta carta1.jpg --carta carta2.jpg --salida comparacion.txt

Zonas:
  - Top (0-15%): Título + logo
  - Central (10-65%): Arte (ovalado=cuarto, cuadrado=librería)
  - Lateral (0-25%): Clan, tipo, coste

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse


class ZonaExploradorVTES:
    """Explorador de zonas para VTES."""
    
    def __init__(self):
        # Definir zonas
        self.zonas = {
            'top': (0, 15, 0, 100),
            'central': (10, 65, 10, 90),
            'lateral': (0, 100, 0, 25),
        }
    
    def open_image(self, path):
        """Abrir imagen."""
        try:
            img = Image.open(path)
            if img.mode == 'RGBA':
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                return bg
            elif img.mode in ['LA', 'P']:
                return img.convert('RGB')
            return img
        except Exception as e:
            print(f"  ⚠️ No pudo abrir {path}: {e}")
            return None
    
    def extract_zone_hash(self, arr, y_range, x_range):
        """Extraer hash de zona usando DCT."""
        try:
            h, w = arr.shape
            y_min, y_max, x_min, x_max = y_range
            
            y_min_px = int(h * y_min / 100)
            y_max_px = int(h * y_max / 100)
            x_min_px = int(w * x_min / 100)
            x_max_px = int(w * x_max / 100)
            
            zona = arr[y_min_px:y_max_px, x_min_px:x_max_px]
            
            if zona.size == 0:
                return None
            
            arr_float = zona.astype(np.float32)
            dct = np.fft.fft2(arr_float)
            dct_shift = np.fft.ifftshift(np.abs(dct))
            
            h_z, w_z = dct_shift.shape
            h_low, w_low = h_z // 4, w_z // 4
            
            if h_low > 0 and w_low > 0:
                low_freq = dct_shift[h_low:2*h_low, w_low:2*w_low]
                mean_val = np.mean(np.real(low_freq))
                max_abs = np.max(np.abs(low_freq))
                
                if max_abs > 0:
                    return float(mean_val / max_abs)
            
            return None
            
        except Exception:
            return None
    
    def compute_hashes(self, image):
        """Generar hashes para las 3 zonas."""
        if image.mode != 'L':
            image = image.convert('L')
        
        arr = np.array(image)
        hashes = {}
        
        for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in self.zonas.items():
            hash_val = self.extract_zone_hash(arr, (y_min_pct, y_max_pct), (x_min_pct, x_max_pct))
            if hash_val is not None:
                hashes[zona_name] = hash_val
        
        return hashes
    
    def draw_zones(self, image):
        """Dibujar zonas en imagen."""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        h, w = image.size
        
        colors = {'top': 'red', 'central': 'green', 'lateral': 'blue'}
        
        for i, (zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct)) in enumerate(self.zonas.items()):
            y_min = int(h * y_min_pct / 100)
            y_max = int(h * y_max_pct / 100)
            x_min = int(w * x_min_pct / 100)
            x_max = int(w * x_max_pct / 100)
            
            draw.rectangle(
                [x_min, y_min, x_max, y_max],
                outline=colors[i],
                width=3
            )
            
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                draw.text(
                    (x_min + 5, y_min + 5),
                    f"{zona_name.upper()}",
                    fill=colors[i],
                    font=font
                )
            except:
                pass
        
        return image
    
    def visualize(self, image_path, output_path=None):
        """Visualizar carta con zonas."""
        image = self.open_image(image_path)
        
        if image is None:
            return None
        
        overlay = self.draw_zones(image)
        
        if output_path:
            overlay.save(output_path)
            print(f"💾 Guardado en: {output_path}")
            overlay.show()
        
        return overlay
    
    def compare(self, img1_path, img2_path, output_path=None):
        """Comparar dos cartas."""
        img1 = self.open_image(img1_path)
        img2 = self.open_image(img2_path)
        
        if img1 is None or img2 is None:
            return None
        
        hashes1 = self.compute_hashes(img1)
        hashes2 = self.compute_hashes(img2)
        
        img1.close()
        img2.close()
        
        if not hashes1 or not hashes2:
            return None
        
        print(f"\n✅ Hashes calculados")
        
        print(f"\n  Carta 1:")
        for zona, hash_val in hashes1.items():
            print(f"    {zona}: {hash_val:.6f}")
        
        print(f"  \n  Carta 2:")
        for zona, hash_val in hashes2.items():
            print(f"    {zona}: {hash_val:.6f}")
        
        print(f"\n  Diferencias:")
        diffs = {}
        for zona in hashes1.keys() & hashes2.keys():
            diff = abs(hashes1[zona] - hashes2[zona])
            diffs[zona] = diff
            print(f"    {zona}: {diff:.6f}")
        
        total_diff = sum(diffs.values()) / len(diffs) if diffs else 0
        
        print(f"\n  Distancia total: {total_diff:.6f}")
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(f"Comparación: {img1_path} vs {img2_path}\n")
                f.write(f"Distancia total: {total_diff:.6f}\n\n")
                for zona in hashes1.keys():
                    f.write(f"{zona}: {hashes1.get(zona, 'N/A'):.6f} vs {hashes2.get(zona, 'N/A'):.6f} (diff: {diffs.get(zona, 0):.6f})\n")
            
            print(f"\n  ✅ Resultados guardados en: {output_path}")
        
        return total_diff


def main():
    parser = argparse.ArgumentParser(description='Explorador de zonas para VTES')
    parser.add_argument('--visualizar', '-v', action='store_true', help='Visualizar carta')
    parser.add_argument('--carta', '-i', type=str, help='Carta a visualizar')
    parser.add_argument('--output', '-o', type=str, help='Guardar visualización')
    
    parser.add_argument('--comparar', '-c', action='store_true', help='Comparar cartas')
    parser.add_argument('--carta1', '-1', type=str, help='Primera carta')
    parser.add_argument('--carta2', '-2', type=str, help='Segunda carta')
    parser.add_argument('--salida', '-o2', type=str, help='Salida comparación')
    
    parser.add_argument('--help', '-h', action='store_true', help='Mostrar ayuda')
    
    args = parser.parse_args()
    
    if args.help or not (args.visualizar or args.comparar):
        print("""
Explorador de zonas para VTES 🦞
===

Uso:
  
  # Visualizar carta
  python zona_explora.py --visualizar --carta cartas_vtes/jpg/abaddong7.jpg --output overlay.jpg
  
  # Comparar cartas
  python zona_explora.py --comparar --carta1 cartas_vtes/jpg/carta1.jpg --carta2 cartas_vtes/jpg/carta2.jpg --salida comparacion.txt

Zonas:
  
  - Top (0-15%): Título + logo
  - Central (10-65%): Arte (ovalado=cuarto, cuadrado=librería)
  - Lateral (0-25%): Clan, tipo, coste

Autor: La Garra Cifrada 🦞
        """)
        return
    
    explorador = ZonaExploradorVTES()
    
    if args.visualizar:
        explorador.visualize(args.carta, output_path=args.output)
    
    elif args.comparar:
        explorador.compare(args.carta1, args.carta2, output_path=args.salida)


if __name__ == '__main__':
    main()
