#!/usr/bin/env python3
"""
VTES Zone Explorer - Explorador visual de zonas óptimas
=====================================================
Script para visualizar y encontrar las zonas más discriminantes
para matching de cartas VTES usando Perceptual Hashing.

Funcionalidades:
- Visualizar zonas en imagen con superposición
- Calcular información mutual (discriminación) por zona
- Encontrar zonas óptimas automáticamente
- Comparar efectividad de diferentes configuraciones

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse


class ZoneVisualizer:
    """Visualizador y explorador de zonas para cartas VTES."""
    
    def __init__(self, image_folder=None):
        """
        Inicializar el visualizador.
        
        Args:
            image_folder: Carpeta con cartas para explorar.
        """
        self.image_folder = image_folder
    
    def draw_zones(self, image, zones=None, labels=True, outline_color='red', 
                   outline_width=3):
        """
        Dibujar superposición de zonas en una imagen.
        
        Args:
            image: Imagen PIL.
            zones: Dict de zonas {nombre: (y_min, y_max, x_min, x_max)}.
            labels: Mostrar etiquetas de zonas.
            outline_color: Color de los bordes.
            outline_width: Grosor de los bordes.
            
        Returns:
            Imagen con zonas dibujadas.
        """
        if zones is None:
            zones = {
                'superior': (0, 15, 0, 100),
                'central': (15, 85, 5, 95),
                'inferior': (85, 100, 0, 100),
            }
        
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Dibujar zonas
        draw = ImageDraw.Draw(image)
        
        h, w = image.size
        
        # Dibujar cada zona
        for zona, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zones.items():
            y_min = int(h * y_min_pct / 100)
            y_max = int(h * y_max_pct / 100)
            x_min = int(w * x_min_pct / 100)
            x_max = int(w * x_max_pct / 100)
            
            # Dibujar borde
            draw.rectangle(
                [x_min, y_min, x_max, y_max],
                outline=outline_color,
                width=outline_width
            )
            
            if labels:
                # Texto de etiqueta
                label_text = f"{zona.upper()}"
                draw.text(
                    (x_min + 5, y_min + 5),
                    label_text,
                    fill=outline_color,
                    font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                )
        
        return image
    
    def calculate_zone_information(self, image):
        """
        Calcular métricas de discriminación por zona.
        
        Args:
            image: Imagen PIL en escala de grises.
            
        Returns:
            Dict con métricas por zona.
        """
        arr = np.array(image)
        h, w = arr.shape[:2]
        
        metrics = {}
        
        # Dividir en 5 regiones horizontales
        step = h // 5
        
        for i in range(5):
            y_min = i * step
            y_max = (i + 1) * step
            
            zona = arr[y_min:y_max, :]
            
            if zona.size > 0:
                # Calcular información de la zona
                std_dev = np.std(zona)
                mean_val = np.mean(zona)
                
                # Calcular "complejidad" (rango de valores)
                complexity = np.max(zona) - np.min(zona)
                
                metrics[f'region_{i}'] = {
                    'y_range': (y_min, y_max),
                    'std': std_dev,
                    'mean': mean_val,
                    'complexity': complexity
                }
        
        return metrics
    
    def find_optimal_zones(self, image_folder, n_samples=5):
        """
        Encontrar las zonas óptimas probando múltiples cartas.
        
        Args:
            image_folder: Carpeta de cartas.
            n_samples: Número de cartas a probar.
            
        Returns:
            Dict con zonas óptimas y métricas.
        """
        # Buscar imágenes
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        image_files = []
        
        for ext in extensions:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(ext):
                    image_files.append(os.path.join(image_folder, filename))
        
        print(f"🔍 Encontradas {len(image_files)} imágenes en {image_folder}")
        print(f"📊 Probando {n_samples} cartas para encontrar zonas óptimas...\n")
        
        # Tomar muestra aleatoria
        np.random.seed(42)
        sample_files = np.random.choice(image_files, min(n_samples, len(image_files)), replace=False)
        
        zone_scores = []
        
        for img_path in sample_files:
            try:
                img = Image.open(img_path).convert('L')
                metrics = self.calculate_zone_information(img)
                
                # Analizar métricas
                region_scores = []
                for region, data in metrics.items():
                    # Puntuación: complejidad + variación
                    score = data['complexity'] + data['std']
                    region_scores.append((region, score))
                
                # Ordenar por puntuación
                region_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Top 3 regiones más discriminantes
                top_zones = [
                    f"region_{i}" for i, (name, _) in enumerate(region_scores[:3])
                ]
                
                zone_scores.append({
                    'image': img_path,
                    'top_zones': top_zones,
                    'all_regions': region_scores
                })
                
                print(f"  ✅ {os.path.basename(img_path)}:")
                for rank, (region, _) in enumerate(region_scores[:3], 1):
                    print(f"    {rank}. {region} (score: {region_scores[rank-1][1]:.2f})")
                
            except Exception as e:
                print(f"  ⚠️ Error con {img_path}: {e}")
                continue
        
        # Resumen
        print("\n" + "="*60)
        print("📊 Resumen de zonas óptimas:")
        print("="*60)
        
        # Contar menciones
        zone_counts = {}
        for result in zone_scores:
            for region in result['top_zones']:
                zone_counts[region] = zone_counts.get(region, 0) + 1
        
        # Mostrar top zonas
        sorted_zones = sorted(zone_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("\nTop zonas por frecuencia:")
        for i, (region, count) in enumerate(sorted_zones[:5], 1):
            print(f"  {i}. {region}: {count} menciones")
        
        return zone_scores
    
    def visualize_zones_comparison(self, image, zones_configs, output_path=None):
        """
        Comparar visualmente diferentes configuraciones de zonas.
        
        Args:
            image: Imagen PIL.
            zones_configs: Lista de configuraciones de zonas para comparar.
            output_path: Ruta para guardar la imagen resultante.
            
        Returns:
            Imagen comparativa.
        """
        configs = zones_configs or [
            {
                'name': 'Standard',
                'zones': {
                    'superior': (0, 15, 0, 100),
                    'central': (15, 85, 5, 95),
                    'inferior': (85, 100, 0, 100),
                }
            },
            {
                'name': 'Solo Central',
                'zones': {
                    'center': (20, 80, 10, 90),
                }
            },
            {
                'name': 'Completa',
                'zones': {
                    'superior': (0, 20, 0, 100),
                    'borde_izq': (0, 100, 0, 10),
                    'borde_der': (0, 100, 90, 100),
                    'center': (15, 85, 10, 90),
                    'inferior': (80, 100, 0, 100),
                }
            },
        ]
        
        # Crear imagen de comparación
        comparison = Image.new('RGB', (image.width * len(configs), image.height))
        
        for i, config in enumerate(configs):
            # Dibujar imagen con esta configuración
            zone_img = self.draw_zones(
                image.copy(),
                zones=config['zones'],
                labels=True,
                outline_color=['red', 'green', 'blue'][i]
            )
            
            # Copiar a imagen de comparación
            x_start = i * image.width
            comparison.paste(zone_img, (x_start, 0))
        
        # Agregar leyenda
        legend_text = "Configuraciones: Standard | Solo Central | Completa\n\nZonas superiores (títulos/símbolos)\nZonas laterales (bordes)\nZonas centrales (contenido)\nZonas inferiores (pie de carta)"
        
        # Crear imagen de leyenda
        legend = Image.new('RGB', (500, 100))
        legend_pil = Image.new('RGB', (500, 100))
        draw = ImageDraw.Draw(legend)
        draw.text((10, 10), legend_text, fill='black')
        
        # Superponer en esquina inferior derecha
        comparison.paste(legend, (comparison.width - 520, comparison.height - 120))
        
        if output_path:
            comparison.save(output_path)
            print(f"💾 Imagen guardada en: {output_path}")
        
        return comparison


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='VTES Zone Explorer - Visualizar y encontrar zonas óptimas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  # Explorar zonas en carpetas de cartas
  python vtes_zone_explorer.py --folder cartas_vtes --samples 5
  
  # Visualizar una carta específica con diferentes configuraciones
  python vtes_zone_explorer.py --visualize --image cartas_vtes/una_carta.webp
  
  # Configurar zonas personalizadas
  python vtes_zone_explorer.py --folder cartas_vtes --zones-config '{"name": "MiConfig", "zones": {"superior": (0, 15, 0, 100), "center": (15, 85, 5, 95)}}'
        '''
    )
    
    parser.add_argument('--folder', '-f', type=str,
                       help='Carpeta de cartas para explorar')
    parser.add_argument('--samples', '-s', type=int, default=5,
                       help='Número de muestras para explorar (default: 5)')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Visualizar carta con diferentes configuraciones')
    parser.add_argument('--image', '-i', type=str,
                       help='Imagen específica para visualizar')
    parser.add_argument('--zones-config', '-z', type=str,
                       help='Configuración de zonas personalizada (JSON)')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Archivo de salida para visualización')
    parser.add_argument('--config-name', '-n', type=str, default=None,
                       help='Nombre para la configuración personalizada')
    
    args = parser.parse_args()
    
    if not args.folder and not args.visualize and not args.image:
        parser.print_help()
        return
    
    print("="*70)
    print("🦞 VTES Zone Explorer - Explorador de Zonas")
    print("="*70)
    
    visualizer = ZoneVisualizer()
    
    if args.visualize and args.image:
        # Visualizar carta específica
        print(f"\n📷 Visualizando: {args.image}")
        
        if os.path.exists(args.image):
            img = Image.open(args.image)
            
            # Crear imagen de comparación
            configs = [
                {
                    'name': 'Standard (Superior, Central, Inferior)',
                    'zones': {
                        'superior': (0, 15, 0, 100),
                        'central': (15, 85, 5, 95),
                        'inferior': (85, 100, 0, 100),
                    }
                },
                {
                    'name': 'Solo Central (Contenido principal)',
                    'zones': {
                        'center': (20, 80, 10, 90),
                    }
                },
                {
                    'name': 'Completa (Con bordes)',
                    'zones': {
                        'superior': (0, 20, 0, 100),
                        'borde_izq': (0, 100, 0, 10),
                        'borde_der': (0, 100, 90, 100),
                        'center': (15, 85, 10, 90),
                        'inferior': (80, 100, 0, 100),
                    }
                },
                {
                    'name': 'Bordes + Centro',
                    'zones': {
                        'borde_super': (0, 15, 0, 100),
                        'borde_inf': (85, 100, 0, 100),
                        'borde_izq': (0, 100, 0, 10),
                        'borde_der': (0, 100, 90, 100),
                        'center': (15, 85, 10, 90),
                    }
                },
            ]
            
            # Si hay nombre personalizado, agregarlo
            if args.config_name:
                configs.append({
                    'name': args.config_name,
                    'zones': eval(args.zones_config) if args.zones_config else {}
                })
            
            # Mostrar visualización
            comparison = visualizer.visualize_zones_comparison(
                img,
                configs,
                output_path=args.output
            )
            
            # Mostrar
            comparison.show()
        else:
            print(f"⚠️ Imagen no encontrada: {args.image}")
    
    elif args.folder:
        # Explorar carpetas
        results = visualizer.find_optimal_zones(
            image_folder=args.folder,
            n_samples=args.samples
        )
        
        if args.output:
            # Guardar resumen
            with open(args.output, 'w') as f:
                f.write(f"# VTES Zone Explorer - Resultados\n")
                f.write(f"# Carpeta: {args.folder}\n")
                f.write(f"# Muestras: {args.samples}\n\n")
                
                for result in results:
                    f.write(f"\n[{result['image']}]\n")
                    for rank, (region, _) in enumerate(result['top_zones'], 1):
                        f.write(f"  {rank}. {region}\n")
            
            print(f"\n✅ Resultados guardados en: {args.output}")
    
    print("\n" + "="*70)
    print("✅ Exploración completada!")
    print("="*70)


if __name__ == '__main__':
    main()
