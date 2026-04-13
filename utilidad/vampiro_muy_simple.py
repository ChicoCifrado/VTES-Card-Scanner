#!/usr/bin/env python3
"""VTES Vampiro Matcher - Muy Simple (sin OpenCV)"""

import os
import json
from difflib import SequenceMatcher

def load_vtes():
    cartas = {}
    with open('/mnt/e/VTES/VTES-Card-Scanner/eliminados/vtes.json', 'r') as f:
        data = json.load(f)
    
    for item in data:
        nombre = item.get('name', item.get('_name', ''))
        if nombre and len(nombre) > 2:
            cartas[nombre] = {'nombre': nombre}
    return cartas

def match(nombre, cartas_db):
    target = nombre.lower().strip()
    matches = []
    
    for nombre_db, info in cartas_db.items():
        info_norm = nombre_db.lower().strip()
        similitud = SequenceMatcher(None, target, info_norm).ratio()
        
        if similitud > 0.75:
            matches.append({'nombre': info['nombre'], 'similitud': similitud})
    
    return sorted(matches, key=lambda x: x['similitud'], reverse=True)[:3]

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', '-f', required=True)
    parser.add_argument('--output', default='vampiro_muy_simple.txt')
    args = parser.parse_args()
    
    cartas_db = load_vtes()
    results = {}
    
    for f in os.listdir(args.folder):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            matches = match(f, cartas_db)
            results[f] = matches
    
    with open(args.output, 'w') as out:
        out.write(f"# VTES Vampiro Matches\n")
        for nombre, matches in results.items():
            out.write(f"[{nombre}]\n")
            for m in matches:
                if 'nombre' in m:
                    out.write(f"  → {m['nombre']} ({m['similitud']:.2f})\n")
    
    print(f"✅ {args.output}")
    print(f"📊 {len(results)} cartas")

if __name__ == '__main__':
    main()
