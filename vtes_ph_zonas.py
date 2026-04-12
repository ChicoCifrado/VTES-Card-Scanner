#!/usr/bin/env python3
"""
VTES Perceptual Hash por Zonas - Multi-Zone Hashing
=====================================================
Módulo avanzado para matching de cartas VTES usando Perceptual Hashing
con división de la carta en zonas clave.

Ventajas:
- Captura bordes distintivos (emotes, símbolos)
- Ignora ruido del fondo
- Mayor precisión en cartas con diseño estructurado
- Detección más confiable de variaciones sutiles

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import numpy as np
from PIL import Image
import argparse
from sklearn.metrics import pairwise_distances


class VTESMultiZoneHash:
    """
    Clases para hashing por zonas de cartas VTES.
    
    Zonas definidas:
    - ZONA_BORDES: 15% superior + inferior (títulos, símbolos)
    - ZONA_CENTER: 50% central (contenido principal)
    - ZONA_BORDES_DER: 10% derecha (elementos laterales)
    """
    
    def __init__(self, hash_size=8, dct_size=8, zones=None):
        """
        Inicializar el matcher multi-zona.
        
        Args:
            hash_size: Tamaño del hash en bits (4, 6, 8).
            dct_size: Tamaño de la matriz DCT.
            zones: Configuración personalizada de zonas.
        """
        self.hash_size = hash_size
        self.dct_size = dct_size
        self.zones = zones or self._get_default_zones()
        
    def _get_default_zones(self):
        """Zonas predeterminadas para cartas VTES."""
        return {
            'bordes': {'y_range': (0, 15), 'h_range': None, 'label': 'Bordes (titulos/simbolos)'},
            'center': {'y_range': (15, 85), 'h_range': (5, 95), 'label': 'Central (contenido principal)'},
            'borde_der': {'y_range': None, 'h_range': (85, 100), 'label': 'Borde derecho (elementos laterales)'},
        }
    
    def extract_zones(self, image):
        """
        Extraer zonas de una imagen y generar hashes para cada zona.
        
        Args:
            image: Imagen PIL convertida a escala de grises.
            
        Returns:
            Dict: {zona_name: hash_value}
        """
        # Convertir a array numpy
        arr = np.array(image)
        h, w = arr.shape[:2]
        
        hashes = {}
        
        # ZONA 1: Bordes superior/inferior (títulos, símbolos clave)
        if self.zones['bordes']['y_range']:
            y_min, y_max = int(h * self.zones['bordes']['y_range'][0] / 100), \
                           int(h * self.zones['bordes']['y_range'][1] / 100)
            zona_bordes = arr[y_min:y_max, :]
            if zona_bordes.size > 0:
                hash_val = self._hash_from_array(zona_bordes)
                hashes['bordes_superior'] = hash_val
                
                # También zona inferior si existe
                if y_max < h:
                    zona_inf = arr[max(0, y_max):min(h, y_max + y_min), :]
                    if zona_inf.size > 0:
                        hash_val_inf = self._hash_from_array(zona_inf)
                        hashes['bordes_inferior'] = hash_val_inf
        
        # ZONA 2: Centro (contenido principal, menos sensible a fondo)
        if self.zones['center']['y_range']:
            y_min, y_max = int(h * self.zones['center']['y_range'][0] / 100), \
                           int(h * self.zones['center']['y_range'][1] / 100)
            if self.zones['center']['h_range']:
                x_min, x_max = int(w * self.zones['center']['h_range'][0] / 100), \
                               int(w * self.zones['center']['h_range'][1] / 100)
                zona_center = arr[y_min:y_max, x_min:x_max]
            else:
                zona_center = arr[y_min:y_max, :]
            
            if zona_center.size > 0:
                hash_val = self._hash_from_array(zona_center)
                hashes['center'] = hash_val
        
        # ZONA 3: Borde derecho (símbolos laterales, elementos decorativos)
        if self.zones['borde_der']['h_range']:
            x_min, x_max = int(w * self.zones['borde_der']['h_range'][0] / 100), \
                           int(w * self.zones['borde_der']['h_range'][1] / 100)
            zona_der = arr[:, x_min:x_max]
            if zona_der.size > 0:
                hash_val = self._hash_from_array(zona_der)
                hashes['borde_der'] = hash_val
        
        return hashes
    
    def _hash_from_array(self, arr):
        """
        Generar hash de un array numpy usando DCT.
        
        Args:
            arr: Array de imagen (escala de grises).
            
        Returns:
            float: Valor de hash normalizado.
        """
        try:
            # Convertir a float32 para evitar problemas
            arr_float = arr.astype(np.float32)
            
            # Aplicar DCT 2D
            dct = np.fft.fft2(arr_float)
            dct_shift = np.fft.ifftshift(np.abs(dct))
            
            # Extraer coeficientes de baja frecuencia
            h, w = dct_shift.shape
            # Tomar 1/4 del centro (baja frecuencia)
            h_low, w_low = h // 4, w // 4
            low_freq = dct_shift[h_low:2*h_low, w_low:2*w_low]
            
            # Normalizar y extraer valor
            if low_freq.size > 0:
                mean_val = np.mean(np.real(low_freq))
                return float(mean_val / np.max(np.abs(low_freq)))  # Normalizado -1 a 1
            return 0.0
            
        except Exception as e:
            return None
    
    def compute_multi_zone_hashes(self, image_path, output_format='detailed'):
        """
        Generar hashes multi-zona para una imagen.
        
        Args:
            image_path: Ruta a la imagen.
            output_format: 'detailed' (dict) o 'summary' (str).
            
        Returns:
            Dict o string: Hashes por zona.
        """
        try:
            # Cargar imagen
            img = Image.open(image_path).convert('L')  # Escala de grises
            
            # Extraer zonas
            hashes = self.extract_zones(img)
            
            if not hashes:
                print(f"  ⚠️ No se pudo procesar {image_path}")
                return None
            
            # Formatear salida
            if output_format == 'summary':
                summary_parts = []
                for zona, hash_val in hashes.items():
                    if hash_val is not None:
                        summary_parts.append(f"{zona}: {hash_val:.4f}")
                return ' | '.join(summary_parts)
            else:
                # Devolver dict detallado
                return {
                    'path': image_path,
                    'zones': hashes,
                    'all_values': [h for h in hashes.values() if h is not None]
                }
                
        except Exception as e:
            print(f"  ⚠️ Error con {image_path}: {e}")
            return None
    
    def batch_process(self, image_folder, zones_only=False, output_file=None):
        """
        Procesar todas las imágenes en una carpeta.
        
        Args:
            image_folder: Carpeta de imágenes.
            zones_only: Solo generar hashes, no buscar duplicados.
            output_file: Archivo de salida.
            
        Returns:
            Dict: {imagen: hashes_por_zona}
        """
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
                # Generar hashes
                hash_result = self.compute_multi_zone_hashes(
                    img_path,
                    output_format='detailed' if zones_only else 'detailed'
                )
                
                if hash_result:
                    results[os.path.basename(img_path)] = hash_result
                    
                    # Progress bar
                    sys.stdout.write(f"\rProcesando: {len(results)}/{len(image_files)}")
                    sys.stdout.flush()
                
            except Exception as e:
                print(f"\n  ⚠️ Error con {img_path}: {e}")
                continue
        
        # Guardar resultados
        if output_file and results:
            with open(output_file, 'w') as f:
                f.write("# VTES Multi-Zone Perceptual Hashes\n")
                f.write(f"# Total: {len(results)} cartas\n\n")
                
                for img_name, data in sorted(results.items()):
                    zones = data['zones']
                    f.write(f"\n[{img_name}]\n")
                    for zona, hash_val in zones.items():
                        if hash_val is not None:
                            f.write(f"  {zona}: {hash_val:.6f}\n")
            
            print(f"\n  ✅ Hashes guardados en: {output_file}")
        
        return results
    
    def compare_images(self, image_path1, image_path2):
        """
        Comparar dos imágenes por zonas.
        
        Args:
            image_path1: Primera imagen.
            image_path2: Segunda imagen.
            
        Returns:
            Dict con comparaciones por zona.
        """
        hash1 = self.compute_multi_zone_hashes(image_path1)
        hash2 = self.compute_multi_zone_hashes(image_path2)
        
        if not hash1 or not hash2:
            return None
        
        comparison = {}
        
        for zona in hash1['zones']:
            val1 = hash1['zones'][zona]
            val2 = hash2['zones'].get(zona)
            
            if val1 is not None and val2 is not None:
                # Normalizar a -1 a 1
                diff = abs(val1 - val2)
                similarity = 1 - diff  # Si son iguales, similarity = 1
                
                comparison[zona] = {
                    'image1': val1,
                    'image2': val2,
                    'difference': diff,
                    'similarity': similarity
                }
        
        return comparison


def main():
    """Función principal con help de uso."""
    
    parser = argparse.ArgumentParser(
        description='VTES Multi-Zone Perceptual Hash Matching - Matching por zonas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  # Hash por zonas para cartas_vtes
  python vtes_ph_zonas.py --folder cartas_vtes
  
  # Comparar dos cartas
  python vtes_ph_zonas.py --compare cartas_vtes/img1.jpg cartas_vtes/img2.jpg
  
  # Ver detalles de zonas
  python vtes_ph_zonas.py --folder cartas_vtes --zones-only
  
  # Personalizar zonas
  python vtes_ph_zonas.py --folder cartas_vtes --zones "bordes:10,90" "center:20,80"
        '''
    )
    
    parser.add_argument('--folder', '-f', type=str,
                       help='Carpeta de cartas (opcional, si se usa --compare)')
    parser.add_argument('--compare', '-c', type=str, nargs='+',
                       help='Comparar estas imágenes (ej: img1.jpg img2.jpg)')
    parser.add_argument('--zones-only', '-z', action='store_true',
                       help='Solo generar hashes, no buscar duplicados')
    parser.add_argument('--output', '-o', type=str, default='zones_hashes.txt',
                       help='Archivo de salida (default: zones_hashes.txt)')
    parser.add_argument('--hash-size', '-h', type=int, default=8,
                       choices=[4, 6, 8],
                       help='Tamaño del hash en bits (default: 8)')
    parser.add_argument('--zones', type=str, default=None,
                       help='Configurar zonas personalizadas (ej: "bordes:10,90" "center:20,80")')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar detalles')
    
    args = parser.parse_args()
    
    # Crear matcher
    matcher = VTESMultiZoneHash(
        hash_size=args.hash_size,
        zones=args.zones
    )
    
    print("=" * 70)
    print("🦞 VTES Multi-Zone Perceptual Hash Matching")
    print("=" * 70)
    
    if args.compare:
        # Comparar imágenes específicas
        print(f"\n🔍 Comparando imágenes:")
        for img in args.compare:
            print(f"  - {img}")
        
        # Comparar primera con segunda, segunda con tercera, etc.
        results = []
        for i in range(len(args.compare)):
            for j in range(i + 1, len(args.compare)):
                result = matcher.compare_images(
                    args.compare[i],
                    args.compare[j]
                )
                
                if result:
                    print(f"\n  🔬 Comparación: {os.path.basename(args.compare[i])} vs {os.path.basename(args.compare[j])}")
                    
                    for zona, data in result.items():
                        print(f"    📍 {zona}:")
                        print(f"      Diff: {data['difference']:.4f} (Similarity: {data['similarity']:.2%})")
                    
                    results.append(result)
    
    elif args.folder:
        # Procesar carpeta
        print(f"\n📂 Carpeta: {args.folder}")
        matcher.batch_process(
            image_folder=args.folder,
            zones_only=args.zones_only,
            output_file=args.output
        )
    
    else:
        parser.print_help()
    
    print(f"\n{'='*70}")
    print("✅ Procesamiento completado!")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
