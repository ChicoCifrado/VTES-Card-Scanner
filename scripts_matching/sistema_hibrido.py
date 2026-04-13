#!/usr/bin/env python3
"""
VTES Sistema Híbrido - Matching + Hashing
- Biblioteca: Hash banda + nombre
- Vampiro: Disciplinas + nombre
"""

import os
import json
import cv2
import numpy as np
from difflib import SequenceMatcher

VTES_JSON = '/mnt/e/VTES/VTES-Card-Scanner/eliminados/vtes.json'
BIBLIOTECA_HASHES = '/mnt/e/VTES/VTES-Card-Scanner/biblioteca_hashes.txt'

def pixelize(img, size=64):
    """Pixelizar simple."""
    img_np = np.array(img.convert('L'))
    threshold = np.percentile(img_np, 40)
    binary = (img_np > threshold).astype(np.uint8)
    
    cell = size // 4
    hash_img = []
    for i in range(4):
        for j in range(4):
            y1, y2 = i*cell, (i+1)*cell
            x1, x2 = j*cell, (j+1)*cell
            celda = binary[y1:y2, x1:x2]
            active = np.sum(celda) / celda.size
            hash_img.append('1' if active > 0.3 else '0')
    
    return ''.join(hash_img)

def extraer_hash_banda(img, w, h):
    """Extraer hash de banda lateral (izquierda)."""
    banda_img = img.crop((0, 0, int(w * 0.2), h))
    return pixelize(banda_img)

def extraer_hash_central(img, w, h):
    """Extraer hash de caja central."""
    central_img = img.crop((int(w * 0.15), int(h * 0.2), w - int(w * 0.15), h - int(h * 0.2)))
    return pixelize(central_img)

def detectar_tipo(img, w, h):
    """Detectar tipo de carta (biblioteca vs vampiro)."""
    # Análisis simple: texto inferior grande = biblioteca
    texto_inferior = img.crop((0, int(h * 0.7), w, h))
    texto_np = np.array(texto_inferior.convert('L'))
    texto_binary = (texto_np > 50).astype(np.uint8)
    texto_area = cv2.countNonZero(texto_binary)
    texto_total = texto_binary.size
    prop_texto = texto_area / texto_total if texto_total > 0 else 0
    
    if prop_texto > 0.40:
        return "biblioteca"
    return "vampiro"

def load_biblioteca_hashes():
    """Cargar hashes de biblioteca."""
    biblioteca = {}
    with open(BIBLIOTECA_HASHES, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('[') and line.endswith(']'):
            nombre = line[1:-1]
            i += 1
            banda_line = lines[i].strip()
            central_line = lines[i+1].strip()
            
            if banda_line.startswith('banda:'):
                banda = banda_line.split(':')[1].strip()
                central = central_line.split(':')[1].strip()
            else:
                banda = central = None
            
            if nombre and banda:
                biblioteca[nombre] = {'banda': banda, 'central': central}
            
            i += 2
    
    return biblioteca

def match_by_nombre(nombre, vtes_db):
    """Buscar por nombre."""
    target = nombre.lower().strip()
    matches = []
    
    for nombre_db, info in vtes_db.items():
        info_norm = nombre_db.lower().strip()
        similitud = SequenceMatcher(None, target, info_norm).ratio()
        
        if similitud > 0.75:
            matches.append({'nombre': info['nombre'], 'similitud': similitud})
    
    return sorted(matches, key=lambda x: x['similitud'], reverse=True)[:3]

def match_by_fingerprint(fp, biblioteca_db):
    """Buscar por fingerprint."""
    matches = []
    
    for nombre, info in biblioteca_db.items():
        db_banda = info.get('banda')
        
        if not db_banda:
            continue
        
        hamming = sum(c1 != c2 for c1, c2 in zip(fp, db_banda))
        similitud = 1.0 - (hamming / len(fp))
        
        if similitud > 0.8:
            matches.append({'nombre': nombre, 'similitud': similitud})
    
    return sorted(matches, key=lambda x: x['similitud'], reverse=True)[:3]

def procesar_imagen(img_path, vtes_db):
    """Procesar una imagen."""
    try:
        img = Image.open(img_path)
        w, h = img.size
        
        # Detectar tipo
        tipo = detectar_tipo(img, w, h)
        
        # Extraer hashes
        hash_banda = extraer_hash_banda(img, w, h)
        hash_central = extraer_hash_central(img, w, h)
        
        # Matching
        matches_nombre = match_by_nombre(os.path.basename(img_path), vtes_db)
        
        biblioteca = load_biblioteca_hashes()
        matches_hash = match_by_fingerprint(hash_banda, biblioteca)
        
        return {
            'nombre': os.path.basename(img_path),
            'tipo': tipo,
            'hash_banda': hash_banda,
            'hash_central': hash_central,
            'matches_nombre': matches_nombre,
            'matches_hash': matches_hash,
        }
    
    except Exception as e:
        print(f"Error {img_path}: {e}")
        return None

def procesar_carpeta(folder, output):
    """Procesar carpeta completa."""
    
    images = [os.path.join(folder, f) for f in os.listdir(folder) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"📂 Carpeta: {folder}")
    print(f"📁 Imágenes: {len(images)}")
    
    # Cargar DBs
    try:
        with open(VTES_JSON, 'r') as f:
            data = json.load(f)
        
        vtes_db = {}
        for item in data:
            nombre = item.get('name', item.get('_name', ''))
            if nombre:
                vtes_db[nombre] = {'nombre': nombre}
        
        print(f"✅ Cargadas {len(vtes_db)} cartas VTES")
    except Exception as e:
        print(f"⚠️ Error cargando vtes.json: {e}")
        vtes_db = {}
    
    biblioteca = load_biblioteca_hashes()
    print(f"✅ Cargadas {len(biblioteca)} cartas biblioteca")
    
    results = []
    for img_path in images:
        try:
            resultado = procesar_imagen(img_path, vtes_db)
            if resultado:
                results.append(resultado)
        except Exception as e:
            print(f"Error {os.path.basename(img_path)}: {e}")
            continue
    
    # Guardar
    with open(output, 'w') as out:
        out.write("# VTES Sistema Híbrido\n")
        out.write(f"# Total: {len(results)} cartas\n\n")
        
        for r in results:
            out.write(f"[{r['nombre']}]\n")
            out.write(f"  tipo: {r['tipo']}\n")
            out.write(f"  hash_banda: {r['hash_banda']}\n")
            out.write(f"  hash_central: {r['hash_central']}\n")
            out.write(f"  matches_nombre:\n")
            for m in r['matches_nombre']:
                if 'nombre' in m:
                    out.write(f"    → {m['nombre']} ({m['similitud']:.2f})\n")
            out.write(f"  matches_hash:\n")
            for m in r['matches_hash']:
                if 'nombre' in m:
                    out.write(f"    → {m['nombre']} ({m['similitud']:.2f})\n")
            out.write("\n")
    
    print(f"✅ Resultados guardados: {output}")
    
    biblioteca_count = sum(1 for r in results if r['tipo'] == 'biblioteca')
    vampiro_count = sum(1 for r in results if r['tipo'] == 'vampiro')
    
    print(f"\n📊 Estadísticas:")
    print(f"  Biblioteca: {biblioteca_count}")
    print(f"  Vampiro: {vampiro_count}")

if __name__ == '__main__':
    import argparse
    from PIL import Image
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', '-f', required=True)
    parser.add_argument('--output', default='sistema_hibrido_matches.txt')
    args = parser.parse_args()
    
    procesar_carpeta(args.folder, args.output)
