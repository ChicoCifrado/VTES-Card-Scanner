#!/usr/bin/env python3
"""
🦇 VTES Complete - Script Unificado CORREGIDO v2.3
Genera dataset + augmentations + labels YOLO + Perceptual Hashing

Unifica:
- vtesCreator.py (generación base)
- vtes_augmentation.py (efectos de funda, contadores, iluminación)
- vtes_perceptual_hash.py (matching)

Usage:
  python vtes_complete.py --num 1000 --with_aug --with_hash --outline --intensity 0.5

Data Augmentation:
  --with_aug          Activar augmentations (funda, contadores, iluminación, flip)
  --augmentations none,gaussian,counter,brightness,flip  (opciones para elegir)
  --intensity         Intensidad de augmentations (0.0 a 1.0 en saltos de 0.1)

Output:
  - vtes-dataset/test/, train/, val/ (imágenes + labels)
  - vtes-dataset/test/*_augmented.jpg (imagen con augmentations aplicadas)
  - vtes-dataset/augmented/ (augmentations individuales por tipo)
  - vtes-dataset/perceptual_hashes.json (matching)
"""
import os
import sys
import random
import json
import math
import argparse
import hashlib
from PIL import Image, ImageDraw, ImageFilter

root_dir = "/mnt/e/VTES/VTES-Card-Scanner"
cartas_dir = f"{root_dir}/cartas_vtes"
fondos_dir = f"{root_dir}/fondos_vtes"
dataset_dir = f"{root_dir}/vtes-dataset"

# === CLASE CardPlacer (de vtesCreator.py) ===
class CardPlacer:
    def __init__(self):
        self.bounds_log = []
    
    def check_collisions(self, bounds_list):
        if len(bounds_list) < 2:
            return []
        
        attached_pairs = []
        
        for i in range(len(bounds_list)):
            for j in range(i + 1, len(bounds_list)):
                b1 = bounds_list[i]
                b2 = bounds_list[j]
                
                area1 = b1['width'] * b1['height']
                area2 = b2['width'] * b2['height']
                
                x1_min = b1['x']
                x1_max = b1['x'] + b1['width']
                y1_min = b1['y']
                y1_max = b1['y'] + b1['height']
                
                x2_min = b2['x']
                x2_max = b2['x'] + b2['width']
                y2_min = b2['y']
                y2_max = b2['y'] + b2['height']
                
                inter_x_min = max(x1_min, x2_min)
                inter_x_max = min(x1_max, x2_max)
                inter_y_min = max(y1_min, y2_min)
                inter_y_max = min(y1_max, y2_max)
                
                if inter_x_max > inter_x_min and inter_y_max > inter_y_min:
                    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
                    min_area = min(area1, area2)
                    overlap_percent = (inter_area / min_area) * 100 if min_area > 0 else 0
                    
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
        if bg_img.size != (1080, 1080):
            bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
        
        if scale_factor is None:
            scale_factor = random.uniform(0.08, 0.15)
        
        card_original = Image.open(card_file)
        card_ratio = card_original.width / card_original.height
        
        new_size = int(1080 * scale_factor)
        new_width = int(new_size * card_ratio)
        new_height = new_size
        
        if new_width + new_height > 2160:
            new_width = int(1080 * scale_factor * card_ratio)
            new_height = int(1080 * scale_factor)
        
        card_img = Image.open(card_file).convert("RGBA")
        card_img = card_img.resize((new_width, new_height), Image.LANCZOS)
        
        rotation_angle = random.uniform(-180, 180)
        # Rotar sin expandir para evitar artefactos
        card_img = card_img.rotate(rotation_angle, expand=False, resample=Image.BICUBIC)
        
        # Actualizar dimensiones después de rotación
        actual_width = card_img.width
        actual_height = card_img.height
        
        paste_x = random.randint(0, 1080 - actual_width)
        paste_y = random.randint(0, 1080 - actual_height)
        
        card_name = os.path.basename(card_file)
        
        bounds = {
            "name": card_name,
            "x": paste_x,
            "y": paste_y,
            "width": actual_width,  # Usar dimensiones reales después de rotación
            "height": actual_height,
            "rotation": rotation_angle,
            "scale": scale_factor,
        }
        
        # Usar alpha channel original para pegar la carta
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
        return self.bounds_log
    
    def get_bounds_with_attached(self):
        attached_pairs = self.check_collisions(self.bounds_log)
        
        bounds_with_attached = []
        for bound in self.bounds_log:
            bound_copy = bound.copy()
            attached = []
            for pair in attached_pairs:
                if pair['name1'] == bound['name']:
                    attached.append({"name": pair['name2'], "overlap_percent": pair['overlap_percent']})
                elif pair['name2'] == bound['name']:
                    attached.append({"name": pair['name1'], "overlap_percent": pair['overlap_percent']})
                if attached:
                    bound_copy['attached'] = attached
            bounds_with_attached.append(bound_copy)
        
        return bounds_with_attached, attached_pairs


# === Función de Perceptual Hashing ===
def perceptual_hash(image_path, hash_size=8):
    try:
        img = Image.open(image_path)
        img = img.resize((hash_size, hash_size), Image.BICUBIC)
        img = img.convert('L')
        hash_bytes = bytearray(img.tobytes())
        hash_value = int.from_bytes(hash_bytes, byteorder='big')
        return f"ph{hash_value:016d}"
    except:
        return None


# === Función de Augmentation ===
def augment_only_card(card_img, aug_type, intensity=0.0):
    """Aplicar augmentation solo a la carta (no al fondo)"""
    try:
        # Eliminar alpha channel y trabajar solo con RGB
        if card_img.mode == 'RGBA':
            augmented_card = card_img.convert('RGB')
        else:
            augmented_card = card_img.copy()
        
        # Aplicar efectos individuales a la carta
        if aug_type in ['gaussian', 'all'] and intensity > 0:
            # Blur más sutil: base 0.3, escala hasta 1.5
            sigma = 0.3 + int(intensity * 1.2)
            if sigma > 0:
                augmented_card = augmented_card.filter(ImageFilter.GaussianBlur(radius=sigma))
            shift = int(intensity * 8)  # Shift reducido de 10 a 8
            if shift > 0:
                augmented_card = augmented_card.point(lambda x: min(255, max(0, x + random.randint(-shift, shift))))
        
        if aug_type in ['counter', 'all'] and intensity > 0:
            # Crear obstáculo aleatorio pequeño (cuadradito)
            alpha = int(intensity * 100)  # Opacidad reducida para evitar saturación
            if alpha > 0:
                # Obstáculo pequeño aleatorio en posición aleatoria
                obs_size = int(random.uniform(5, 15))  # Tamaño del obstáculo (5-15px, muy pequeño)
                obs_x = random.randint(obs_size, augmented_card.width - obs_size)
                obs_y = random.randint(obs_size, augmented_card.height - obs_size)
                
                # Crear obstáculo gris para simular menor brillo
                obs_color = (50, 50, 50, alpha)  # Gris oscuro, no verde
                obs_shape = Image.new('RGBA', (obs_size, obs_size), obs_color)
                augmented_card.paste(obs_shape, (obs_x, obs_y), obs_shape.split()[3] if obs_shape.mode == 'RGBA' else obs_shape)
        
        if aug_type in ['brightness', 'all'] and intensity > 0:
            # Brillo variable con tinte gris (no verde)
            brightness = 1.0 + (random.uniform(-0.2, 0.2) * intensity)  # Rango más estrecho
            if brightness != 1.0:
                augmented_card = augmented_card.point(lambda x: int(255 * pow(x / 255.0, 1.1 / brightness)))
        
        if aug_type == 'flip' and intensity >= 1.0:
            augmented_card = augmented_card.transpose(Image.FLIP_LEFT_RIGHT)
        
        return augmented_card
    except Exception as e:
        print(f"   ⚠️ Aug error {aug_type}: {e}")
        return card_img


def apply_single_augmentation(img, aug_type, intensity=0.0):
    """Aplicar una única augmentation con intensidad controlada (0.0 a 1.0) - VIEJO, ya no se usa"""
    try:
        if aug_type == 'gaussian':
            sigma = 0.5 + int(intensity * 2.5)
            if sigma > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
            shift = int(intensity * 10)
            if shift > 0:
                img = img.point(lambda x: min(255, max(0, x + random.randint(-shift, shift))))
        elif aug_type == 'counter':
            alpha = int(intensity * 200)
            if alpha > 0:
                img = img.copy()
                counter = Image.new('RGBA', img.size, (0, 100, 0, alpha))
                img.paste(counter, (0, 0), counter.split()[3] if counter.mode == 'RGBA' else counter)
        elif aug_type == 'brightness':
            brightness = 1.0 + (random.uniform(-0.4, 0.4) * intensity)
            if brightness != 1.0:
                img = img.convert('RGB')
                img = img.point(lambda x: int(x * brightness))
        elif aug_type == 'flip':
            if intensity >= 1.0:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return img
    except Exception as e:
        print(f"   ⚠️ Aug error {aug_type}: {e}")
        return img


def apply_all_augmentations_to_image(img, bounds_list, intensity=0.0):
    """Aplicar augmentations solo a las cartas, no al fondo"""
    try:
        if not bounds_list:
            return img
        
        # Convertir imagen base a RGB (eliminar alpha)
        if img.mode != 'RGB':
            img_rgb = img.convert('RGB')
        else:
            img_rgb = img.copy()
        
        # Aplicar augmentations a cada carta individualmente
        for bound in bounds_list:
            x = bound['x']
            y = bound['y']
            w = bound['width']
            h = bound['height']
            angle = bound['rotation']
            
            # Extraer carta del fondo (ya sin alpha)
            card = img_rgb.crop((x, y, x + w, y + h))
            
            # Rotar carta para compensar (invertir rotación)
            # Solo rotar si es significativa (> 5 grados)
            if abs(angle) > 5.0:
                card = card.rotate(-angle, expand=False, resample=Image.BICUBIC)
            
            # Aplicar augmentations a la carta
            card_aug = augment_only_card(card, 'all', intensity)
            
            # Rotar de nuevo a la posición original
            if abs(angle) > 5.0:
                card_aug = card_aug.rotate(angle, expand=False, resample=Image.BICUBIC)
            
            # Crear mask sólido para pegar sin artefactos de alpha
            mask_solid = Image.new('L', (card_aug.width, card_aug.height), 255)
            img_rgb.paste(card_aug, (x, y), mask_solid)
        
        return img_rgb
    except Exception as e:
        print(f"   ⚠️ Error aplicando augmentations a imagen: {e}")
        return img


def apply_all_augmentations(img, intensity=0.0):
    """Aplicar todas las augmentations acumulativamente con intensidad global (0.0 a 1.0) - VIEJO"""
    try:
        result = img
        
        # Funda (gaussian) - más visible
        sigma = 0.5 + int(intensity * 2.5)
        if sigma > 0:
            result = result.filter(Image.GaussianBlur(radius=sigma))
        shift = int(intensity * 10)
        if shift > 0:
            result = result.point(lambda x: min(255, max(0, x + random.randint(-shift, shift))), Image.LUT)
        
        # Contador verde - más visible
        alpha = int(intensity * 200)
        if alpha > 0:
            result = result.copy()
            counter = Image.new('RGBA', result.size, (0, 100, 0, alpha))
            result.paste(counter, (0, 0), None)
        
        # Iluminación variable - más variable
        brightness = 1.0 + (random.uniform(-0.4, 0.4) * intensity)
        if brightness != 1.0:
            result = result.convert('RGB')
            result = result.point(lambda x: int(x * brightness))
        
        # Flip horizontal
        if intensity >= 1.0:
            result = result.transpose(Image.FLIP_LEFT_RIGHT)
        
        return result
    except Exception as e:
        print(f"   ⚠️ Error aplicando all augmentations: {e}")
        return img


# === GENERACIÓN ===
def generate_image(args, idx, cartas_files, fondos_files, use_augmentations, use_outline):
    if not fondos_files:
        print(f"   ⚠️ No hay fondos disponibles")
        return None
    
    bg_file = random.choice(fondos_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    placer = CardPlacer()
    
    for _ in range(random.randint(1, 4)):
        if cartas_files:
            card_file = random.choice(cartas_files)
            scale_factor = random.uniform(0.08, 0.15)
            bg_img = placer.scale_and_place_card(card_file, bg_img, scale_factor)
        else:
            break
    
    bounds = placer.get_bounds()
    bounds_with_attached, attached_pairs = placer.get_bounds_with_attached()
    
    # Asignar carpeta
    if idx < 10:
        dst_dir = f"{dataset_dir}/test"
    elif idx < 200:
        dst_dir = f"{dataset_dir}/val"
    else:
        dst_dir = f"{dataset_dir}/train"
    
    dst_path = os.path.join(dst_dir, f"image_{idx:06d}.jpg")
    os.makedirs(dst_dir, exist_ok=True)
    
    if bg_img.mode == 'RGBA':
        bg = Image.new('RGB', bg_img.size)
        bg.paste(bg_img, mask=bg_img.split()[3])
        img = bg
    else:
        img = bg_img
    
    # Guardar imagen base
    img.save(dst_path, quality=100)
    
    # Dibujar líneas de contorno (si --outline)
    if use_outline and bounds_with_attached:
        img_outline = img.copy().convert('RGB')
        draw = ImageDraw.Draw(img_outline)
        
        for bound in bounds_with_attached:
            # Calcular tamaño del borde (5% del ancho)
            outline_width = max(1, int(bound['width'] * 0.05))
            
            # Coordenadas del bounding box
            x1 = bound['x']
            y1 = bound['y']
            x2 = bound['x'] + bound['width']
            y2 = bound['y'] + bound['height']
            
            # Dibujar rectángulo rojo DELIMITANDO el área de la carta
            draw.rectangle([x1, y1, x2, y2], width=outline_width, outline='red', fill=None)
            
            # Dibujar texto con coordenadas OBB (x1 y1 x2 y2)
            w = bound['width']
            h = bound['height']
            angle_rad = math.radians(bound['rotation'])
            
            draw.text((x1 + 2, y1 + 2), f"x1:{x1:.0f}", fill='yellow')
            draw.text((x1 + 2, y1 + 15), f"y1:{y1:.0f}", fill='yellow')
            draw.text((x2 - 5, y2 - 5), f"x2:{x2:.0f}", fill='yellow')
            draw.text((x2 - 5, y2 - 18), f"y2:{y2:.0f}", fill='yellow')
            draw.text((x2 + 2, y1 + 2), f"w:{w:.0f}", fill='yellow')
            draw.text((x2 + 2, y1 + 15), f"h:{h:.0f}", fill='yellow')
            draw.text((x2 + 2, y1 + 30), f"ang:{angle_rad:.1f}°", fill='yellow')
        
        # Sobrescribir la imagen con los outlines
        img = img_outline
        img.save(dst_path, quality=100)
    
    # Guardar bounds
    bounds_dict = {
        "filename": os.path.basename(dst_path),
        "path": dst_path,
        "dir": os.path.basename(dst_dir),
        "num_cards": len(bounds_with_attached),
        "bounds": bounds_with_attached,
        "attached_pairs": attached_pairs
    }
    
    # Generar labels YOLO (formato OBB Ultralytics: class_index x1 y1 x2 y2 x3 y3 x4 y4)
    label_path = f"{dst_dir}/{os.path.basename(dst_path)}.txt"
    with open(label_path, 'w', encoding='utf-8') as f_label:
        for bound in bounds_with_attached:
            # Calcular las 4 esquinas del rectángulo rotado
            cx = bound['x'] + bound['width'] / 2.0
            cy = bound['y'] + bound['height'] / 2.0
            w = bound['width']
            h = bound['height']
            angle_rad = math.radians(bound['rotation'])
            
            # Calcular radio (diagonal / 2)
            r = math.hypot(w / 2.0, h / 2.0)
            
            # Calcular las 4 esquinas usando trigonometría
            corners_rel = [
                (-w/2, -h/2),
                (w/2, -h/2),
                (w/2, h/2),
                (-w/2, h/2)
            ]
            
            # Rotar y trasladar cada esquina
            corners = []
            for rx, ry in corners_rel:
                x_rotated = cx + rx * math.cos(angle_rad) - ry * math.sin(angle_rad)
                y_rotated = cy + rx * math.sin(angle_rad) + ry * math.cos(angle_rad)
                corners.append((x_rotated, y_rotated))
            
            # Normalizar coordenadas a imagen de 1080x1080
            x1, y1 = corners[0]
            x2, y2 = corners[1]
            x3, y3 = corners[2]
            x4, y4 = corners[3]
            
            # Normalizar
            x1_n = x1 / 1080.0
            y1_n = y1 / 1080.0
            x2_n = x2 / 1080.0
            y2_n = y2 / 1080.0
            x3_n = x3 / 1080.0
            y3_n = y3 / 1080.0
            x4_n = x4 / 1080.0
            y4_n = y4 / 1080.0
            
            # Formato OBB Ultralytics: class_index x1 y1 x2 y2 x3 y3 x4 y4
            f_label.write(f"0 {x1_n:.4f} {y1_n:.4f} {x2_n:.4f} {y2_n:.4f} {x3_n:.4f} {y3_n:.4f} {x4_n:.4f} {y4_n:.4f}\n")
    
    # También guardar labels COCO para compatibilidad (4 parámetros)
    label_path_coco = label_path.replace('.txt', '_coco.txt')
    with open(label_path_coco, 'w', encoding='utf-8') as f_label_coco:
        for bound in bounds_with_attached:
            x = bound['x'] / 1080.0
            y = bound['y'] / 1080.0
            w = bound['width'] / 1080.0
            h = bound['height'] / 1080.0
            f_label_coco.write(f"{x:.4f} {y:.4f} {w:.4f} {h:.4f}\n")
    
    # Augmentations - aplicar solo si se activaron
    augmented_dir = f"{dataset_dir}/augmented"
    os.makedirs(augmented_dir, exist_ok=True)
    
    if use_augmentations and bounds_with_attached:
        # Determinar qué augmentations aplicar
        selected_augments = ['all'] if args.augmentations == 'all' else [args.augmentations]
        intensity = args.intensity if hasattr(args, 'intensity') and args.intensity >= 0 else 0.0
        
        # Aplicar todas las augmentations a las cartas individuales
        img_augmented = apply_all_augmentations_to_image(img, bounds_with_attached, intensity)
        img_augmented_path = os.path.join(dst_dir, f"image_{idx:06d}_augmented.jpg")
        img_augmented.save(img_augmented_path, quality=90)
        print(f"   🎨 Augmentations aplicadas (intensidad={intensity:.1f}, {intensity*100:.0f}%) a: {os.path.basename(img_augmented_path)}")
        
        # Guardar augmentations individuales en directorio augmented/
        for aug_type in selected_augments:
            try:
                aug = img.copy()
                if aug_type == 'gaussian':
                    aug = apply_single_augmentation(aug, 'gaussian', intensity)
                elif aug_type == 'counter':
                    aug = apply_single_augmentation(aug, 'counter', intensity)
                elif aug_type == 'brightness':
                    aug = apply_single_augmentation(aug, 'brightness', intensity)
                elif aug_type == 'flip':
                    aug = apply_single_augmentation(aug, 'flip', intensity)
                
                aug_path = os.path.join(augmented_dir, f"aug_{idx}_{aug_type}.jpg")
                aug.save(aug_path, quality=90)
            except Exception as e:
                print(f"   ⚠️ Error guardando augmentation {aug_type}: {e}")
    
    return bounds_dict


def main():
    # Chequear si se ejecutó sin parámetros
    if len(sys.argv) >= 2 and sys.argv[1].startswith('--'):
        # Se proporcionaron parámetros
        parser = argparse.ArgumentParser(description="🦇 VTES Complete - Unificado")
        parser.add_argument("--num", type=int, choices=[10, 100, 1000, 10000], default=10, help="Imágenes a generar")
        parser.add_argument("--output", type=str, default=root_dir, help="Directorio base")
        parser.add_argument("--with_aug", action="store_true", help="Incluir augmentations (funda, contadores, iluminación, flip) [default: all]")
        parser.add_argument("--augmentations", type=str, choices=["gaussian", "counter", "brightness", "flip", "all"], default="all", help="Augmentaciones específicas: gaussian (funda), counter (contadores), brightness (iluminación), flip (horizontal), all (todas) [default: all]")
        parser.add_argument("--with_hash", action="store_true", help="Incluir Perceptual Hashing")
        parser.add_argument("--outline", action="store_true", help="Dibujar líneas rojas alrededor de cartas para visualizar el bounding box")
        parser.add_argument("--intensity", type=float, default=0.0, help="Intensidad de augmentations (0.0 a 1.0 en saltos de 0.1, 0.0=0%, 1.0=100%, default: 0.0)")
        
        args = parser.parse_args()
    else:
        # Mostrar ayuda
        print("🦇 VTES Complete v2.4")
        print("="*50)
        print()
        print("📜 Uso:")
        print("   python3 vtes_complete.py --num 1000 --with_aug --with_hash --outline --intensity 0.5")
        print()
        print("📋 Parámetros disponibles:")
        print("   --num         Número de imágenes: 10, 100, 1000, 10000 (default: 10)")
        print("   --output      Directorio base (default: /mnt/e/VTES/VTES-Card-Scanner)")
        print("   --with_aug    Activar augmentations: gaussian (funda), counter (obstáculos), brightness (brillo), flip (horizontal)")
        print("   --augmentations    Tipo de augmentation: gaussian|counter|brightness|flip|all (default: all)")
        print("   --with_hash   Activar Perceptual Hashing para matching")
        print("   --outline     Dibujar bounding boxes rojos con coordenadas")
        print("   --intensity   Intensidad: 0.0 a 1.0 (default: 0.0, desactivado)")
        print()
        print("📊 Ejemplos:")
        print("   # Generar 10 imágenes con augmentations al 50%")
        print("   python3 vtes_complete.py --num 10 --with_aug --outline --intensity 0.5")
        print()
        print("   # Solo blur (funda) al 30%")
        print("   python3 vtes_complete.py --num 100 --augmentations gaussian --intensity 0.3")
        print()
        print("   # Solo obstáculos grises al 70%")
        print("   python3 vtes_complete.py --num 100 --augmentations counter --intensity 0.7")
        print()
        print("   # Sin augmentations")
        print("   python3 vtes_complete.py --num 100")
        print()
        print("   # Generar dataset completo con matching")
        print("   python3 vtes_complete.py --num 1000 --with_aug --with_hash --intensity 0.5")
        print()
        return
    
    # Validar augmentations
    if args.with_aug and args.augmentations != "all":
        print(f"📊 Augmentations seleccionadas: {args.augmentations}")
        print(f"   Opciones: gaussian, counter, brightness, flip, all")
        print()
    elif not args.with_aug:
        print(f"⚠️  Augmentations desactivadas.")
        print(f"   Usa --with_aug para activarlas.")
        print(f"   Opciones: --augmentations gaussian|counter|brightness|flip|all")
        print()
    
    print(f"🦇 VTES Complete v2.3")
    print(f"   Imágenes: {args.num}")
    print(f"   Augmentations: {'Sí' if args.with_aug else 'No'}")
    print(f"   Perceptual Hash: {'Sí' if args.with_hash else 'No'}")
    print(f"   Contornos rojos: {'Sí' if args.outline else 'No'}")
    print(f"   Intensidad augmentations: {args.intensity:.1f} ({int(args.intensity*100):.0f}%)")
    print()
    
    # Verificar directorios
    if not os.path.exists(cartas_dir):
        print(f"❌ Error: {cartas_dir} no existe")
        sys.exit(1)
    if not os.path.exists(fondos_dir):
        print(f"❌ Error: {fondos_dir} no existe")
        sys.exit(1)
    
    # Obtener archivos
    cartas_files = [
        os.path.join(cartas_dir, f)
        for f in os.listdir(cartas_dir)
        if f.endswith(('.png', '.jpg', '.jpeg', '.webp', '.web'))
    ]
    fondos_files = [
        os.path.join(fondos_dir, f)
        for f in os.listdir(fondos_dir)
        if f.endswith(('.png', '.jpg', '.jpeg', '.webp', '.web'))
    ]
    
    if not cartas_files:
        print(f"❌ Error: No hay cartas en {cartas_dir}")
        sys.exit(1)
    if not fondos_files:
        print(f"❌ Error: No hay fondos en {fondos_dir}")
        sys.exit(1)
    
    print(f"📍 Archivos:")
    print(f"   Cartas: {len(cartas_files)}")
    print(f"   Fondos: {len(fondos_files)}")
    print()
    
    # Crear estructura
    dataset_dir = f"{args.output}/vtes-dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    for subdir in ['test', 'val', 'train', 'augmented']:
        os.makedirs(f"{dataset_dir}/{subdir}", exist_ok=True)
    
    # Generar dataset
    print(f"🚀 Generando dataset...")
    all_bounds = []
    
    for idx in range(args.num):
        bounds_dict = generate_image(args, idx, cartas_files, fondos_files, args.with_aug, use_outline=args.outline)
        all_bounds.append(bounds_dict)
        
        if args.num <= 100:
            print(f"   ✓ {idx:04d}: {bounds_dict['dir']}/{bounds_dict['filename']} ({len(bounds_dict['bounds'])} cartas)")
        else:
            print(f"   ✓ {idx:06d}")
    
    # Resumen
    train_count = len([b for b in all_bounds if b['dir'] == 'train'])
    val_count = len([b for b in all_bounds if b['dir'] == 'val'])
    test_count = len([b for b in all_bounds if b['dir'] == 'test'])
    total_cards = sum(b['num_cards'] for b in all_bounds)
    
    print(f"\n✅ Dataset generado!")
    print(f"   Imágenes: {args.num}")
    print(f"   Distribución:")
    print(f"      Train: {train_count} ({train_count/args.num*100:.1f}%)")
    print(f"      Val:   {val_count} ({val_count/args.num*100:.1f}%)")
    print(f"      Test:  {test_count} ({test_count/args.num*100:.1f}%)")
    print(f"   Total cartas: {total_cards}")
    
    # Guardar bounds.json
    bounds_file = f"{dataset_dir}/bounds.json"
    with open(bounds_file, 'w', encoding='utf-8') as f:
        json.dump(all_bounds, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 bounds.json guardado en: {bounds_file}")
    
    # Perceptual Hashing
    if args.with_hash:
        print(f"\n🔍 Ejecutando Perceptual Hashing...")
        
        # Obtener todos los archivos de imágenes en los directorios
        for subdir in ['test', 'train', 'val']:
            subdir_path = f"{dataset_dir}/{subdir}"
            if os.path.exists(subdir_path):
                image_files = [os.path.join(subdir_path, f) for f in os.listdir(subdir_path) if f.endswith('.jpg')]
                print(f"   Procesando {subdir}: {len(image_files)} imágenes")
                
                hashes = []
                for img_path in image_files:
                    hash_value = perceptual_hash(img_path)
                    if hash_value:
                        hashes.append({
                            "image": os.path.basename(img_path),
                            "hash": hash_value
                        })
                
                # Guardar en JSON
                hashes_file = f"{dataset_dir}/perceptual_hashes.json"
                with open(hashes_file, 'w', encoding='utf-8') as f:
                    json.dump(hashes, f, indent=2, ensure_ascii=False)
                
                print(f"   📊 Hashes guardados en: {hashes_file}")
    
    print("\n✅ ¡Completo!")
    print(f"   Dataset: {dataset_dir}")
    print(f"   bounds.json: {bounds_file}")
    if args.with_hash:
        print(f"   perceptual_hashes.json: {dataset_dir}/perceptual_hashes.json")


if __name__ == "__main__":
    main()