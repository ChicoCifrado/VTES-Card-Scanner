#!/usr/bin/env python3
"""
VTES Card Scanner - Unificado v1.0
Dataset + Hashing + Matching en un único script.
"""

import os
import sys
import json
import numpy as np
from PIL import Image
import argparse

# === CONFIGURACIÓN ===
ZONAS = {
    'top_superior': (0, 15, 0, 100),      # Título + Símbolo Edición
    'imagen_central': (10, 65, 0, 100),   # Arte (forma)
    'banda_lateral': (0, 25, 0, 100),     # Clan + Tipo + Coste
}

# === FUNCIONES ===

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

def generate_dataset(num=100, folder='cartas_vtes/jpg', background='fondos_vtes/dark.jpg',
                     augmentations='all', intensity=0.5, output='vtes-dataset', outline=False):
    """Generar dataset con augmentations."""
    
    # Importar PIL si no está ya disponible
    from PIL import Image
    
    # Obtener cartas y fondos
    cartas = [os.path.join(folder, f) for f in os.listdir(folder) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))][:num]
    
    if not cartas:
        print("❌ Sin cartas disponibles")
        return
    
    print(f"🚀 Generando {num} cartas...")
    
    # Generar imágenes
    for i, card_path in enumerate(cartas):
        try:
            # Leer carta
            card = Image.open(card_path).convert('RGBA')
            
            # Leer fondo
            if i == 0:
                bg = Image.open(background).convert('RGBA').resize((1080, 1080), Image.LANCZOS)
            else:
                bg = bg.resize((1080, 1080), Image.LANCZOS)
            
            # Colocar carta aleatoria
            import random
            scale = random.uniform(0.08, 0.15)
            card_ratio = card.width / card.height
            new_size = int(1080 * scale)
            new_width = int(new_size * card_ratio)
            new_height = new_size
            
            if new_width + new_height > 2160:
                new_width = int(1080 * scale * card_ratio)
                new_height = int(1080 * scale)
            
            card_resized = card.resize((new_width, new_height), Image.LANCZOS)
            card_rotated = card_resized.rotate(random.uniform(-180, 180), expand=False, resample=Image.BICUBIC)
            
            # Calcular posición
            actual_width, actual_height = card_rotated.size
            paste_x = random.randint(0, 1080 - actual_width)
            paste_y = random.randint(0, 1080 - actual_height)
            
            # Aplicar augmentations
            aug_card = card_rotated.convert('RGB')
            
            if augmentations in ['gaussian', 'all'] and intensity > 0:
                sigma = 0.3 + int(intensity * 1.2)
                aug_card = aug_card.filter(ImageFilter.GaussianBlur(radius=sigma))
            
            if augmentations in ['counter', 'all'] and intensity > 0:
                alpha = int(intensity * 100)
                obs_size = random.randint(5, 15)
                obs_x, obs_y = random.randint(obs_size, aug_card.width - obs_size), \
                                random.randint(obs_size, aug_card.height - obs_size)
                obs_shape = Image.new('RGBA', (obs_size, obs_size), (50, 50, 50, alpha))
                aug_card.paste(obs_shape, (obs_x, obs_y), obs_shape.split()[3])
            
            if augmentations in ['brightness', 'all'] and intensity > 0:
                brightness = 1.0 + (random.uniform(-0.2, 0.2) * intensity)
                aug_card = aug_card.point(lambda x: int(255 * pow(x / 255.0, 1.1 / brightness)))
            
            if augmentations == 'flip' and intensity >= 1.0:
                aug_card = aug_card.transpose(Image.FLIP_LEFT_RIGHT)
            
            # Guardar imagen
            folder_img = os.path.join(output, f'{i:06d}.jpg')
            os.makedirs(os.path.dirname(folder_img), exist_ok=True)
            aug_card.save(folder_img, quality=90)
            
            print(f"  ✓ {i+1}/{num}")
            
        except Exception as e:
            print(f"  ⚠️ Error en carta {i+1}: {e}")
    
    print(f"\n✅ Dataset generado en: {output}/")

def generate_hashes(folder='cartas_vtes/jpg', output='vtes_hashes.txt'):
    """Generar hashes para todas las imágenes."""
    
    images = [os.path.join(folder, f) for f in os.listdir(folder) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
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

def find_matches(hash_file='vtes_hashes.txt', tolerance=0):
    """Encontrar cartas similares por hash."""
    
    hashes = {}
    with open(hash_file, 'r') as f:
        lines = f.readlines()[11:]  # Saltar cabecera
    
    for line in lines:
        if line.strip():
            parts = line.strip().split(': ')
            if len(parts) == 2:
                zona, hash_bits = parts
                key = f"carta:{zona}:{hash_bits}"
                hashes[key] = {
                    'zone': zona,
                    'hash': hash_bits,
                    'bits': len(hash_bits)
                }
    
    print(f"\n🔍 Analizando {len(hashes)} hashes...")
    print(f"  Tolerancia: {tolerance}")
    
    # Agrupar por hash
    clusters = {}
    for key, data in hashes.items():
        cluster_key = int(data['hash'], 2) // (2 ** (8 - tolerance)) * (2 ** (8 - tolerance))
        if cluster_key not in clusters:
            clusters[cluster_key] = []
        clusters[cluster_key].append({
            'key': key,
            'hash': data['hash'],
            'zone': data['zone']
        })
    
    # Mostrar clusters
    if clusters:
        print(f"\n🎯 Encontrados {len(clusters)} clusters de cartas similares:")
        for cluster_key, items in sorted(clusters.items()):
            print(f"  Cluster {cluster_key}: {len(items)} cartas")
            for item in items[:3]:  # Mostrar primeras 3
                print(f"    - {item['key']}")
    
    return clusters

# === MAIN ===

def main():
    parser = argparse.ArgumentParser(description='VTES Card Scanner Unificado')
    subparsers = parser.add_subparsers(dest='command', help='Comando')
    
    # Generate
    gen_parser = subparsers.add_parser('generate', help='Generar dataset')
    gen_parser.add_argument('--num', type=int, default=100, help='Número de imágenes')
    gen_parser.add_argument('--folder', default='cartas_vtes/jpg', help='Carpeta de cartas')
    gen_parser.add_argument('--augmentations', default='all', help='gaussian|counter|brightness|flip|all')
    gen_parser.add_argument('--intensity', type=float, default=0.5, help='0.0-1.0')
    gen_parser.add_argument('--output', default='vtes-dataset', help='Directorio de salida')
    
    # Hash
    hash_parser = subparsers.add_parser('hash', help='Generar hashes')
    hash_parser.add_argument('--folder', default='cartas_vtes/jpg', help='Carpeta de cartas')
    hash_parser.add_argument('--output', default='vtes_hashes.txt', help='Archivo de salida')
    
    # Match
    match_parser = subparsers.add_parser('match', help='Encontrar similares')
    match_parser.add_argument('--hashes', default='vtes_hashes.txt', help='Archivo de hashes')
    match_parser.add_argument('--tolerance', type=int, default=0, help='0-255')
    
    # Help
    parser.add_argument('--help', '-h', action='store_true', help='Mostrar ayuda')
    
    args = parser.parse_args()
    
    if args.help or not args.command:
        parser.print_help()
        return
    
    # Ejecutar comando
    if args.command == 'generate':
        generate_dataset(
            num=args.num,
            folder=args.folder,
            augmentations=args.augmentations,
            intensity=args.intensity,
            output=args.output
        )
    
    elif args.command == 'hash':
        generate_hashes(
            folder=args.folder,
            output=args.output
        )
    
    elif args.command == 'match':
        find_matches(
            hash_file=args.hashes,
            tolerance=args.tolerance
        )

if __name__ == '__main__':
    main()
