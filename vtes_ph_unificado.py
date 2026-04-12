#!/usr/bin/env python3
"""
VTES Perceptual Hash Unificado - Multi-Zone + Visualización
=====================================================
Script todo-en-uno para:
- Visualizar zonas en cartas
- Generar hashes perceptuales por zona
- Encontrar duplicados
- Explorar y optimizar zonas automáticamente

Ventajas:
- TODO en un solo script
- No requiere exploración por separado
- Visualización integrada
- Configuración simple

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse


class VTESPerceptualHashZone:
    """
    Clases para hashing y visualización por zonas.
    
    Uso básico:
    1. Visualizar carta: python vtes_ph_unificado.py --visualize --image carta.jpg
    2. Generar hashes: python vtes_ph_unificado.py --folder cartas_vtes
    3. Comparar cartas: python vtes_ph_unificado.py --compare carta1.jpg carta2.jpg
    4. Explorar zonas: python vtes_ph_unificado.py --folder cartas_vtes --find-optimal
    """
    
    def __init__(self, hash_size=8):
        self.hash_size = hash_size
        self.zones_config = None
    
    def get_default_zones(self):
        """Configuración de zonas predeterminada."""
        return {
            'borde_superior': (0, 15, 0, 100),
            'borde_inferior': (85, 100, 0, 100),
            'borde_izq': (0, 100, 0, 10),
            'borde_der': (0, 100, 90, 100),
            'centro': (15, 85, 10, 90),
        }
    
    def get_zone_config(self, config_name='standard'):
        """
        Obtener configuración de zonas por nombre.
        
        Args:
            config_name: Nombre de configuración ('standard', 'bordes', 'centro', etc.)
            
        Returns:
            Dict de zonas.
        """
        configs = {
            'standard': self.get_default_zones(),
            'bordes': {
                'borde_superior': (0, 15, 0, 100),
                'borde_inferior': (85, 100, 0, 100),
                'borde_izq': (0, 100, 0, 10),
                'borde_der': (0, 100, 90, 100),
            },
            'centro': {
                'centro': (20, 80, 10, 90),
            },
            'superior_inferior': {
                'superior': (0, 15, 0, 100),
                'inferior': (85, 100, 0, 100),
            },
            'bordes_y_centro': {
                'borde_superior': (0, 15, 0, 100),
                'borde_inferior': (85, 100, 0, 100),
                'centro': (15, 85, 10, 90),
            },
        }
        
        return configs.get(config_name, configs['standard'])
    
    def extract_zone_hash(self, arr, y_range, h_range):
        """
        Extraer hash de una zona.
        
        Args:
            arr: Array de imagen.
            y_range: (y_min, y_max) en porcentaje.
            h_range: (x_min, x_max) en porcentaje o None para todo ancho.
            
        Returns:
            Hash o None.
        """
        h, w = arr.shape[:2]
        
        y_min = int(h * y_range[0] / 100)
        y_max = int(h * y_range[1] / 100)
        
        if h_range:
            x_min = int(w * h_range[0] / 100)
            x_max = int(w * h_range[1] / 100)
            zona = arr[y_min:y_max, x_min:x_max]
        else:
            zona = arr[y_min:y_max, :]
        
        if zona.size == 0:
            return None
        
        try:
            arr_float = zona.astype(np.float32)
            dct = np.fft.fft2(arr_float)
            dct_shift = np.fft.ifftshift(np.abs(dct))
            
            h_z, w_z = dct_shift.shape
            h_low, w_low = h_z // 4, w_z // 4
            low_freq = dct_shift[h_low:2*h_low, w_low:2*w_low]
            
            if low_freq.size > 0:
                mean_val = np.mean(np.real(low_freq))
                max_abs = np.max(np.abs(low_freq))
                if max_abs > 0:
                    return float(mean_val / max_abs)
            
            return None
            
        except Exception:
            return None
    
    def compute_zone_hashes(self, image):
        """
        Generar hashes para todas las zonas.
        
        Args:
            image: Imagen PIL.
            
        Returns:
            Dict con hashes por zona.
        """
        if image.mode != 'L':
            image = image.convert('L')
        
        arr = np.array(image)
        hashes = {}
        zones = self.get_zone_config()
        
        for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zones.items():
            hash_val = self.extract_zone_hash(arr, (y_min_pct, y_max_pct), (x_min_pct, x_max_pct))
            if hash_val is not None:
                hashes[zona_name] = hash_val
        
        return hashes
    
    def draw_zones_overlay(self, image, zones=None, labels=True, 
                          colors=['red', 'green', 'blue', 'yellow', 'magenta'],
                          outline_width=3):
        """
        Dibujar superposición de zonas en imagen.
        
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
            zones = self.get_zone_config()
        
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
                text = f"{zona_name.upper()}"
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                try:
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_w = text_bbox[2] - text_bbox[0]
                    text_h = text_bbox[3] - text_bbox[1]
                    text_anchor_x = x_min + (x_max - x_min) / 2 - text_w / 2
                    text_anchor_y = y_min + (y_max - y_min) / 2 - text_h / 2
                    draw.text((text_anchor_x, text_anchor_y), text, fill=colors[i % len(colors)], font=font)
                except:
                    pass
        
        return image
    
    def visualize_image(self, image_path, zones=None, output_path=None):
        """
        Visualizar una carta con overlay de zonas.
        
        Args:
            image_path: Ruta a la carta.
            zones: Config de zonas (opcional).
            output_path: Ruta para guardar imagen (opcional).
            
        Returns:
            Imagen visualizada.
        """
        print(f"📷 Visualizando: {image_path}")
        
        image = Image.open(image_path)
        
        # Mostrar imagen original
        image.show()
        
        # Dibujar zonas
        overlay = self.draw_zones_overlay(image, zones)
        
        if output_path:
            overlay.save(output_path)
            print(f"💾 Guardado en: {output_path}")
            overlay.show()
        
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
            zones = self.get_zone_config()
        
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
                hashes = self.compute_zone_hashes(image)
                
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
                f.write(f"# VTES Perceptual Hashes por Zona\n")
                f.write(f"# Total: {len(results)} cartas\n\n")
                
                for img_name, hashes in sorted(results.items()):
                    f.write(f"\n[{img_name}]\n")
                    for zona, hash_val in hashes.items():
                        f.write(f"  {zona}: {hash_val:.6f}\n")
            
            print(f"\n  ✅ Hashes guardados en: {output_file}")
        
        return results
    
    def find_optimal_zones(self, image_folder, n_samples=5):
        """
        Encontrar las zonas óptimas por discriminación.
        
        Args:
            image_folder: Carpeta de imágenes.
            n_samples: Número de muestras.
            
        Returns:
            Dict con zonas recomendadas.
        """
        print(f"\n🔍 Buscando zonas óptimas en {image_folder}")
        
        # Buscar imágenes
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        image_files = []
        
        for ext in extensions:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(ext):
                    image_files.append(os.path.join(image_folder, filename))
        
        print(f"  🔍 Encontradas {len(image_files)} imágenes")
        
        # Muestra aleatoria
        import random
        random.seed(42)
        sample_files = random.sample(image_files, min(n_samples, len(image_files)))
        
        zone_scores = {}
        
        for img_path in sample_files:
            try:
                image = Image.open(img_path).convert('L')
                arr = np.array(image)
                
                # Calcular puntuación de cada zona
                zone_scores = {}
                zones = self.get_zone_config()
                
                for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zones.items():
                    y_min = int(arr.shape[0] * y_min_pct / 100)
                    y_max = int(arr.shape[0] * y_max_pct / 100)
                    
                    x_min = int(arr.shape[1] * x_min_pct / 100) if x_min_pct else 0
                    x_max = int(arr.shape[1] * x_max_pct / 100) if x_max_pct else arr.shape[1]
                    
                    # Extraer zona
                    if x_min_pct and x_max_pct:
                        zona = arr[y_min:y_max, x_min:x_max]
                    else:
                        zona = arr[y_min:y_max, :]
                    
                    if zona.size > 0:
                        # Calcular complejidad
                        complexity = np.max(zona) - np.min(zona)
                        std_dev = np.std(zona)
                        
                        # Puntuación: combinado de complejidad y variación
                        score = complexity + std_dev
                        
                        if zona_name not in zone_scores:
                            zone_scores[zona_name] = score
                        
                # Ordenar zonas por puntuación
                sorted_zones = sorted(zone_scores.items(), key=lambda x: x[1], reverse=True)
                
                print(f"\n  ✅ {os.path.basename(img_path)}:")
                for i, (zona_name, score) in enumerate(sorted_zones[:3], 1):
                    print(f"    {i}. {zona_name}: score={score:.2f}")
                    
            except Exception as e:
                print(f"  ⚠️ Error con {img_path}: {e}")
                continue
        
        # Recomendar zonas
        print("\n" + "="*60)
        print("📊 Zonas recomendadas (basado en las muestras):")
        print("="*60)
        
        for zona_name in sorted(zone_scores.keys(), key=lambda x: zone_scores[x], reverse=True)[:3]:
            print(f"  ✅ {zona_name}")
        
        return zone_scores
    
    def compare_images(self, image_path1, image_path2):
        """
        Comparar dos imágenes por zonas.
        
        Args:
            image_path1: Primera imagen.
            image_path2: Segunda imagen.
            
        Returns:
            Dict con comparaciones.
        """
        image1 = Image.open(image_path1).convert('L')
        image2 = Image.open(image_path2).convert('L')
        
        hashes1 = self.compute_zone_hashes(image1)
        hashes2 = self.compute_zone_hashes(image2)
        
        if not hashes1 or not hashes2:
            return None
        
        comparison = {}
        
        for zona in hashes1.keys():
            val1 = hashes1[zona]
            val2 = hashes2.get(zona)
            
            if val1 is not None and val2 is not None:
                diff = abs(val1 - val2)
                similarity = 1 - diff  # Normalizado
                
                comparison[zona] = {
                    'image1': val1,
                    'image2': val2,
                    'difference': diff,
                    'similarity': similarity
                }
        
        return comparison


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='VTES Perceptual Hash Unificado - Multi-Zone + Visualización',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  
  # Visualizar carta con zonas
  python vtes_ph_unificado.py --visualize --image cartas_vtes/una_carta.webp
  
  # Generar hashes para todas las cartas
  python vtes_ph_unificado.py --folder cartas_vtes --output hashes_zonas.txt
  
  # Comparar dos cartas
  python vtes_ph_unificado.py --compare cartas_vtes/img1.jpg cartas_vtes/img2.jpg
  
  # Explorar zonas óptimas
  python vtes_ph_unificado.py --folder cartas_vtes --find-optimal
  
  # Usar configuración de zonas específica
  python vtes_ph_unificado.py --folder cartas_vtes --config bordes
  
  # Visualizar y guardar overlay
  python vtes_ph_unificado.py --visualize --image carta.webp --output overlay.png
        '''
    )
    
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Visualizar carta con overlay de zonas')
    parser.add_argument('--image', '-i', type=str,
                       help='Carta a visualizar (requerido para --visualize)')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Archivo de salida para visualización')
    parser.add_argument('--folder', '-f', type=str,
                       help='Carpeta de cartas (para generar hashes o explorar)')
    parser.add_argument('--find-optimal', action='store_true',
                       help='Buscar zonas óptimas automáticamente')
    parser.add_argument('--compare', '-c', type=str, nargs='+',
                       help='Comparar estas imágenes (ej: img1.jpg img2.jpg)')
    parser.add_argument('--config', type=str, default='standard',
                       choices=['standard', 'bordes', 'centro', 'superior_inferior', 'bordes_y_centro'],
                       help='Configuración de zonas (default: standard)')
    parser.add_argument('--hash-size', '-h', type=int, default=8,
                       choices=[4, 6, 8],
                       help='Tamaño del hash en bits (default: 8)')
    parser.add_argument('--samples', '-s', type=int, default=5,
                       help='Número de muestras para explorar (default: 5)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🦞 VTES Perceptual Hash Unificado - Multi-Zone")
    print("="*70)
    
    # Crear matcher
    matcher = VTESPerceptualHashZone(hash_size=args.hash_size)
    
    if args.visualize and args.image:
        # Visualizar carta
        print(f"\n📷 Visualizando carta con zonas")
        print(f"   Archivo: {args.image}")
        print(f"   Config: {args.config}")
        
        image = Image.open(args.image)
        
        # Dibujar overlay
        overlay = matcher.draw_zones_overlay(
            image,
            zones=matcher.get_zone_config(args.config),
            colors=['red', 'blue', 'green', 'yellow', 'cyan']
        )
        
        # Mostrar
        overlay.show()
        
        # Guardar si se especificó
        if args.output:
            overlay.save(args.output)
            print(f"\n💾 Guardado en: {args.output}")
            
    elif args.folder and args.find_optimal:
        # Explorar zonas óptimas
        zone_scores = matcher.find_optimal_zones(
            image_folder=args.folder,
            n_samples=args.samples
        )
        
        # Recomendar configuración basada en resultados
        print("\n" + "="*60)
        print("📋 Recomendación:")
        print("="*60)
        print("  Usa el script anterior para ver las zonas.")
        print("  Las zonas recomendadas son las mencionadas más frecuentemente.")
        
    elif args.folder:
        # Generar hashes
        output_file = args.output or f"hashes_{args.config}.txt"
        results = matcher.compute_batch_hashes(
            image_folder=args.folder,
            zones=matcher.get_zone_config(args.config),
            output_file=output_file
        )
        
    elif args.compare:
        # Comparar imágenes
        comparison = matcher.compare_images(args.compare[0], args.compare[1])
        
        if comparison:
            print(f"\n🔬 Comparación: {os.path.basename(args.compare[0])} vs {os.path.basename(args.compare[1])}")
            for zona, data in comparison.items():
                print(f"\n  📍 {zona}:")
                print(f"    Imagen 1: {data['image1']:.4f}")
                print(f"    Imagen 2: {data['image2']:.4f}")
                print(f"    Diff: {data['difference']:.4f}")
                print(f"    Similarity: {(data['similarity']*100):.2f}%")
        else:
            print("⚠️ No se pudo comparar las imágenes")
    else:
        parser.print_help()
    
    print(f"\n{'='*70}")
    print("✅ Terminado!")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
