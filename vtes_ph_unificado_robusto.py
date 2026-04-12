#!/usr/bin/env python3
"""
VTES Perceptual Hash - CORREGIDO con AVG POOLING + BINARIZACIÓN
Reemplaza DCT por método estándar perceptual.
Genera hashes binarios de 8 bits por zona.

Método:
1. Resize imagen con avg pooling (reducir resolución)
2. Binarizar con umbral 128 (valores >=128 → '1', <128 → '0')
3. Agrupar en chunks de 8 bits
4. Retornar hex string de 6 caracteres (3 bytes × 2 hex digits)

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
    """
    Hash perceptual con AVG POOLING + BINARIZACIÓN (CORREGIDO).
    Genera hashes binarios de 8 bits por zona.
    """
    
    def __init__(self, hash_size=8):
        self.hash_size = hash_size
    
    def get_default_zones_3_areas(self):
        """
        Las 3 Áreas Estratégicas.
        """
        return {
            'top_superior': (0, 15, 0, 100),      # Título + Símbolo Edición
            'imagen_central': (10, 65, 10, 65),   # Arte (forma)
            'banda_lateral': (0, 25, 0, 100),     # Clan + Tipo + Coste
        }
    
    def avg_pooling(self, image, size=8):
        """
        Aplicar avg pooling para reducir resolución de imagen.
        """
        w, h = image.size
        new_w, new_h = w // size, h // size
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return resized
    
    def extract_zone_hash(self, image, zone_name):
        """
        Extraer hash binario de una zona.
        
        Args:
            image: Imagen PIL.
            zone_name: Nombre de zona ('top_superior', 'imagen_central', 'banda_lateral').
            
        Returns:
            Hash binario de 6 caracteres hex (3 bytes) o None.
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
            zonas_config = {
                'top_superior': (0, 15, 0, 100),
                'imagen_central': (10, 65, 10, 65),
                'banda_lateral': (0, 25, 0, 100),
            }
            
            if zone_name not in zonas_config:
                zone_name = 'imagen_central'
            
            x_min_pct, x_max_pct, y_min_pct, y_max_pct = zonas_config[zone_name]
            
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
            
            # 7. Binarizar con umbral 128
            bits = ['1' if p >= 128 else '0' for p in zona_flat]
            
            # 8. Agrupar en chunks de 8 bits
            hash_bytes = []
            for i in range(0, len(bits), 8):
                chunk = bits[i:i+8]
                if len(chunk) < 8:
                    chunk.extend(['0'] * (8 - len(chunk)))
                byte_val = int(''.join(chunk), 2)
                hash_bytes.append(f'{byte_val:02x}')
            
            # 9. Retornar string hex
            return ''.join(hash_bytes) if hash_bytes else '00'
            
        except Exception as e:
            print(f"    ⚠️ Error en zona {zone_name}: {e}")
            return None
    
    def compute_zone_hashes(self, image, zones=None):
        """
        Generar hashes para las 3 áreas.
        """
        if zones is None:
            zones = self.get_default_zones_3_areas()
        
        hashes = {}
        
        for zona_name in zones.keys():
            hash_val = self.extract_zone_hash(image, zona_name)
            if hash_val is not None:
                hashes[zona_name] = hash_val
        
        return hashes
    
    def compute_batch_hashes(self, image_folder, output_file=None, strict=False):
        """
        Generar hashes para todas las imágenes en carpeta.
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
        
        # Validar imágenes antes de procesar
        valid_files = []
        corrupted_files = []
        
        for img_path in image_files:
            try:
                # Intentar abrir como imagen
                image = Image.open(img_path)
                
                # Verificar si es imagen válida (tiene modo y tamaño)
                if image.mode and image.size:
                    valid_files.append(img_path)
                    image.close()
                else:
                    print(f"  ⚠️ Imagen inválida: {img_path}")
                    corrupted_files.append(img_path)
                    
            except Exception as e:
                corrupted_files.append(img_path)
                print(f"  ⚠️ Archivo corrupto: {img_path} - {e}")
        
        print(f"  ✅ Válidas: {len(valid_files)} | ❌ Corruptas: {len(corrupted_files)}")
        
        # Si hay imágenes corruptas, preguntar si continuar
        if corrupted_files and not strict:
            print(f"  💡 Estas imágenes se saltarán automáticamente")
        
        # Procesar solo imágenes válidas
        results = {}
        skipped = 0
        
        for img_path in valid_files:
            try:
                image = Image.open(img_path)
                hashes = self.compute_zone_hashes(image)
                
                if hashes:
                    results[os.path.basename(img_path)] = hashes
                else:
                    print(f"  ⚠️ No se pudo generar hash para {img_path}")
                    skipped += 1
                    
            except Exception as e:
                print(f"  ⚠️ Error inesperado con {img_path}: {e}")
                skipped += 1
                continue
        
        # Guardar resultados
        if output_file and results:
            with open(output_file, 'w') as f:
                f.write(f"# VTES Perceptual Hashes - CORREGIDO\n")
                f.write(f"# Método: AVG POOLING + BINARIZACIÓN (umbral 128)\n")
                f.write(f"# Total válidas: {len(valid_files)}\n")
                f.write(f"# Procesadas: {len(results)}\n")
                f.write(f"# Saltadas: {skipped}\n\n")
                
                for img_name, hashes in sorted(results.items()):
                    f.write(f"[{img_name}]\n")
                    for zona, hash_val in hashes.items():
                        f.write(f"  {zona}: {hash_val}\n")
            
            print(f"\n  ✅ Hashes guardados en: {output_file}")
        
        # Informar de archivos corruptos
        if corrupted_files:
            with open('corrupted_images.txt', 'w') as f:
                f.write("# Imágenes corruptas o inválidas\n")
                f.write(f"# Total: {len(corrupted_files)}\n\n")
                for cf in corrupted_files:
                    f.write(f"{os.path.basename(cf)}\n")
            
            print(f"\n  ⚠️ Lista de imágenes corruptas guardada en: corrupted_images.txt")
        
        return results

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='VTES Perceptual Hash - CORREGIDO (Avg Pooling + Binario)',
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
