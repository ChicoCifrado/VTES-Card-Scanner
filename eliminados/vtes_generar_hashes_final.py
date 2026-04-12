#!/usr/bin/env python3
"""
Generador de hashes VTES - Versión corregida y funcionando
"""

import sys
import os
from PIL import Image
import numpy as np

# Configurar zonas
zones = {
    'top_superior': (0, 15, 0, 100),
    'imagen_central': (10, 65, 10, 90),
    'banda_lateral': (0, 100, 0, 25),
}

def extract_zone_hash(arr, y_range, x_range):
    """Extraer hash de una zona usando FFT."""
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
        
        # Aplicar FFT y extraer hash
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
        
    except Exception as e:
        return None

def generar_hashes_carpeta(carpeta, output_file):
    """Generar hashes para todas las imágenes en carpeta y guardar en archivo."""
    
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
            arr = np.array(image)
            
            hashes = {}
            for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zones.items():
                hash_val = extract_zone_hash(arr, (y_min_pct, y_max_pct), (x_min_pct, x_max_pct))
                if hash_val is not None:
                    hashes[zona_name] = hash_val
            
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

if __name__ == '__main__':
    carpeta = '/mnt/e/VTES/VTES-Card-Scanner/cartas_vtes/jpg'
    output = '/mnt/e/VTES/VTES-Card-Scanner/vtes_hashes_completos.txt'
    
    generar_hashes_carpeta(carpeta, output)
