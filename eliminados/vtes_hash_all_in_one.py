#!/usr/bin/env python3
"""
VTES Perceptual Hash ALL-IN-ONE 🦞
=====================================================
Script unificado con TODAS las funcionalidades:
1. Convertir .webp a .jpg
2. Visualizar carta con overlay de las 3 Áreas
3. Generar hashes para carpeta
4. Comparar dos cartas

Comandos:
  # Convertir .webp a .jpg
  python vtes_hash_all_in_one.py convert --folder cartas_vtes

  # Visualizar carta
  python vtes_hash_all_in_one.py visualize --image carta.jpg [--output overlay.jpg]

  # Generar hashes
  python vtes_hash_all_in_one.py hash --folder cartas_vtes/jpg [--output hashes.txt]

  # Comparar cartas
  python vtes_hash_all_in_one.py compare --image1 carta1.jpg --image2 carta2.jpg [--output comparacion.txt]

Las 3 Áreas Estratégicas:
  1. TOP SUPERIOR (0-15%) → Título + Símbolo Edición
  2. IMAGEN CENTRAL (10-65%) → Arte (vampiro vs biblioteca)
  3. BANDA LATERAL (0-25%) → Clan + Tipo + Coste

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse


class VTESHashAllInOne:
    """Clase unificada con todas las funcionalidades."""
    
    def __init__(self, hash_size=8):
        self.hash_size = hash_size
        self.zones = {
            'top_superior': (0, 15, 0, 100),
            'imagen_central': (10, 65, 10, 90),
            'banda_lateral': (0, 100, 0, 25),
        }
    
    def open_image_safely(self, path):
        """Abrir imagen (manejar .webp problemáticos)."""
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
            print(f"  ⚠️ No pudo abrir {os.path.basename(path)}: {type(e).__name__}")
            return None
    
    def extract_zone_hash(self, arr, y_range, x_range):
        """Extraer hash de una zona usando DCT."""
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
    
    def compute_zone_hashes(self, image, zones=None):
        """Generar hashes para las 3 áreas."""
        if zones is None:
            zones = self.zones
        
        if image.mode != 'L':
            image = image.convert('L')
        
        arr = np.array(image)
        hashes = {}
        
        for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zones.items():
            hash_val = self.extract_zone_hash(arr, (y_min_pct, y_max_pct), (x_min_pct, x_max_pct))
            if hash_val is not None:
                hashes[zona_name] = hash_val
        
        return hashes
    
    def draw_zones_overlay(self, image, zones=None, labels=True, 
                          colors=['red', 'green', 'blue'],
                          outline_width=3):
        """Dibujar superposición de las 3 áreas."""
        if zones is None:
            zones = self.zones
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        h, w = image.size
        
        for i, (zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct)) in enumerate(zones.items()):
            y_min = int(h * y_min_pct / 100)
            y_max = int(h * y_max_pct / 100)
            x_min = int(w * x_min_pct / 100)
            x_max = int(w * x_max_pct / 100)
            
            draw.rectangle(
                [x_min, y_min, x_max, y_max],
                outline=colors[i % len(colors)],
                width=outline_width
            )
            
            if labels:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                    draw.text(
                        (x_min + 5, y_min + 5),
                        f"{zona_name.upper()}",
                        fill=colors[i % len(colors)],
                        font=font
                    )
                except:
                    pass
        
        return image
    
    def convert_webp_to_jpg(self, webp_path, jpg_path):
        """Convertir .webp a .jpg."""
        try:
            img = Image.open(webp_path)
            
            if img.mode == 'RGBA':
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            elif img.mode in ['LA', 'P']:
                img = img.convert('RGB')
            elif img.mode in ['RGB', 'L']:
                pass
            
            img.save(jpg_path, 'JPEG', quality=95)
            img.close()
            
            return True
            
        except Exception as e:
            print(f"  ⚠️ Fallo en {os.path.basename(webp_path)}: {type(e).__name__}")
            return False
    
    def convert_all_webp_to_jpg(self, source_folder, dest_folder=None):
        """Convertir todos los .webp a .jpg."""
        if dest_folder is None:
            dest_folder = os.path.join(source_folder, 'jpg')
        
        os.makedirs(dest_folder, exist_ok=True)
        
        webp_files = []
        for filename in os.listdir(source_folder):
            if filename.lower().endswith('.webp'):
                webp_files.append(os.path.join(source_folder, filename))
        
        print(f"\n📂 Carpeta origen: {source_folder}")
        print(f"💾 Carpeta destino: {dest_folder}")
        print(f"🔍 Encontradas {len(webp_files)} imágenes .webp")
        
        converted = 0
        failed = 0
        
        for webp_path in webp_files:
            base_name = os.path.splitext(os.path.basename(webp_path))[0]
            jpg_path = os.path.join(dest_folder, base_name + '.jpg')
            
            if os.path.exists(jpg_path):
                continue
            
            success = self.convert_webp_to_jpg(webp_path, jpg_path)
            
            if success:
                converted += 1
                print(f"  ✅ {os.path.basename(webp_path)}")
            else:
                failed += 1
        
        print(f"\n  📊 Estadísticas:")
        print(f"     Total .webp: {len(webp_files)}")
        print(f"     Convertidos: {converted}")
        print(f"     Fallidos: {failed}")
        
        return {
            'total': len(webp_files),
            'converted': converted,
            'failed': failed,
        }
    
    def visualize_image(self, image_path, zones=None, output_path=None):
        """Visualizar una carta con overlay."""
        print(f"📷 Visualizando: {image_path}")
        
        image = self.open_image_safely(image_path)
        
        if image is None:
            return None
        
        overlay = self.draw_zones_overlay(image, zones)
        
        if output_path:
            overlay.save(output_path)
            print(f"💾 Guardado en: {output_path}")
        
        return overlay
    
    def compute_batch_hashes(self, image_folder, output_file=None):
        """Generar hashes para todas las imágenes en carpeta."""
        print(f"\n📂 Carpeta: {image_folder}")
        
        # Buscar SOLO archivos .jpg
        extensions = ['.jpg', '.jpeg']
        image_files = []
        
        for ext in extensions:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(ext):
                    image_files.append(os.path.join(image_folder, filename))
        
        print(f"  🔍 Encontradas {len(image_files)} imágenes .jpg")
        
        results = {}
        
        for img_path in image_files:
            try:
                image = self.open_image_safely(img_path)
                
                if image is None:
                    continue
                
                hashes = self.compute_zone_hashes(image)
                image.close()
                
                if hashes:
                    results[os.path.basename(img_path)] = hashes
                    
                    # Progress bar
                    sys.stdout.write(f"\rProcesando: {len(results)}/{len(image_files)}")
                    sys.stdout.flush()
                else:
                    print(f"  ⚠️ No se pudo generar hash para {os.path.basename(img_path)}")
                    
            except Exception as e:
                print(f"  ⚠️ Error con {img_path}: {e}")
                continue
        
        # Guardar resultados
        if output_file and results:
            with open(output_file, 'w') as f:
                f.write(f"# VTES Perceptual Hashes - 3 Áreas\n")
                f.write(f"# Total: {len(image_files)} imágenes\n")
                f.write(f"# Procesadas: {len(results)}\n\n")
                
                for img_name, hashes in sorted(results.items()):
                    f.write(f"\n[{img_name}]\n")
                    for zona, hash_val in hashes.items():
                        f.write(f"  {zona}: {hash_val:.6f}\n")
            
            print(f"\n  ✅ Hashes guardados en: {output_file}")
        
        return results
    
    def compare_images(self, image1_path, image2_path, output_file=None):
        """Comparar dos cartas."""
        print(f"\n🔍 Comparando: {image1_path} vs {image2_path}")
        
        image1 = self.open_image_safely(image1_path)
        image2 = self.open_image_safely(image2_path)
        
        if image1 is None or image2 is None:
            print("  ⚠️ Una de las imágenes no pudo cargarse")
            return None
        
        hashes1 = self.compute_zone_hashes(image1)
        hashes2 = self.compute_zone_hashes(image2)
        
        image1.close()
        image2.close()
        
        if not hashes1 or not hashes2:
            print("  ⚠️ Una de las imágenes no pudo procesarse")
            return None
        
        print(f"  ✅ Hashes calculados")
        print(f"  \n  Carta 1:")
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
        
        print(f"\n  Distancia total (promedio): {total_diff:.6f}")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"# Comparación de imágenes\n")
                f.write(f"Imagen 1: {image1_path}\n")
                f.write(f"Imagen 2: {image2_path}\n")
                f.write(f"Distancia total: {total_diff:.6f}\n\n")
                
                f.write(f"Imagen 1 hashes:\n")
                for zona, hash_val in hashes1.items():
                    f.write(f"  {zona}: {hash_val:.6f}\n")
                
                f.write(f"\nImagen 2 hashes:\n")
                for zona, hash_val in hashes2.items():
                    f.write(f"  {zona}: {hash_val:.6f}\n")
            
            print(f"\n  ✅ Resultados guardados en: {output_file}")
        
        return {
            'hashes1': hashes1,
            'hashes2': hashes2,
            'diffs': diffs,
            'total_diff': total_diff
        }
    
    def print_help(self):
        """Imprimir ayuda de uso."""
        print("""
VTES Perceptual Hash ALL-IN-ONE 🦞
===

Comandos disponibles:

  1. CONVERTIR .webp a .jpg:
     python vtes_hash_all_in_one.py convert --folder cartas_vtes
  
  2. VISUALIZAR carta:
     python vtes_hash_all_in_one.py visualize --image carta.jpg [--output overlay.jpg]
  
  3. GENERAR HASHES:
     python vtes_hash_all_in_one.py hash --folder cartas_vtes/jpg [--output hashes.txt]
  
  4. COMPARAR cartas:
     python vtes_hash_all_in_one.py compare --image1 carta1.jpg --image2 carta2.jpg [--output comparacion.txt]

Las 3 Áreas Estratégicas:
  
  1. TOP SUPERIOR (0-15%)
     - Título del set + símbolo de edición
     - Identifica el SET directamente
  
  2. IMAGEN CENTRAL (10-65%)
     - Ilustración principal (forma)
     - Ovalada = vampiro, cuadrada = biblioteca
  
  3. BANDA LATERAL (0-25%)
     - Símbolo clan, requisitos, coste
     - Elementos distintivos del SET

Ventajas:
  
  ✅ Todo en un solo script
  ✅ Rápido y eficiente
  ✅ Maneja .webp problemáticos
  ✅ Visualización integrada
  ✅ Matching P2P simple

Ejemplos:
  
  # Convertir .webp a .jpg
  python vtes_hash_all_in_one.py convert --folder cartas_vtes
  
  # Visualizar carta
  python vtes_hash_all_in_one.py visualize --image cartas_vtes/jpg/abaddong7.jpg --output overlay.jpg
  
  # Generar hashes
  python vtes_hash_all_in_one.py hash --folder cartas_vtes/jpg --output hashes.txt
  
  # Comparar cartas
  python vtes_hash_all_in_one.py compare --image1 cartas_vtes/jpg/aabg1.jpg --image2 cartas_vtes/jpg/aabg2.jpg

Autor: La Garra Cifrada 🦞
        """)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='VTES Perceptual Hash ALL-IN-ONE - Convertir, Visualizar, Hashing y Comparar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ver ayuda completa con: python vtes_hash_all_in_one.py
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos')
    
    # Comando convert
    convert_parser = subparsers.add_parser('convert', help='Convertir .webp a .jpg')
    convert_parser.add_argument('--folder', '-f', type=str, required=True, help='Carpeta de origen')
    convert_parser.add_argument('--dest', '-d', type=str, default=None, help='Carpeta destino (si None, subcarpeta jpg)')
    
    # Comando visualize
    visualize_parser = subparsers.add_parser('visualize', help='Visualizar carta con overlay')
    visualize_parser.add_argument('--image', '-i', type=str, required=True, help='Imagen a visualizar')
    visualize_parser.add_argument('--output', '-o', type=str, default=None, help='Guardar imagen')
    
    # Comando hash
    hash_parser = subparsers.add_parser('hash', help='Generar hashes')
    hash_parser.add_argument('--folder', '-f', type=str, required=True, help='Carpeta de imágenes')
    hash_parser.add_argument('--output', '-o', type=str, default=None, help='Archivo de salida')
    
    # Comando compare
    compare_parser = subparsers.add_parser('compare', help='Comparar dos cartas')
    compare_parser.add_argument('--image1', '-1', type=str, required=True, help='Primera carta')
    compare_parser.add_argument('--image2', '-2', type=str, required=True, help='Segunda carta')
    compare_parser.add_argument('--output', '-o', type=str, default=None, help='Archivo de salida')
    
    # Ayuda
    parser.add_argument('--help', '-h', action='store_true', help='Mostrar ayuda')
    
    args = parser.parse_args()
    
    if args.help or not args.command:
        parser.print_help()
        print("\nComandos disponibles: convert, visualize, hash, compare")
        return
    
    hash_engine = VTESHashAllInOne()
    
    if args.command == 'convert':
        # Convertir .webp a .jpg
        stats = hash_engine.convert_all_webp_to_jpg(args.folder, dest_folder=args.dest)
        
    elif args.command == 'visualize':
        # Visualizar carta
        hash_engine.visualize_image(args.image, output_path=args.output)
        
    elif args.command == 'hash':
        # Generar hashes
        hashes = hash_engine.compute_batch_hashes(args.folder, output_file=args.output)
        print(f"\n✅ {len(hashes)} cartas procesadas")
        
    elif args.command == 'compare':
        # Comparar cartas
        hash_engine.compare_images(args.image1, args.image2, output_file=args.output)


if __name__ == '__main__':
    main()
