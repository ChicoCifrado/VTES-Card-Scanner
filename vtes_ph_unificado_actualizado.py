#!/usr/bin/env python3
"""
VTES Perceptual Hash Unificado - Multi-Zona 3 Áreas + Visualización
=====================================================
Script todo-en-uno para:
- Visualizar zonas en cartas (las 3 áreas estratégicas)
- Generar hashes perceptuales por zona (top, central, lateral)
- Encontrar duplicados
- Comparar cartas

3 Áreas Estratégicas:
1. TOP SUPERIOR (0-15%) → Título + Símbolo Edición → Identifica SET
2. IMAGEN CENTRAL (10-65%) → Forma del arte → Vampiro vs Biblioteca  
3. BANDA LATERAL (0-25%) → Clan + Tipo + Coste → Distintivo

Ventajas:
- MENOS ZONAS = más rápido
- MENOR RUIDO = mayor precisión
- VISUALIZACIÓN integrada

Uso básico:
1. Visualizar carta: python vtes_ph_unificado_actualizado.py --visualize --image carta.jpg
2. Generar hashes: python vtes_ph_unificado_actualizado.py --folder cartas_vtes
3. Comparar cartas: python vtes_ph_unificado_actualizado.py --compare carta1.jpg carta2.jpg
4. Explorar zonas: python vtes_ph_unificado_actualizado.py --folder cartas_vtes --find-optimal

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse


class VTESPerceptualHash3Areas:
    """
    Clases para hashing y visualización con las 3 Áreas Estratégicas.
    
    Uso básico:
    1. Visualizar carta: python vtes_ph_unificado_actualizado.py --visualize --image carta.jpg
    2. Generar hashes: python vtes_ph_unificado_actualizado.py --folder cartas_vtes
    3. Comparar cartas: python vtes_ph_unificado_actualizado.py --compare carta1.jpg carta2.jpg
    """
    
    def __init__(self, hash_size=8):
        self.hash_size = hash_size
    
    def get_default_zones_3_areas(self):
        """
        Las 3 Áreas Estratégicas para clasificación.
        
        Returns:
            Dict de las 3 áreas con rangos en porcentaje.
        """
        return {
            'top_superior': (0, 15, 0, 100),      # Título + Símbolo Edición → Identifica SET
            'imagen_central': (10, 65, 10, 90),   # Arte (forma) → Vampiro vs Biblioteca
            'banda_lateral': (0, 100, 0, 25),     # Clan + Tipo + Coste → Elementos distintivos
        }
    
    def extract_zone_hash(self, arr, y_range, x_range):
        """
        Extraer hash de una zona usando DCT.
        
        Args:
            arr: Array de imagen (grayscale).
            y_range: (y_min, y_max) en porcentaje.
            x_range: (x_min, x_max) en porcentaje.
            
        Returns:
            Hash (0-1) o None si falla.
        """
        try:
            h, w = arr.shape
            y_min, y_max, x_min, x_max = y_range
            
            # Convertir rangos a píxeles
            y_min_px = int(h * y_min / 100)
            y_max_px = int(h * y_max / 100)
            x_min_px = int(w * x_min / 100)
            x_max_px = int(w * x_max / 100)
            
            # Extraer zona
            zona = arr[y_min_px:y_max_px, x_min_px:x_max_px]
            
            if zona.size == 0:
                return None
            
            # Normalizar
            arr_float = zona.astype(np.float32)
            
            # Aplicar DCT y extraer hash
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
        """
        Generar hashes para las 3 áreas.
        
        Args:
            image: Imagen PIL.
            zones: Config de zonas (opcional, usa default si None).
            
        Returns:
            Dict con hashes por área.
        """
        if zones is None:
            zones = self.get_default_zones_3_areas()
        
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
        """
        Dibujar superposición de las 3 áreas en imagen.
        
        Args:
            image: Imagen PIL.
            zones: Dict de zonas o None para usar predeterminado.
            labels: Mostrar etiquetas.
            colors: Colores para cada zona.
            outline_width: Grosor de bordes.
            
        Returns:
            Imagen con overlay.
        """
        if zones is None:
            zones = self.get_default_zones_3_areas()
        
        # Convertir a RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        h, w = image.size
        
        # Dibujar cada zona
        for i, (zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct)) in enumerate(zones.items()):
            y_min = int(h * y_min_pct / 100)
            y_max = int(h * y_max_pct / 100)
            x_min = int(w * x_min_pct / 100)
            x_max = int(w * x_max_pct / 100)
            
            # Dibujar borde
            draw.rectangle(
                [x_min, y_min, x_max, y_max],
                outline=colors[i % len(colors)],
                width=outline_width
            )
            
            if labels:
                # Texto de etiqueta
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
    
    def visualize_image(self, image_path, zones=None, output_path=None):
        """
        Visualizar una carta con overlay de las 3 áreas.
        
        Args:
            image_path: Ruta a la carta.
            zones: Config de zonas (opcional).
            output_path: Ruta para guardar imagen (opcional).
            
        Returns:
            Imagen visualizada.
        """
        print(f"📷 Visualizando: {image_path}")
        
        image = Image.open(image_path)
        
        # Dibujar zonas
        overlay = self.draw_zones_overlay(image, zones)
        
        if output_path:
            overlay.save(output_path)
            print(f"💾 Guardado en: {output_path}")
        
        return overlay
    
    def compute_batch_hashes(self, image_folder, zones=None, output_file=None):
        """
        Generar hashes para todas las imágenes en carpeta.
        
        Args:
            image_folder: Carpeta de imágenes.
            zones: Config de zonas (opcional).
            output_file: Archivo de salida (opcional).
            
        Returns:
            Dict con hashes.
        """
        if zones is None:
            zones = self.get_default_zones_3_areas()
        
        print(f"\n📂 Carpeta: {image_folder}")
        
        # Buscar imágenes
        extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        image_files = []
        
        for ext in extensions:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(ext):
                    image_files.append(os.path.join(image_folder, filename))
        
        print(f"  🔍 Encontradas {len(image_files)} imágenes")
        
        results = {}
        
        for img_path in image_files:
            try:
                image = Image.open(img_path)
                hashes = self.compute_zone_hashes(image, zones)
                
                if hashes:
                    results[os.path.basename(img_path)] = hashes
                    
                    # Progress bar
                    sys.stdout.write(f"\rProcesando: {len(results)}/{len(image_files)}")
                    sys.stdout.flush()
                else:
                    print(f"  ⚠️ No se pudo procesar {img_path}")
                    
            except Exception as e:
                print(f"  ⚠️ Error con {img_path}: {e}")
                continue
        
        # Guardar resultados
        if output_file and results:
            with open(output_file, 'w') as f:
                f.write(f"# VTES Perceptual Hashes - 3 Áreas Estratégicas\n")
                f.write(f"# Total: {len(results)} cartas\n\n")
                
                for img_name, hashes in sorted(results.items()):
                    f.write(f"\n[{img_name}]\n")
                    for zona, hash_val in hashes.items():
                        f.write(f"  {zona}: {hash_val:.6f}\n")
            
            print(f"\n  ✅ Hashes guardados en: {output_file}")
        
        return results
    
    def compare_images(self, image1_path, image2_path, output_file=None):
        """
        Comparar dos cartas usando hashing por zonas.
        
        Args:
            image1_path: Primera imagen.
            image2_path: Segunda imagen.
            output_file: Archivo de salida con resultados.
            
        Returns:
            Diccionario con distancias Hamming y hashes.
        """
        print(f"\n🔍 Comparando: {image1_path} vs {image2_path}")
        
        # Cargar imágenes
        image1 = Image.open(image1_path).convert('L')
        image2 = Image.open(image2_path).convert('L')
        
        # Calcular hashes
        hashes1 = self.compute_zone_hashes(image1)
        hashes2 = self.compute_zone_hashes(image2)
        
        if not hashes1 or not hashes2:
            print("  ⚠️ Una de las imágenes no pudo procesarse")
            return None
        
        # Calcular distancia Hamming para cada zona
        print(f"  ✅ Hashes calculados")
        print(f"  \n  Carta 1:")
        for zona, hash_val in hashes1.items():
            print(f"    {zona}: {hash_val:.6f}")
        
        print(f"  \n  Carta 2:")
        for zona, hash_val in hashes2.items():
            print(f"    {zona}: {hash_val:.6f}")
        
        # Calcular diferencias
        print(f"\n  Diferencias:")
        diffs = {}
        for zona in hashes1.keys() & hashes2.keys():
            diff = abs(hashes1[zona] - hashes2[zona])
            diffs[zona] = diff
            print(f"    {zona}: {diff:.6f}")
        
        # Calcular distancia total (media de diferencias)
        total_diff = sum(diffs.values()) / len(diffs) if diffs else 0
        
        print(f"\n  Distancia total (promedio): {total_diff:.6f}")
        
        # Guardar resultados
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
    
    def print_usage(self):
        """Imprimir ayuda de uso."""
        print("""
VTES Perceptual Hash - 3 Áreas Estratégicas 🦞
===

Uso básico:
  
  # Ver resumen de las 3 áreas
  python vtes_ph_unificado_actualizado.py --help
  
  # Visualizar carta con las 3 áreas
  python vtes_ph_unificado_actualizado.py --visualize --image carta.jpg
  
  # Guardar visualización
  python vtes_ph_unificado_actualizado.py --visualize --image carta.jpg --output overlay.jpg
  
  # Generar hashes para carpeta
  python vtes_ph_unificado_actualizado.py --folder cartas_vtes
  
  # Guardar hashes en archivo
  python vtes_ph_unificado_actualizado.py --folder cartas_vtes --output hashes.txt
  
  # Comparar dos cartas
  python vtes_ph_unificado_actualizado.py --compare carta1.jpg carta2.jpg
  
  # Comparar con salida
  python vtes_ph_unificado_actualizado.py --compare carta1.jpg carta2.jpg --output comparacion.txt

Las 3 Áreas Estratégicas:
  
  1. TOP SUPERIOR (0-15%)
     - Título del set + símbolo de edición
     - Identifica el SET directamente
  
  2. IMAGEN CENTRAL (10-65%)
     - Ilustración principal (forma ovalada=vampiro, cuadrada=biblioteca)
     - Forma del arte diferencia vampiros vs biblioteca
  
  3. BANDA LATERAL (0-25%)
     - Símbolo clan, requisitos, coste, tipo de carta
     - Captura elementos distintivos del SET

Ventajas de las 3 áreas:
  
  ✅ Más rápido (menor procesamiento)
  ✅ Menor ruido visual (mayor precisión)
  ✅ Más robusto a variaciones de iluminación
  ✅ Ideal para matching masivo

Autor: La Garra Cifrada 🦞
        """)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='VTES Perceptual Hash - 3 Áreas Estratégicas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ver resumen de uso con: python vtes_ph_unificado_actualizado.py --help
        """,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos')
    
    # Subcomando visualize
    visualize_parser = subparsers.add_parser('visualize', help='Visualizar carta con overlay')
    visualize_parser.add_argument('--image', '-i', type=str, required=True, help='Carta a visualizar')
    visualize_parser.add_argument('--output', '-o', type=str, default=None, help='Guardar imagen visualizada')
    
    # Subcomando hash
    hash_parser = subparsers.add_parser('hash', help='Generar hashes para carpeta')
    hash_parser.add_argument('--folder', '-f', type=str, required=True, help='Carpeta de imágenes')
    hash_parser.add_argument('--output', type=str, default=None, help='Archivo de salida')
    
    # Subcomando compare
    compare_parser = subparsers.add_parser('compare', help='Comparar dos cartas')
    compare_parser.add_argument('--image1', '-1', type=str, required=True, help='Primera carta')
    compare_parser.add_argument('--image2', '-2', type=str, required=True, help='Segunda carta')
    compare_parser.add_argument('--output', type=str, default=None, help='Archivo de salida')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    hash_engine = VTESPerceptualHash3Areas()
    
    if args.command == 'visualize':
        # Visualizar carta
        hash_engine.visualize_image(args.image, output_path=args.output)
        
    elif args.command == 'hash':
        # Generar hashes
        hashes = hash_engine.compute_batch_hashes(args.folder, output_file=args.output)
        print(f"\n✅ {len(hashes)} cartas procesadas")
        
    elif args.command == 'compare':
        # Comparar imágenes
        hash_engine.compare_images(args.image1, args.image2, output_file=args.output)


if __name__ == '__main__':
    main()
