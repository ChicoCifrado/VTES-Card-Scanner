#!/usr/bin/env python3
"""
VTES Vampiro Matcher - Versión Fija
Matching simple por nombre (sin pixelización)
"""

import os
import json
from difflib import SequenceMatcher

VTES_JSON = '/mnt/e/VTES/VTES-Card-Scanner/eliminados/vtes.json'

def load_vtes():
    """Cargar base de datos."""
    cartas = {}
    with open(VTES_JSON, 'r') as f:
        data = json.load(f)
    
    for item in data:
        nombre = item.get('name', item.get('_name', item.get('printed_name', '')))
        if nombre and len(nombre) > 2:
            cartas[nombre] = {'nombre': nombre}
    
    return cartas

def match(nombre_archivo, cartas_db):
    """Matchear carta por nombre."""
    target = nombre_archivo.lower().strip()
    matches = []
    
    for nombre_db, info in cartas_db.items():
        info_norm = nombre_db.lower().strip()
        similitud = SequenceMatcher(None, target, info_norm).ratio()
        
        if similitud > 0.75:
            matches.append({'nombre': info['nombre'], 'similitud': similitud})
    
    return sorted(matches, key=lambda x: x['similitud'], reverse=True)[:3]

def procesar_carpeta(folder, output):
    """Procesar carpeta."""
    
    images = [os.path.join(folder, f) for f in os.listdir(folder) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"📂 {len(images)} imágenes")
    
    cartas_db = load_vtes()
    if not cartas_db:
        print("❌ Sin DB")
        return
    
    results = []
    for img_path in images:
        try:
            matches = match(os.path.basename(img_path), cartas_db)
            results.append({'nombre': os.path.basename(img_path), 'matches': matches})
        except Exception as e:
            print(f"Error con {os.path.basename(img_path)}: {e}")
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
    procesar_carpeta(args.folder, args.output)
