#!/usr/bin/env python3
"""
🦇 VTES Creator - Unificador para generar dataset VTES

Genera imágenes de cartas VTES con diferentes configuraciones:
- Opciones: 1, 10, 1000 o 10000 imágenes
- Genera bounds logs (relaciones) AUTOMÁTICAMENTE
- Estructura dataset en formato YOLO (80% train, 10% val, 10% test)
- Usa multiprocessing para paralelización
- Comprime en ZIP al finalizar

📍 Ubicación: /mnt/e/VTES/VTES-Card-Scanner/
🎯 Output: vtes-dataset/
   - images/train/ (80%)
   - images/val/ (10%)
   - images/test/ (10%)
📦 ZIP: vtes-dataset.zip
"""
import os
import sys
import random
import json
import zipfile
import argparse
import multiprocessing
from PIL import Image


# === CLASES ===

class CardPlacer:
    """Clase auxiliar para colocar cartas y guardar bounds logs."""
    
    def __init__(self):
        self.bounds_log = []
    
    def check_collisions(self, bounds_list):
        """
        Detectar cartas solapadas (>=10% del área).
        Devuelve lista de pares attached.
        
        # Aquí va la toda lógica de equipos, retainers, cartas especiales, etc.
        # - Detectar solapamiento entre cartas de mismo equipo
        # - Detectar cartas de retainer
        # - Detectar cartas especiales (VIP, edición limitada)
        """
        if len(bounds_list) < 2:
            return []
        
        attached_pairs = []
        
        for i in range(len(bounds_list)):
            for j in range(i + 1, len(bounds_list)):
                b1 = bounds_list[i]
                b2 = bounds_list[j]
                
                # Calcular áreas
                area1 = b1['width'] * b1['height']
                area2 = b2['width'] * b2['height']
                
                # Verificar intersección (overlap)
                x1_min = b1['x']
                x1_max = b1['x'] + b1['width']
                y1_min = b1['y']
                y1_max = b1['y'] + b1['height']
                
                x2_min = b2['x']
                x2_max = b2['x'] + b2['width']
                y2_min = b2['y']
                y2_max = b2['y'] + b2['height']
                
                # Calcular intersección
                inter_x_min = max(x1_min, x2_min)
                inter_x_max = min(x1_max, x2_max)
                inter_y_min = max(y1_min, y2_min)
                inter_y_max = min(y1_max, y2_max)
                
                # Si hay intersección
                if inter_x_max > inter_x_min and inter_y_max > inter_y_min:
                    # Calcular área de intersección
                    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
                    
                    # Calcular porcentaje de intersección (relativo al área menor)
                    min_area = min(area1, area2)
                    overlap_percent = (inter_area / min_area) * 100 if min_area > 0 else 0
                    
                    # Si solapan >= 10%
                    if overlap_percent >= 10:
                        attached_pairs.append({
                            "name1": b1['name'],
                            "name2": b2['name'],
                            "overlap_percent": round(overlap_percent, 2),
                            "intersection": {
                                "x": inter_x_min,
                                "y": inter_y_min,
                                "width": inter_x_max - inter_x_min,
                                "height": inter_y_max - inter_y_min
                            }
                        })
        
        return attached_pairs
    
    def scale_and_place_card(self, card_file, bg_img, scale_factor=None):
        """
        Escala, rota y coloca carta manteniendo el ratio de aspecto,
        guardando bounds.
        """
        if bg_img.size != (1080, 1080):
            bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
        
        if scale_factor is None:
            scale_factor = random.uniform(0.02, 0.08)
        
        # Calcular dimensiones manteniendo ratio de aspecto
        card_original = Image.open(card_file)
        card_ratio = card_original.width / card_original.height
        
        new_size = int(1080 * scale_factor)
        new_width = int(new_size * card_ratio)
        new_height = new_size
        
        # Asegurar que caben en 1080x1080
        if new_width + new_height > 2160:  # Máximo 1080 ancho + 1080 alto
            new_width = int(1080 * scale_factor * card_ratio)
            new_height = int(1080 * scale_factor)
        
        card_img = Image.open(card_file).convert("RGBA")
        card_img = card_img.resize((new_width, new_height), Image.LANCZOS)
        
        rotation_angle = random.uniform(-180, 180)
        card_img = card_img.rotate(rotation_angle, expand=True, resample=Image.BICUBIC)
        
        paste_x = random.randint(0, 1080 - card_img.width)
        paste_y = random.randint(0, 1080 - card_img.height)
        
        card_name = os.path.basename(card_file)
        
        bounds = {
            "name": card_name,
            "x": paste_x,
            "y": paste_y,
            "width": card_img.width,
            "height": card_img.height,
            "rotation": rotation_angle,
            "scale": scale_factor,
        }
        
        if card_img.mode == 'RGBA':
            mask = card_img.split()[3]
        else:
            mask = Image.new('L', (card_img.width, card_img.height))
            mask.paste(255, (0, 0, card_img.width, card_img.height))
        
        result_img = bg_img.copy()
        result_img.paste(card_img, (paste_x, paste_y), mask)
        
        self.bounds_log.append(bounds)
        
        return result_img
    
    def get_bounds(self):
        """Devolver todos los bounds loguados"""
        return self.bounds_log
    
    def get_bounds_with_attached(self):
        """Devolver bounds con attached"""
        attached_pairs = self.check_collisions(self.bounds_log)
        
        # Añadir attached a cada bound
        bounds_with_attached = []
        for bound in self.bounds_log:
            bound_copy = bound.copy()
            attached = []
            for pair in attached_pairs:
                if pair['name1'] == bound['name']:
                    attached.append({
                        "name": pair['name2'],
                        "overlap_percent": pair['overlap_percent']
                    })
                elif pair['name2'] == bound['name']:
                    attached.append({
                        "name": pair['name1'],
                        "overlap_percent": pair['overlap_percent']
                    })
                if attached:
                    bound_copy['attached'] = attached
            bounds_with_attached.append(bound_copy)
        
        return bounds_with_attached, attached_pairs


# === FUNCIONES PARA MULTIPROCESING ===

def generate_image_wrapper(args):
    """
    Función wrapper para multiprocessing.
    args: (cartas_files, fondos_files, idx)
    """
    cartas_files, fondos_files, idx = args
    
    # Seleccionar fondo
    bg_file = random.choice(fondos_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Generar cartas
    placer = CardPlacer()
    
    for _ in range(random.randint(1, 100)):
        if cartas_files:
            card_file = random.choice(cartas_files)
            scale_factor = random.uniform(0.02, 0.08)
            bg_img = placer.scale_and_place_card(card_file, bg_img, scale_factor)
        else:
            break
    
    bounds = placer.get_bounds()
    bounds_with_attached, attached_pairs = placer.get_bounds_with_attached()
    
    # Asignar carpeta (80% train, 10% val, 10% test)
    if idx < 10:  # 0-9 -> test (10%)
        dst_dir = f"{root_dir}/test"
    elif idx < 200:  # 10-199 -> val (10%)
        dst_dir = f"{root_dir}/val"
    else:  # Resto -> train (80%)
        dst_dir = f"{root_dir}/train"
    
    dst_path = os.path.join(dst_dir, f"image_{idx:06d}.jpg")
    os.makedirs(dst_dir, exist_ok=True)
    
    # Guardar imagen
    if bg_img.mode == 'RGBA':
        bg = Image.new('RGB', bg_img.size)
        bg.paste(bg_img, mask=bg_img.split()[3])
        img = bg
    else:
        img = bg_img
    
    img.save(dst_path, quality=100)
    
    # Guardar bounds con attached
    bounds_dict = {
        "filename": os.path.basename(dst_path),
        "path": dst_path,
        "dir": os.path.basename(dst_dir),
        "num_cards": len(bounds_with_attached),
        "bounds": bounds_with_attached,
        "attached_pairs": attached_pairs
    }
    
    return bounds_dict


# === FUNCIONES ===

def generate_dataset_final(num_imagenes, cartas_files, fondos_files, root_dir):
    """
    Función principal para generar dataset con multiprocessing.
    """
    # Crear carpeta raíz
    os.makedirs(root_dir, exist_ok=True)
    
    # Preparar args para multiprocessing
    args_list = [(cartas_files, fondos_files, idx) for idx in range(num_imagenes)]
    
    print(f"🚀 Generando {num_imagenes} imágenes con multiprocessing...")
    
    # Determinar número de workers
    num_workers = min(multiprocessing.cpu_count(), num_imagenes)
    
    print(f"   Workers: {num_workers}")
    
    # Crear pool
    with multiprocessing.Pool(processes=num_workers) as pool:
        # Generar imágenes en paralelo
        all_bounds = pool.map(generate_image_wrapper, args_list)
    
    print(f"✅ Imágenes generadas en {num_workers} procesos en paralelo")
    
    # Mostrar resumen de distribución
    train_count = len([b for b in all_bounds if b['dir'] == 'train'])
    val_count = len([b for b in all_bounds if b['dir'] == 'val'])
    test_count = len([b for b in all_bounds if b['dir'] == 'test'])
    
    total_cards = sum(b['num_cards'] for b in all_bounds)
    
    print(f"\n✅ Dataset generado!")
    print(f"   Imágenes: {num_imagenes}")
    print(f"   Distribution:")
    print(f"      Train: {train_count} ({train_count/num_imagenes*100:.1f}%)")
    print(f"      Val:   {val_count} ({val_count/num_imagenes*100:.1f}%)")
    print(f"      Test:  {test_count} ({test_count/num_imagenes*100:.1f}%)")
    print(f"   Total cartas: {total_cards}")
    
    return all_bounds


# === MAIN ===

if __name__ == "__main__":
    # Parsear argumentos
    parser = argparse.ArgumentParser(description="🦇 VTES Creator - Generador de dataset")
    parser.add_argument(
        "--num", 
        type=int,
        choices=[1, 10, 1000, 10000],
        default=10,
        help="Número de imágenes a generar (1, 10, 1000, 10000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/mnt/e/VTES/VTES-Card-Scanner",
        help="Directorio de salida"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Modo secuencial (sin multiprocessing)"
    )
    
    args = parser.parse_args()
    
    num_imagenes = args.num
    target_dir = args.output
    
    print(f"🦇 VTES Creator v1.0")
    print(f"   Opción: {num_imagenes} imágenes" + (" (secuencial)" if args.sequential else " (multiprocessing)"))
    print(f"   Distribución: 80% train, 10% val, 10% test")
    print()
    
    # Rutas
    root_dir = f"{target_dir}/vtes-dataset"
    cartas_dir = f"{target_dir}/cartas_vtes"
    fondos_dir = f"{target_dir}/fondos_vtes"
    zip_path = f"{target_dir}/vtes-dataset.zip"
    
    # Verificar carpetas
    if not os.path.exists(cartas_dir):
        print(f"❌ Error: La carpeta {cartas_dir} no existe")
        sys.exit(1)
    if not os.path.exists(fondos_dir):
        print(f"❌ Error: La carpeta {fondos_dir} no existe")
        sys.exit(1)
    
    # Obtener archivos
    cartas_files = [
        os.path.join(cartas_dir, f) 
        for f in os.listdir(cartas_dir) 
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ]
    fondos_files = [
        os.path.join(fondos_dir, f) 
        for f in os.listdir(fondos_dir) 
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ]
    
    print(f"📍 Archivos:")
    print(f"   Cartas: {len(cartas_files)} archivos encontrados")
    print(f"   Fondos: {len(fondos_files)} archivos encontrados")
    print()
    
    # Crear estructura
    for subdir in ['train', 'val', 'test']:
        os.makedirs(f"{root_dir}/{subdir}", exist_ok=True)
    
    print(f"✅ Estructura creada: {root_dir}")
    print()
    
    # Generar dataset
    if not args.sequential:
        # Modo multiprocessing
        all_bounds = generate_dataset_final(
            num_imagenes, cartas_files, fondos_files, root_dir
        )
    else:
        # Modo secuencial
        print(f"🚀 Generando {num_imagenes} imágenes (secuencial)...")
        
        all_bounds = []
        for idx in range(num_imagenes):
            bg_file = random.choice(fondos_files)
            bg_img = Image.open(bg_file).convert("RGBA")
            bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
            
            placer = CardPlacer()
            
            for _ in range(random.randint(1, 100)):
                if cartas_files:
                    card_file = random.choice(cartas_files)
                    scale_factor = random.uniform(0.02, 0.08)
                    bg_img = placer.scale_and_place_card(card_file, bg_img, scale_factor)
                else:
                    break
            
            bounds = placer.get_bounds()
            
            # Asignar carpeta
            if idx < 10:  # 0-9 -> test (10%)
                dst_dir = f"{root_dir}/test"
            elif idx < 200:  # 10-199 -> val (10%)
                dst_dir = f"{root_dir}/val"
            else:  # Resto -> train (80%)
                dst_dir = f"{root_dir}/train"
            
            dst_path = os.path.join(dst_dir, f"image_{idx:06d}.jpg")
            os.makedirs(dst_dir, exist_ok=True)
            
            # Guardar imagen
            if bg_img.mode == 'RGBA':
                bg = Image.new('RGB', bg_img.size)
                bg.paste(bg_img, mask=bg_img.split()[3])
                img = bg
            else:
                img = bg_img
            
            img.save(dst_path, quality=100)
            
            bounds_dict = {
                "filename": os.path.basename(dst_path),
                "path": dst_path,
                "dir": os.path.basename(dst_dir),
                "num_cards": len(bounds),
                "bounds": bounds
            }
            all_bounds.append(bounds_dict)
            
            if num_imagenes <= 100:
                print(f"   ✓ {idx:04d}: {dst_path} ({len(bounds)} cartas)")
            else:
                print(f"   ✓ {idx:06d}")
        
        print(f"\n✅ Imágenes generadas en modo secuencial")
    
    # Mostrar resumen de distribución
    train_count = len([b for b in all_bounds if b['dir'] == 'train'])
    val_count = len([b for b in all_bounds if b['dir'] == 'val'])
    test_count = len([b for b in all_bounds if b['dir'] == 'test'])
    
    total_cards = sum(b['num_cards'] for b in all_bounds)
    
    print(f"\n✅ Dataset generado!")
    print(f"   Imágenes: {num_imagenes}")
    print(f"   Distribution:")
    print(f"      Train: {train_count} ({train_count/num_imagenes*100:.1f}%)")
    print(f"      Val:   {val_count} ({val_count/num_imagenes*100:.1f}%)")
    print(f"      Test:  {test_count} ({test_count/num_imagenes*100:.1f}%)")
    print(f"   Total cartas: {total_cards}")
    
    # Generar archivo de relaciones con bounds REALES
    bounds_file = f"{target_dir}/vtes-dataset/bounds.json"
    with open(bounds_file, 'w', encoding='utf-8') as f:
        json.dump(all_bounds, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Archivo de relaciones generado: {bounds_file}")
    print(f"   Total bounds: {sum(len(b['bounds']) for b in all_bounds)} cartas")
    
    # Comprimir a ZIP
    print(f"\n📦 Comprimiendo a ZIP: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(f"{target_dir}/vtes-dataset"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = file
                zipf.write(file_path, arcname)
    
    # Verificar tamaño del ZIP
    if os.path.exists(zip_path):
        zip_size = os.path.getsize(zip_path)
        print(f"\n✅ Dataset completado:")
        print(f"   📄 Imágenes: {num_imagenes}")
        print(f"   📦 ZIP: {zip_path}")
        print(f"   💾 Tamaño: {zip_size / 1024 / 1024:.2f} MB")
        print(f"   📊 Bounds: {len(all_bounds)} imágenes anotadas")
        print(f"   📋 Distribución: train={train_count}, val={val_count}, test={test_count}")
    else:
        print(f"\n❌ Error: No se pudo crear el ZIP")
    
    # === Generar labels YOLO ===
    print(f"\n🏷️ Generando labels YOLO...")
    
    # Guardar bounds con attached
    bounds_file = f"{target_dir}/vtes-dataset/bounds.json"
    with open(bounds_file, 'w', encoding='utf-8') as f:
        json.dump(all_bounds, f, indent=2, ensure_ascii=False)
    
    print(f"   📄 bounds.json: {sum(len(b['bounds']) for b in all_bounds)} cartas")
    
    # Generar labels COCO
    for item in all_bounds:
        img_name = item['filename']
        bounds_list = item['bounds']
        dst_dir = f"{item['dir']}"
        
        # Crear archivo de labels
        label_path = f"{dst_dir}/{img_name}.txt"
        os.makedirs(dst_dir, exist_ok=True)
        
        # Escribir labels en formato YOLO
        with open(label_path, 'w', encoding='utf-8') as f_label:
            for bound in bounds_list:
                # Normalizar a imagen de 1080x1080
                x = bound['x'] / 1080.0
                y = bound['y'] / 1080.0
                w = bound['width'] / 1080.0
                h = bound['height'] / 1080.0
                
                # Formato COCO: x y width height
                f_label.write(f"{x:.4f} {y:.4f} {w:.4f} {h:.4f}\n")
    
    # Contar labels generados
    train_labels = len([f for f in os.listdir(f"{root_dir}/train") if f.endswith('.txt')])
    val_labels = len([f for f in os.listdir(f"{root_dir}/val") if f.endswith('.txt')])
    test_labels = len([f for f in os.listdir(f"{root_dir}/test") if f.endswith('.txt')])
    
    print(f"   ✅ Labels generados:")
    print(f"      Train: {train_labels} imágenes")
    print(f"      Val:   {val_labels} imágenes")
    print(f"      Test:  {test_labels} imágenes")
    print(f"   📋 Total: {train_labels + val_labels + test_labels} labels")
    
    # Guardar bounds.json
    print(f"\n📄 bounds.json guardado en: {bounds_file}")
    
    # Comprimir a ZIP
    print(f"\n📦 Comprimiendo a ZIP: {zip_path}")
