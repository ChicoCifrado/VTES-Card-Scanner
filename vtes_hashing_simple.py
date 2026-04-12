#!/usr/bin/env python3
"""
VTES Hashing Simple - AVG POOLING + BINARIZACIÓN
Genera hashes binarios de 8 bits por zona.
"""

import os
import sys
import numpy as np
from PIL import Image

# === CONFIGURACIÓN ===
ZONAS = {
    'top_superior': (0, 15, 0, 100),
    'imagen_central': (10, 65, 0, 100),
    'banda_lateral': (0, 25, 0, 100),
}

def extract_hash(img, zone_name, hash_bits=8):
    """Extraer hash binario de una zona."""
    try:
        if img.width > 1920 or img.height > 1920:
            img = img.resize((1920, 1920), Image.LANCZOS)
        
        gray = img.convert('L')
        small = gray.resize((8, 8), Image.LANCZOS)
        arr = np.array(small, dtype=np.uint8)
        
        x1_pct, x2_pct, y1_pct, y2_pct = ZONAS[zone_name]
        w, h = arr.shape
        x1, x2, y1, y2 = (int(w * pct / 100) for pct in [x1_pct, x2_pct, y1_pct, y2_pct])
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        zona = arr[y1:y2, x1:x2]
        binary = (zona >= 128).astype(np.uint8).flatten()
        bits = ''.join(map(str, binary[:hash_bits]))
        
        return bits if len(bits) == hash_bits else None
    
    except Exception as e:
        return None

def extract_all_hashes(img):
    """Extraer hashes de todas las zonas."""
    hashes = {}
    for zona_name in ZONAS.keys():
        h = extract_hash(img, zona_name)
        if h:
            hashes[zona_name] = h
    return hashes

def process_folder(folder, output):
    """Procesar carpeta y generar hashes."""
    
    images = []
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        for f in os.listdir(folder):
            if f.lower().endswith(ext):
                images.append(os.path.join(folder, f))
    
    print(f"\n📂 Carpeta: {folder}")
    print(f"  🔍 Encontradas {len(images)} imágenes")
    
    results = {}
    corrupted = []
    
    for img_path in images:
        try:
            img = Image.open(img_path)
            hashes = extract_all_hashes(img)
            
            if hashes:
                results[os.path.basename(img_path)] = hashes
            else:
                print(f"  ⚠️ Sin hash: {img_path}")
                
        except Exception as e:
            corrupted.append(img_path)
            print(f"  ⚠️ Corrupta: {img_path} - {e}")
    
    # Guardar
    if results:
        with open(output, 'w') as f:
            f.write("# VTES Hashes - AVG POOLING + BINARIZACIÓN\n")
            f.write(f"# Total: {len(results)}\n\n")
            
            for img_name, hashes in sorted(results.items()):
                f.write(f"[{img_name}]\n")
                for zona, h in hashes.items():
                    f.write(f"  {zona}: {h}\n")
        
        print(f"\n  ✅ Hashes guardados: {output}")
    
    if corrupted:
        with open('corrupted_images.txt', 'w') as f:
            f.write(f"# Corruptas: {len(corrupted)}\n\n")
            for c in corrupted:
                f.write(f"  {os.path.basename(c)}\n")
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='VTES Hashing Simple')
    parser.add_argument('command', choices=['hash'], help='Comando')
    parser.add_argument('--folder', '-f', required=True, help='Carpeta')
    parser.add_argument('--output', '-o', help='Salida')
    args = parser.parse_args()
    
    hasher = process_folder(args.folder, args.output)
    
    print(f"\n✅ Completado: {len(hasher)} cartas procesadas")

if __name__ == '__main__':
    main()
