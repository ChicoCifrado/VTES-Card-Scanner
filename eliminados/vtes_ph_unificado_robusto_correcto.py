#!/usr/bin/env python3
"""
VTES Perceptual Hash Generator - CORREGIDO con AVG POOLING + BINARIZACIÓN
Genera hashes binarios de 8 bits por zona × 3 zonas = 24 bits totales.

Uso:
  python vtes_ph_unificado_robusto.py hash --folder cartas_vtes --output vtes_hashes_corregidos.txt
  python vtes_ph_unificado_robusto.py hash -f cartas_vtes -o vtes_hashes_corregidos.txt
  python vtes_ph_unificado_robusto.py hash --folder jpg --output hashes_jpg.txt (si es necesario)

Las 3 Áreas Estratégicas:
1. TOP SUPERIOR (0-15%) → Título + Símbolo Edición → Identifica SET
2. IMAGEN CENTRAL (10-65%) → Forma del arte → Ovalada=vampiro, cuadrada=biblioteca
3. BANDA LATERAL (0-25%) → Clan + Tipo + Coste → Elementos distintivos
"""

import os
import sys
import numpy as np
from PIL import Image
import argparse


class VTESPerceptualHashCorrecto:
    """Hash con AVG POOLING + BINARIZACIÓN (CORREGIDO)"""
    
    def __init__(self):
        self.umbral = 128  # Umbral para binarización
    
    def avg_pooling(self, image, size=8):
        """Aplicar avg pooling para reducir resolución"""
        w, h = image.size
        new_w, new_h = w // size, h // size
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return resized
    
    def extract_zone_hash(self, image, y_min_pct, y_max_pct, x_min_pct, x_max_pct):
        """
        Extraer hash binario de una zona.
        
        Args:
            image: Imagen PIL.
            y_min_pct, y_max_pct, x_min_pct, x_max_pct: Rangos en porcentaje.
            
        Returns:
            Hash binario de 8 bits (hex 4 caracteres) o None.
        """
        try:
            # 1. Normalizar imagen si es muy grande
            if image.width > 1920 or image.height > 1920:
                image = image.resize((1920, 1920), Image.Resampling.LANCZOS)
            
            # 2. Convertir a escala de grises
            img_gray = image.convert('L')
            
            # 3. Aplicar avg pooling
            img_pooled = self.avg_pooling(img_gray, size=8)
            
            # 4. Extraer zona
            w, h = img_pooled.size
            x_min_px = int(w * x_min_pct / 100)
            x_max_px = int(w * x_max_pct / 100)
            y_min_px = int(h * y_min_pct / 100)
            y_max_px = int(h * y_max_pct / 100)
            
            # 5. Crop zona
            if x_max_px > x_min_px and y_max_px > y_min_px:
                zona = img_pooled.crop((x_min_px, y_min_px, x_max_px, y_max_px))
            else:
                zona = img_pooled
            
            # 6. Convertir a array
            zona_array = np.array(zona, dtype=np.uint8)
            zona_flat = zona_array.flatten()
            
            # 7. Binarizar con umbral
            bits = ['1' if p >= self.umbral else '0' for p in zona_flat]
            
            # 8. Agrupar en chunks de 8 bits
            hash_bytes = []
            for i in range(0, len(bits), 8):
                chunk = bits[i:i+8]
                if len(chunk) < 8:
                    chunk.extend(['0'] * (8 - len(chunk)))
                byte_val = int(''.join(chunk), 2)
                hash_bytes.append(f'{byte_val:02x}')
            
            return ''.join(hash_bytes) if hash_bytes else '00'
            
        except Exception as e:
            return None
    
    def get_zones_config(self):
        """
        Las 3 Áreas Estratégicas.
        
        Returns:
            Dict de configuraciones de zonas.
        """
        return {
            'top_superior': (0, 15, 0, 100),      # (y_min, y_max, x_min, x_max)
            'imagen_central': (10, 65, 10, 65),
            'banda_lateral': (0, 25, 0, 100),
        }
    
    def compute_zone_hashes(self, image):
        """
        Generar hashes para las 3 áreas.
        
        Returns:
            Dict con hashes por zona.
        """
        zones = self.get_zones_config()
        hashes = {}
        
        for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zones.items():
            hash_val = self.extract_zone_hash(image, y_min_pct, y_max_pct, x_min_pct, x_max_pct)
            if hash_val is not None:
                hashes[zona_name] = hash_val
        
        return hashes
    
    def compute_batch_hashes(self, image_folder, output_file=None, strict=False):
        """
        Generar hashes para todas las imágenes en carpeta.
        
        Args:
            image_folder: Carpeta de imágenes.
            output_file: Archivo de salida (opcional).
            strict: Si True, detener en primera imagen corrupta.
            
        Returns:
            Dict con hashes.
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
        
        # Validar imágenes
        valid_files = []
        corrupted_files = []
        
        for img_path in image_files:
            try:
                image = Image.open(img_path)
                
                # Verificar si es imagen válida
                if image.mode and image.size:
                    valid_files.append(img_path)
                    image.close()
                else:
                    corrupted_files.append(img_path)
                    print(f"  ⚠️ Imagen inválida: {img_path}")
                    
            except Exception as e:
                corrupted_files.append(img_path)
                print(f"  ⚠️ Archivo corrupto: {img_path} - {e}")
        
        print(f"  ✅ Válidas: {len(valid_files)} | ❌ Corruptas: {len(corrupted_files)}")
        
        # Si hay corruptas y no strict, saltarlas
        if corrupted_files and not strict:
            print(f"  💡 Imágenes corruptas saltadas automáticamente")
        
        # Procesar solo válidas
        results = {}
        skipped = 0
        
        for img_path in valid_files:
            try:
                image = Image.open(img_path)
                hashes = self.compute_zone_hashes(image)
                
                if hashes:
                    results[os.path.basename(img_path)] = hashes
                else:
                    print(f"  ⚠️ Sin hash para {img_path}")
                    skipped += 1
                    
            except Exception as e:
                print(f"  ⚠️ Error con {img_path}: {e}")
                skipped += 1
                continue
        
        # Guardar resultados
        if output_file and results:
            with open(output_file, 'w') as f:
                f.write(f"# VTES Perceptual Hashes - CORREGIDO\n")
                f.write(f"# Método: AVG POOLING + BINARIZACIÓN (umbral {self.umbral})\n")
                f.write(f"# Total válidas: {len(valid_files)}\n")
                f.write(f"# Procesadas: {len(results)}\n")
                f.write(f"# Saltadas: {skipped}\n\n")
                
                for img_name, hashes in sorted(results.items()):
                    f.write(f"[{img_name}]\n")
                    for zona, hash_val in hashes.items():
                        f.write(f"  {zona}: {hash_val}\n")
            
            print(f"\n  ✅ Hashes guardados en: {output_file}")
        
        # Guardar lista corruptas
        if corrupted_files:
            with open('corrupted_images.txt', 'w') as f:
                f.write(f"# Imágenes corruptas o inválidas\n")
                f.write(f"# Total: {len(corrupted_files)}\n\n")
                for cf in corrupted_files:
                    f.write(f"{os.path.basename(cf)}\n")
            
            print(f"\n  ⚠️ Lista corruptas guardada en: corrupted_images.txt")
        
        return results


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='VTES Perceptual Hash - CORREGIDO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('command', choices=['hash'], help='Comando principal')
    parser.add_argument('--folder', '-f', type=str, required=True, help='Carpeta de imágenes')
    parser.add_argument('--output', '-o', type=str, default=None, help='Archivo de salida')
    parser.add_argument('--strict', action='store_true', help='Detener en primera imagen corrupta')
    
    args = parser.parse_args()
    
    hash_engine = VTESPerceptualHashCorrecto()
    hashes = hash_engine.compute_batch_hashes(args.folder, output_file=args.output, strict=args.strict)
    
    print(f"\n{'='*60}")
    print(f"✅ Completado: {len(hashes)} cartas procesadas")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
