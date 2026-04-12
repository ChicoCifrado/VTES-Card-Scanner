#!/usr/bin/env python3
"""
Generador de hashes VTES - Versión simple para guardar resultados
"""

import sys
sys.path.insert(0, '/mnt/e/VTES/VTES-Card-Scanner')
from vtes_ph_unificado_robusto import VTESPerceptualHash3Areas
import os

def generar_hashes_carpeta(carpeta, output_file):
    """Generar hashes para todas las imágenes en carpeta y guardar en archivo."""
    
    hash_engine = VTESPerceptualHash3Areas()
    
    # Configurar zonas
    zones = hash_engine.get_default_zones_3_areas()
    
    print(f"\n📂 Carpeta: {carpeta}")
    
    # Buscar imágenes
    extensions = ['.jpg', '.jpeg', '.png']
    image_files = []
    
    for ext in extensions:
        for filename in os.listdir(carpeta):
            if filename.lower().endswith(ext):
                image_files.append(os.path.join(carpeta, filename))
    
    print(f"  🔍 Encontradas {len(image_files)} imágenes")
    
    # Guardar estadísticas
    with open(output_file, 'w') as f:
        f.write("# VTES Perceptual Hashes - 3 Áreas Estratégicas\n")
        f.write("# Carpeta: {}\n".format(carpeta))
        f.write("# Total imágenes: {}\n".format(len(image_files)))
        f.write("# Zonas: top_superior, imagen_central, banda_lateral\n\n")
    
    # Procesar imágenes
    resultados = {}
    
    for img_path in image_files:
        try:
            image = Image.open(img_path).convert('L')
            hashes = hash_engine.compute_zone_hashes(image, zones)
            
            if hashes:
                img_name = os.path.basename(img_path)
                resultados[img_name] = hashes
                
                # Guardar en archivo
                with open(output_file, 'a') as f:
                    f.write(f"\n[{img_name}]\n")
                    for zona, hash_val in hashes.items():
                        f.write(f"  {zona}: {hash_val:.6f}\n")
                
                # Imprimir progreso
                sys.stdout.write(f"\rProcesando: {len(resultados)}/{len(image_files)}")
                sys.stdout.flush()
                
        except Exception as e:
            continue  # Saltar errores
    
    print(f"\n\n✅ Total procesadas: {len(resultados)}")
    print(f"💾 Hashes guardados en: {output_file}")
    
    return resultados

def main():
    import PIL.Image as Image
    
    carpeta = '/mnt/e/VTES/VTES-Card-Scanner/cartas_vtes/jpg'
    output = '/mnt/e/VTES/VTES-Card-Scanner/vtes_hashes_completos.txt'
    
    generar_hashes_carpeta(carpeta, output)
    
    return resultados if 'resultados' in locals() else None

if __name__ == '__main__':
    main()
