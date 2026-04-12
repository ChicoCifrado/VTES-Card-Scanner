#!/usr/bin/env python3
"""
VTES Perceptual Hash Matching
-----------------------------
Módulo para matching de cartas VTES usando Perceptual Hashing.
Genera hashes perceptuales y encuentra cartas similares.

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import hashlib
import numpy as np
from PIL import Image
from sklearn.metrics import pairwise_distances
import argparse


class VTESPerceptualHash:
    """Clase para generar y comparar hashes perceptuales de cartas VTES."""
    
    def __init__(self, hash_size=8, dct_size=8):
        """
        Inicializar el matcher de hashes perceptuales.
        
        Args:
            hash_size: Tamaño del hash en bits (4, 6, 8 bits). 
                      8 bits = 256 posibles hashes.
            dct_size: Tamaño de la matriz DCT para extraer el hash.
        """
        self.hash_size = hash_size
        self.dct_size = dct_size
        self.hash_bit = hash_size // 8  # Cuántos bytes por hash
        
    def _dct_hash(self, image_path):
        """
        Generar hash perceptual de una imagen.
        
        Args:
            image_path: Ruta a la imagen.
            
        Returns:
            hash_bytes: Hash de 8 bytes (64 bits).
        """
        try:
            # Cargar imagen y convertir a escala de grises
            img = Image.open(image_path).convert('L')
            img_array = np.array(img)
            
            # Aplicar DCT 2D
            dct = np.fft.fft2(img_array)
            dct_shift = np.fft.ifftshift(dct)
            
            # Extraer coeficientes de baja frecuencia (cuadrante superior izquierdo)
            h, w = dct_shift.shape
            h_low, w_low = h // 2, w // 2
            
            # Tomar el bloque central de baja frecuencia
            low_freq = dct_shift[h_low:2*h_low, w_low:2*w_low]
            
            # Calcular media de los coeficientes reales
            hash_float = np.mean(np.real(low_freq))
            
            # Escalar a rango normalizado y convertir a float32
            hash_bytes = np.float32(hash_float)
            
            return hash_bytes
            
        except Exception as e:
            print(f"  ⚠️ Error procesando {image_path}: {e}")
            return None
    
    def compute_hashes(self, image_folder, output_file='perceptual_hashes.txt'):
        """
        Generar hashes perceptuales para todas las imágenes en una carpeta.
        
        Args:
            image_folder: Ruta a la carpeta de imágenes.
            output_file: Nombre del archivo para guardar los hashes.
            
        Returns:
            Dict: {nombre_archivo: hash_bytes}
        """
        hashes = {}
        
        # Buscar todas las imágenes
        extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        image_files = []
        
        for ext in extensions:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(ext):
                    image_files.append(os.path.join(image_folder, filename))
        
        print(f"🔍 Encontradas {len(image_files)} imágenes en {image_folder}")
        
        # Procesar cada imagen
        for image_path in image_files:
            try:
                hash_value = self._dct_hash(image_path)
                if hash_value is not None:
                    # Crear nombre único basado en el hash
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    hash_key = f"{base_name}:{hash_value:.4f}"
                    
                    hashes[hash_key] = {
                        'path': image_path,
                        'hash': hash_value,
                        'name': base_name
                    }
                    
                    # Progress bar
                    sys.stdout.write(f"\rProcesando: {len(hashes)}/{len(image_files)}")
                    sys.stdout.flush()
                    
            except Exception as e:
                print(f"\n⚠️ Error con {image_path}: {e}")
                continue
        
        # Guardar hashes en archivo
        with open(output_file, 'w') as f:
            f.write("# VTES Perceptual Hashes\n")
            f.write(f"# Generado por vtes_perceptual_hash.py\n")
            f.write(f"# Total: {len(hashes)} cartas\n\n")
            
            for hash_key, data in sorted(hashes.items()):
                f.write(f"{hash_key}|{data['name']}|{data['path']}\n")
        
        print(f"\n✅ Hashes guardados en: {output_file}")
        return hashes
    
    def find_duplicates(self, hashes_file, threshold=0.01, max_results=10):
        """
        Encontrar cartas con hashes similares.
        
        Args:
            hashes_file: Archivo con los hashes generados.
            threshold: Umbral de similitud (menor = más estricto).
            
        Returns:
            Lista de grupos de cartas similares.
        """
        # Leer hashes
        hashes = {}
        with open(hashes_file, 'r') as f:
            for line in f.readlines()[11:]:  # Saltar cabecera
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 3:
                        hash_key, name, path = parts
                        hash_value = float(hash_key.split(':')[1])
                        hashes[name] = {
                            'hash': hash_value,
                            'path': path,
                            'name': name
                        }
        
        print(f"\n🔍 Analizando similitudes de {len(hashes)} hashes...")
        print(f"⚖️ Umbral: {threshold}")
        
        # Agrupar por hash similar
        similar_groups = {}
        
        for i, (name1, data1) in enumerate(hashes.items()):
            for name2, data2 in hashes.items():
                if name1 != name2 and abs(data1['hash'] - data2['hash']) < threshold:
                    group_key = tuple(sorted([name1, name2]))
                    if group_key not in similar_groups:
                        similar_groups[group_key] = [data1, data2]
                    else:
                        similar_groups[group_key].append(data2)
        
        # Mostrar resultados
        if similar_groups:
            print(f"\n🎯 Encontradas {len(similar_groups)} duplicados potenciales:")
            
            for group_key, group in list(similar_groups.items())[:max_results]:
                print(f"\n  📌 Grupo de cartas similares:")
                for card in group:
                    print(f"    - {card['name']}")
        else:
            print("\n✅ No se encontraron duplicados con este umbral.")
        
        return list(similar_groups.values())
    
    def batch_compute(self, image_folder_1, image_folder_2, output_file='all_perceptual_hashes.txt'):
        """
        Generar hashes para múltiples carpetas.
        
        Args:
            image_folder_1: Primera carpeta de cartas.
            image_folder_2: Segunda carpeta de cartas (opcional, para comparar).
            output_file: Archivo de salida.
            
        Returns:
            Dict: Hashes de todas las carpetas.
        """
        all_hashes = {}
        
        for folder in [image_folder_1, image_folder_2]:
            if os.path.exists(folder):
                hashes = self.compute_hashes(folder)
                
                # Unir a dict principal
                for key, value in hashes.items():
                    all_hashes[key] = value
            else:
                print(f"⚠️ Carpeta no encontrada: {folder}")
        
        # Guardar
        with open(output_file, 'w') as f:
            f.write(f"# VTES Perceptual Hashes - Múltiples carpetas\n")
            f.write(f"# Total: {len(all_hashes)} cartas\n\n")
            
            for hash_key, data in sorted(all_hashes.items()):
                f.write(f"{hash_key}|{data['name']}|{data['path']}\n")
        
        print(f"\n✅ Todos los hashes guardados en: {output_file}")
        return all_hashes


def main():
    """Función principal con help de uso."""
    
    parser = argparse.ArgumentParser(
        description='VTES Perceptual Hash Matching - Matching de cartas usando hashes perceptuales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  # Generar hashes para cartas_vtes
  python vtes_perceptual_hash.py --folder cartas_vtes
  
  # Generar y comparar dos carpetas
  python vtes_perceptual_hash.py --folder cartas_vtes --compare fondos_vtes
  
  # Encontrar duplicados
  python vtes_perceptual_hash.py --folder cartas_vtes --find-duplicates
  
  # Personalizar
  python vtes_perceptual_hash.py --folder cartas_vtes --hash-size 8 --threshold 0.01
        '''
    )
    
    parser.add_argument('--folder', '-f', type=str, 
                       required=True,
                       help='Carpetas con cartas (separadas por coma)')
    parser.add_argument('--hash-size', '-h', type=int, default=8,
                       choices=[4, 6, 8],
                       help='Tamaño del hash en bits (4=16 combos, 6=64 combos, 8=256 combos). Default: 8')
    parser.add_argument('--find-duplicates', '-d', action='store_true',
                       help='Encontrar cartas con hashes similares después de generar')
    parser.add_argument('--threshold', '-t', type=float, default=0.01,
                       help='Umbral de similitud para encontrar duplicados (default: 0.01)')
    parser.add_argument('--compare', '-c', type=str,
                       help='Carpetas adicionales a comparar (separadas por coma)')
    parser.add_argument('--output', '-o', type=str, default='perceptual_hashes.txt',
                       help='Archivo de salida para hashes (default: perceptual_hashes.txt)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar detalles de procesamiento')
    
    args = parser.parse_args()
    
    # Crear matcher
    matcher = VTESPerceptualHash(
        hash_size=args.hash_size,
        dct_size=8
    )
    
    print("=" * 60)
    print("🦞 VTES Perceptual Hash Matching")
    print("=" * 60)
    
    # Parsear carpetas
    folders = [f.strip() for f in args.folder.split(',')]
    
    if args.compare:
        folders.extend([f.strip() for f in args.compare.split(',')])
    
    print(f"\n📂 Carpetas a procesar:")
    for folder in folders:
        print(f"  - {folder}")
    
    # Generar hashes
    all_hashes = {}
    for folder in folders:
        if not os.path.exists(folder):
            print(f"\n⚠️ Carpeta no encontrada: {folder}")
            continue
            
        print(f"\n{'='*60}")
        print(f"📂 Procesando: {folder}")
        print(f"{'='*60}")
        
        hashes = matcher.compute_hashes(
            folder=folder,
            output_file=args.output
        )
        all_hashes.update(hashes)
    
    # Encontrar duplicados si se pidió
    if args.find_duplicates:
        print(f"\n{'='*60}")
        print(f"🔍 Buscando duplicados...")
        print(f"{'='*60}")
        
        # Crear archivo temporal
        temp_file = args.output.replace('.txt', '_temp.txt')
        matcher.compute_hashes(
            folder=folders[0],
            output_file=temp_file
        )
        
        matcher.find_duplicates(
            temp_file,
            threshold=args.threshold,
            max_results=20
        )
    
    print(f"\n{'='*60}")
    print(f"✅ Procesamiento completado!")
    print(f"   Total de cartas procesadas: {len(all_hashes)}")
    print(f"   Archivo de hashes: {args.output}")
    print(f"{'='*60}")
    
    return all_hashes


if __name__ == '__main__':
    main()
