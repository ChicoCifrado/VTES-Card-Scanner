#!/usr/bin/env python3
"""
VTES Vampiro Matcher - Versión Minimalista
Matching simple:
- Pixelización binaria
- Similaridad de fingerprint
- Normalización de nombre
"""

import os
import cv2
import numpy as np
from PIL import Image

# === CONFIG ===
VTES_JSON = '/mnt/e/VTES/VTES-Card-Scanner/eliminados/vtes.json'

def pixelize(img, size=64):
    """Pixelizar arte central, return fingerprint binario."""
    try:
        w, h = img.size
        # Centro con márgenes
        mx, my = 10, 15
        x1, y1 = mx, my
        x2, y2 = w - mx, h - my
        
        centro = img.crop((x1, y1, x2, y2))
        if centro.size[0] > 256:
            centro = centro.resize((256, 256), Image.LANCZOS)
        
        centro_np = np.array(centro.convert('L'))
        threshold = np.percentile(centro_np, 40)
        binary = centro_np > threshold
        
        # Resize
        if binary.size > 4096:
            binary = cv2.resize(binary.astype(np.uint8), (size, size))
        
        # 4x4 celdas
        cell = size // 4
        fp = []
        for i in range(4):
            for j in range(4):
                y1_c, y2_c = i*cell, (i+1)*cell
                x1_c, x2_c = j*cell, (j+1)*cell
                celda = binary[y1_c:y2_c, x1_c:x2_c]
                ratio = np.sum(celda) / celda.size
                fp.append('1' if ratio > 0.3 else '0')
        
        return ''.join(fp), int(np.sum(binary))
    
    except Exception as e:
        return '0'*16, 0

def load_vtes():
    """Cargar base de datos."""
    try:
        with open(VTES_JSON, 'r') as f:
            data = [item for item in f]  # JSON no parseado, buscar por nombre
        
        cartas = {}
        # Parsear JSON (lento pero necesario)
        import json
        with open(VTES_JSON, 'r') as f:
            data = json.load(f)
        
        for item in data:
            nombre = item.get('name', item.get('_name', item.get('printed_name', '')))
            if nombre and len(nombre) > 2:
                disciplinas = item.get('disciplinas', item.get('disciplines', []))
                cartas[nombre] = {
                    'nombre': nombre,
                    'disciplinas': disciplinas,
                }
        
        return cartas
    
    except Exception as e:
        print(f"Error: {e}")
        return {}

def normalize_name(nombre):
    """Normalizar nombre."""
    return nombre.lower().strip().replace(',', '').replace('-', '')

def match_by_fingerprint(fp, cartas_db):
    """Buscar por fingerprint."""
    matches = []
    for nombre, info in cartas_db.items():
        db_fp = pixelize(info.get('image', None), size=64) if hasattr(info, 'image') else None
        
        # Si no tenemos fp de DB, saltar
        if not db_fp:
            continue
        
        hamming = sum(c1 != c2 for c1, c2 in zip(fp, db_fp))
        similitud = 1.0 - (hamming / len(fp))
        
        if similitud > 0.6:
            matches.append({'nombre': info['nombre'], 'similitud': similitud})
    
    return sorted(matches, key=lambda x: x['similitud'], reverse=True)[:5]

def match_by_name(nombre, cartas_db):
    """Buscar por nombre normalizado."""
    target = normalize_name(nombre)
    matches = []
    
    for nombre_db, info in cartas_db.items():
        info_norm = normalize_name(info['nombre'])
        from difflib import SequenceMatcher
        similitud = SequenceMatcher(None, target, info_norm).ratio()
        
        if similitud > 0.75:
            matches.append({'nombre': info['nombre'], 'similitud': similitud})
    
    return sorted(matches, key=lambda x: x['similitud'], reverse=True)[:5]

def process_folder(folder, output):
    """Procesar carpeta."""
    images = []
    for ext in ['.jpg', '.jpeg', '.png']:
        for f in os.listdir(folder):
            if f.lower().endswith(ext):
                images.append(os.path.join(folder, f))
    
    print(f"📂 {len(images)} imágenes")
    
    cartas_db = load_vtes()
    if not cartas_db:
        print("❌ Sin DB")
        return
    
    results = []
    for img_path in images:
        try:
            img = Image.open(img_path)
            
            # Matching
            matches = match_by_name(os.path.basename(img_path), cartas_db)
            if not matches:
                # Fallback a fingerprint
                fp, _ = pixelize(img)
                matches = match_by_fingerprint(fp, cartas_db)
            
            results.append({'nombre': os.path.basename(img_path), 'matches': matches})
        
        except Exception as e:
            continue
    
    # Guardar
    with open(output, 'w') as f:
        f.write("# VTES Matcher Simple\n")
        for r in results:
            f.write(f"[{r['nombre']}]\n")
            for m in r['matches'][:3]:
                if 'nombre' in m:
                    f.write(f"  → {m['nombre']} ({m['similitud']:.2f})\n")
    
    print(f"✅ {output}")
    print(f"📊 Encontradas: {sum(1 for r in results if r['matches'])}/{len(results)}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', '-f', required=True)
    parser.add_argument('--output', default='vampiro_simple_matches.txt')
    args = parser.parse_args()
    process_folder(args.folder, args.output)
