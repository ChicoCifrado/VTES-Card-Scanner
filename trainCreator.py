import os
import random
import math
import shutil
import yaml
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
import zipfile

def create_directory_structure():
    """Crea la estructura de directorios necesaria para el dataset YOLO."""
    # Crea los directorios principales
    base_dirs = ['dataset', 'dataset/images', 'dataset/labels', 
                'dataset/images/train', 'dataset/images/val', 'dataset/images/test',
                'dataset/labels/train', 'dataset/labels/val', 'dataset/labels/test']
    
    for dir_path in base_dirs:
        os.makedirs(dir_path, exist_ok=True)
        
    print("✓ Estructura de directorios creada con éxito")

def get_card_files(cards_dir):
    """Obtiene la lista de archivos de cartas Pokémon."""
    return [os.path.join(cards_dir, f) for f in os.listdir(cards_dir) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

def get_background_files(backgrounds_dir):
    """Obtiene la lista de archivos de fondo."""
    return [os.path.join(backgrounds_dir, f) for f in os.listdir(backgrounds_dir) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

def calculate_iou(box1, box2):
    """
    Calcula el IoU (Intersection over Union) entre dos bounding box.
    box1, box2: cada box está representada por [x1, y1, x2, y2]
    """
    # Coordenadas de la intersección
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    # Área de la intersección
    intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
    
    # Área de cada box
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    # Unión
    union_area = box1_area + box2_area - intersection_area
    
    # Índice de intersección sobre unión (IoU)
    if union_area <= 0:
        return 0
    return intersection_area / union_area

def place_card_on_background(card_img, bg_img, existing_boxes=None, max_attempts=50, scale_factor=None):
    """
    Coloca una carta Pokémon sobre un fondo, usando un enfoque de grilla.
    """
    if existing_boxes is None:
        existing_boxes = []
    
    # Obtén dimensiones de las imágenes
    bg_width, bg_height = bg_img.size
    card_width, card_height = card_img.size
    
    # Usa el factor de escala proporcionado o genera uno por defecto
    if scale_factor is None:
        scale_factor = random.uniform(0.08, 0.15)
    
    new_card_width = int(bg_width * scale_factor)
    new_card_height = int(card_height * (new_card_width / card_width))
    
    # Guarda las dimensiones originales antes de la rotación
    original_width = new_card_width
    original_height = new_card_height
    
    card_img = card_img.resize((new_card_width, new_card_height), Image.LANCZOS)
    
    # Ángulo aleatorio más limitado para mantener un aspecto ordenado
    # Reduce el ángulo para cartas grandes
    if scale_factor > 0.3:
        angle_deg = random.uniform(-5, 5)  # Ángulo menor para cartas grandes
    else:
        angle_deg = random.uniform(-15, 15)
        
    card_img = card_img.rotate(angle_deg, expand=True, resample=Image.BICUBIC)
    
    # Obtén las nuevas dimensiones después de la rotación
    rotated_width, rotated_height = card_img.size
    
    # Define una grilla
    grid_cols = 5  # Número de columnas en la grilla
    grid_rows = 4  # Número de filas en la grilla
    cell_width = bg_width // grid_cols
    cell_height = bg_height // grid_rows
    
    # Prova posizioni nella griglia
    for _ in range(max_attempts):
        # Elige una celda de la grilla
        grid_x = random.randint(0, grid_cols - 1)
        grid_y = random.randint(0, grid_rows - 1)
        
        # Calcula la posición base en la celda con un poco de variación aleatoria
        base_x = grid_x * cell_width + random.randint(-10, 10)
        base_y = grid_y * cell_height + random.randint(-10, 10)
        
        # Calcula la posición efectiva, asegurándote de que esté dentro de la imagen
        paste_x = max(0, min(base_x, bg_width - rotated_width))
        paste_y = max(0, min(base_y, bg_height - rotated_height))
        
        # Calcula la bounding box en coordenadas absolutas (pixeles)
        x1 = paste_x
        y1 = paste_y
        x2 = paste_x + rotated_width
        y2 = paste_y + rotated_height
        
        # Comprueba si la bounding box es válida
        if x1 >= bg_width or y1 >= bg_height or x2 <= 0 or y2 <= 0:
            continue
        
        # Asegúrate de que la bounding box esté dentro de la imagen
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(bg_width, x2)
        y2 = min(bg_height, y2)
        
        # Comprueba si la bounding box es lo suficientemente grande
        if (x2 - x1) < 10 or (y2 - y1) < 10:
            continue
        
        # Crea bbox en formato pixel para verificar superposiciones
        pixel_bbox = [x1, y1, x2, y2]
        
        # Baja el umbral IoU para permitir cartas más cercanas
        overlap_detected = False
        for existing_box in existing_boxes:
            iou = calculate_iou(pixel_bbox, existing_box)
            if iou > 0.1:  # Umbral IoU reducido al 10%
                overlap_detected = True
                break
                
        if not overlap_detected:
            # Crea una copia del fondo para evitar modificar el original
            result_img = bg_img.copy()
            
            # Crea una máscara para la transparencia
            if card_img.mode == 'RGBA':
                mask = card_img.split()[3]
            else:
                mask = None
                
            # Pega la carta sobre el fondo
            result_img.paste(card_img, (paste_x, paste_y), mask)
            
            # Calcula los cuatro ángulos del rectángulo rotado
            # Para OBB, necesitamos las coordenadas de los 4 ángulos
            # Calcula el centro de la carta
            center_x = paste_x + rotated_width / 2
            center_y = paste_y + rotated_height / 2
            
            # Calcula los cuatro ángulos antes de la rotación (relativo al centro)
            # Usa las dimensiones originales de la carta, no aquellas después de la rotación
            half_width = original_width / 2
            half_height = original_height / 2
            corners = [
                [-half_width, -half_height],  # Top-left
                [half_width, -half_height],   # Top-right
                [half_width, half_height],    # Bottom-right
                [-half_width, half_height]    # Bottom-left
            ]
            
            # Convierte el ángulo a radianes (para el cálculo de la rotación)
            angle_rad = math.radians(-angle_deg)  # Negativo porque PIL rota en sentido antihorario
            
            # Aplica la rotación y traslada al centro
            rotated_corners = []
            for x, y in corners:
                # Aplica la rotación
                x_rot = x * math.cos(angle_rad) - y * math.sin(angle_rad)
                y_rot = x * math.sin(angle_rad) + y * math.cos(angle_rad)
                
                # Traslada al centro y normaliza para YOLO
                x_final = (center_x + x_rot) / bg_width
                y_final = (center_y + y_rot) / bg_height
                
                # Asegúrate de que los valores estén en el rango [0, 1]
                x_final = max(0, min(1, x_final))
                y_final = max(0, min(1, y_final))
                
                rotated_corners.append(x_final)
                rotated_corners.append(y_final)
            
            # Formato OBB YOLO: clase x1 y1 x2 y2 x3 y3 x4 y4
            yolo_bbox = [0] + rotated_corners
            
            # Para el control de superposiciones, usamos aún el rectángulo no rotado
            pixel_bbox = [x1, y1, x2, y2]
            
            return result_img, yolo_bbox, pixel_bbox
    
    # Si después de todos los intentos no fue posible evitar superposiciones
    # Devuelve la última posición generada
    result_img = bg_img.copy()
    
    if card_img.mode == 'RGBA':
        mask = card_img.split()[3]
    else:
        mask = None
        
    result_img.paste(card_img, (paste_x, paste_y), mask)
    
    # Asegúrate de que la bounding box esté dentro de la imagen
    x1 = max(0, paste_x)
    y1 = max(0, paste_y)
    x2 = min(bg_width, paste_x + rotated_width)
    y2 = min(bg_height, paste_y + rotated_height)
    
    # Calcula el centro de la carta
    center_x = paste_x + rotated_width / 2
    center_y = paste_y + rotated_height / 2
    
    # Calcula los cuatro ángulos antes de la rotación (relativo al centro)
    half_width = original_width / 2
    half_height = original_height / 2
    corners = [
        [-half_width, -half_height],  # Top-left
        [half_width, -half_height],   # Top-right
        [half_width, half_height],    # Bottom-right
        [-half_width, half_height]    # Bottom-left
    ]
    
    # Convierte el ángulo a radianes (para el cálculo de la rotación)
    angle_rad = math.radians(-angle_deg)  # Negativo porque PIL rota en sentido antihorario
    
    # Aplica la rotación y traslada al centro
    rotated_corners = []
    for x, y in corners:
        # Aplica la rotación
        x_rot = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        y_rot = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        
        # Traslada al centro y normaliza para YOLO
        x_final = (center_x + x_rot) / bg_width
        y_final = (center_y + y_rot) / bg_height
        
        # Asegúrate de que los valores estén en el rango [0, 1]
        x_final = max(0, min(1, x_final))
        y_final = max(0, min(1, y_final))
        
        rotated_corners.append(x_final)
        rotated_corners.append(y_final)
    
    # Formato OBB YOLO: clase x1 y1 x2 y2 x3 y3 x4 y4
    yolo_bbox = [0] + rotated_corners
    
    pixel_bbox = [x1, y1, x2, y2]
    
    return result_img, yolo_bbox, pixel_bbox

def generate_dataset_image(cards_files, backgrounds_files, idx, save_dir, labels_dir, cards_per_image=None):
    """
    Genera un'immagine di dataset con più carte Pokemon su uno sfondo.
    Salva l'immagine e il file di label corrispondente.
    """
    if cards_per_image is None:
        if random.random() < 0.5:
            grid_rows = random.randint(5, 15)
            grid_cols = random.randint(10, 20)
            cards_per_image = grid_rows * grid_cols
            use_grid = True
        else:
            # For random placement, sometimes generate very few cards
            cards_per_image = random.choices(
                [1, 2, 3, random.randint(8, 15)],
                weights=[0.1, 0.1, 0.1, 0.7]  # 30% chance for 1-3 cards, 70% for many cards
            )[0]
            use_grid = False
    else:
        use_grid = False
    
    # Seleziona uno sfondo casuale
    bg_file = random.choice(backgrounds_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    
    # Ridimensiona lo sfondo a una dimensione standard per YOLO
    target_size = (640, 640)  # tamaño estándar para dataset YOLO
    bg_img = bg_img.resize(target_size, Image.LANCZOS)
    
    # Lista para mantener un registro de las bounding box existentes
    existing_boxes = []
    
    # Lista para almacenar las coordenadas YOLO
    yolo_bboxes = []
    
    if use_grid:
        # Genera una grilla regular de cartas
        cell_width = bg_img.width // grid_cols
        cell_height = bg_img.height // grid_rows
        
        # Calcula el tamaño de las cartas (ligeramente más pequeña que la celda)
        card_scale = 0.99  # Deja un pequeño espacio entre las cartas
        card_width = int(cell_width * card_scale)
        card_height = int(cell_height * card_scale)
        
        for row in range(grid_rows):
            for col in range(grid_cols):
                # Selecciona una carta aleatoria
                card_file = random.choice(cards_files)
                card_img = Image.open(card_file).convert("RGBA")
                
                # Ridimensiona la carta per adattarla alla cella
                original_width, original_height = card_img.size
                aspect_ratio = original_height / original_width
                new_card_width = card_width
                new_card_height = int(new_card_width * aspect_ratio)
                
                # Si la altura es demasiado grande, redimensiona según la altura
                if new_card_height > card_height:
                    new_card_height = card_height
                    new_card_width = int(new_card_height / aspect_ratio)
                
                card_img = card_img.resize((new_card_width, new_card_height), Image.LANCZOS)
                
                # Calcula la posición central en la celda
                paste_x = col * cell_width + (cell_width - new_card_width) // 2
                paste_y = row * cell_height + (cell_height - new_card_height) // 2
                
                # Pega la carta sobre el fondo
                if card_img.mode == 'RGBA':
                    mask = card_img.split()[3]
                else:
                    mask = None
                
                bg_img.paste(card_img, (paste_x, paste_y), mask)
                
                # Calcola la bounding box in formato YOLO (normalizzata)
                x1 = paste_x / bg_img.width
                y1 = paste_y / bg_img.height
                x2 = (paste_x + new_card_width) / bg_img.width
                y2 = y1
                x3 = x2
                y3 = (paste_y + new_card_height) / bg_img.height
                x4 = x1
                y4 = y3
                
                # Formato OBB YOLO: clase x1 y1 x2 y2 x3 y3 x4 y4
                yolo_bbox = [0, x1, y1, x2, y2, x3, y3, x4, y4]
                yolo_bboxes.append(yolo_bbox)
                
                # Añade la bounding box a la lista de existentes (para compatibilidad)
                pixel_bbox = [paste_x, paste_y, paste_x + new_card_width, paste_y + new_card_height]
                existing_boxes.append(pixel_bbox)
    else:
        # Usa el posicionamiento aleatorio original
        for _ in range(cards_per_image):
            # Selecciona una carta aleatoria
            card_file = random.choice(cards_files)
            card_img = Image.open(card_file).convert("RGBA")

            # Determina el factor de escala basado en el número de cartas
            if cards_per_image == 1:
                scale_factor = random.uniform(0.7, 0.8)  # Cartas muy grandes (70-80% de la imagen)
            elif cards_per_image == 2:
                scale_factor = random.uniform(0.35, 0.45)  # Cartas grandes (35-45% de la imagen)
            elif cards_per_image == 3:
                scale_factor = random.uniform(0.25, 0.35)  # Cartas medianas (25-35% de la imagen)
            else:
                scale_factor = random.uniform(0.08, 0.15)  # Cartas pequeñas (8-15% de la imagen)
            
            # Posiciona la carta sobre el fondo con el factor de escala especificado
            result, yolo_bbox, bbox = place_card_on_background(
                card_img, bg_img, existing_boxes, scale_factor=scale_factor
            )
            bg_img = result
            
            # Añade la bounding box a la lista de existentes
            existing_boxes.append(bbox)
            
            # Almacena las coordenadas YOLO
            yolo_bboxes.append(yolo_bbox)
    
    # Salva l'immagine
    img_filename = f"image_{idx:06d}.jpg"
    img_path = os.path.join(save_dir, img_filename)
    bg_img = bg_img.convert("RGB")  # Converti in RGB per salvare come JPG
    bg_img.save(img_path, quality=95)
    
    # Salva il file di label YOLO OBB
    label_filename = f"image_{idx:06d}.txt"
    label_path = os.path.join(labels_dir, label_filename)
    
    with open(label_path, "w") as f:
        for bbox in yolo_bboxes:
            # Formato YOLO OBB: clase x1 y1 x2 y2 x3 y3 x4 y4
            formatted_bbox = [
                int(bbox[0]),  # classe (intero)
            ]
            # Aggiungi le 8 coordinate (4 punti) arrotondate a 6 decimali
            for i in range(1, 9):
                formatted_bbox.append(round(float(bbox[i]), 6))
                
            line = " ".join(map(str, formatted_bbox))
            f.write(line + "\n")
            
    return img_path, label_path

def create_yaml_file():
    """Crea el archivo YAML para el entrenamiento de YOLOv8."""
    data = {
        'train': './train/images',  # Ruta relativa para Ultralytics HUB
        'val': './val/images',
        'test': './test/images',
        'nc': 1,  # Número de clases
        'names': ['pokemon_card']  # Nombre de la clase
    }
    
    with open('dataset/data.yaml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print("✓ File YAML creato con successo")

def split_dataset(total_images=10000, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """
    Calcola la suddivisione del dataset in train, validation e test.
    Restituisce il numero di immagini per ogni split.
    """
    train_images = int(total_images * train_ratio)
    val_images = int(total_images * val_ratio)
    test_images = total_images - train_images - val_images
    
    return {
        'train': train_images,
        'val': val_images,
        'test': test_images
    }

def create_zip_file():
    """Crea un archivo ZIP del dataset."""
    zip_filename = 'pokemon_cards_dataset.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Crea una estructura como lo requiere Ultralytics HUB
        for split in ['train', 'val', 'test']:
            # Añade imágenes
            imgs_dir = f'dataset/images/{split}'
            for img_file in os.listdir(imgs_dir):
                img_path = os.path.join(imgs_dir, img_file)
                # Ruta en el archivo ZIP: train/images/file.jpg
                zipf.write(img_path, f'{split}/images/{img_file}')
            
            # Añade labels
            labels_dir = f'dataset/labels/{split}'
            for label_file in os.listdir(labels_dir):
                label_path = os.path.join(labels_dir, label_file)
                # Percorso nel file ZIP: train/labels/file.txt
                zipf.write(label_path, f'{split}/labels/{label_file}')
        
        # Aggiungi il file YAML
        zipf.write('dataset/data.yaml', 'data.yaml')
    
    print(f"✓ File ZIP '{zip_filename}' creato con successo")
    return zip_filename

def verify_labels(labels_dir):
    """Verifica que los archivos de label estén correctamente formateados para OBB."""
    invalid_files = []
    
    for label_file in os.listdir(labels_dir):
        label_path = os.path.join(labels_dir, label_file)
        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 9:  # Formato OBB: clase + 8 coordenadas
                    invalid_files.append(label_file)
                    break
                try:
                    # Comprueba que los valores sean números y estén en el rango correcto
                    class_id = int(parts[0])
                    
                    # Verifica che tutte le coordinate siano nel range [0,1]
                    for i in range(1, 9):
                        coord = float(parts[i])
                        if coord < 0 or coord > 1:
                            invalid_files.append(label_file)
                            break
                            
                except ValueError:
                    invalid_files.append(label_file)
                    break
    
    if invalid_files:
        print(f"ATTENZIONE: Trovati {len(invalid_files)} file di label non validi")
        return False
    else:
        print("✓ Tutti i file di label sono formattati correttamente per OBB")
        return True

def main():
    """Función principal para generar el dataset."""
    print("Generazione dataset YOLO per rilevamento carte Pokemon")
    
    # Define rutas
    cards_dir = 'cartas_vtes'
    backgrounds_dir = 'fondos_vtes'
    
    # Verifica esistenza cartelle
    if not os.path.exists(cards_dir):
        raise FileNotFoundError(f"La cartella {cards_dir} non esiste")
    if not os.path.exists(backgrounds_dir):
        raise FileNotFoundError(f"La cartella {backgrounds_dir} non esiste")
    
    # Crea estructura de directorios
    create_directory_structure()
    
    # Obtén archivos
    cards_files = get_card_files(cards_dir)
    backgrounds_files = get_background_files(backgrounds_dir)
    
    if not cards_files:
        raise ValueError(f"Nessuna immagine trovata nella cartella {cards_dir}")
    if not backgrounds_files:
        raise ValueError(f"Nessuna immagine trovata nella cartella {backgrounds_dir}")
    
    # Calcula la división del dataset
    total_images = 10000  # Número total de imágenes solicitado
    split_counts = split_dataset(total_images)
    
    print(f"Generazione di {total_images} immagini:")
    print(f" - Train: {split_counts['train']} immagini")
    print(f" - Validation: {split_counts['val']} immagini")
    print(f" - Test: {split_counts['test']} immagini")
    
    # Genera el dataset
    current_idx = 0
    
    # Genera imágenes de train
    print("\nGenerazione immagini di train...")
    for i in tqdm(range(split_counts['train'])):
        generate_dataset_image(
            cards_files, 
            backgrounds_files, 
            current_idx,
            'dataset/images/train',
            'dataset/labels/train'
        )
        current_idx += 1
    
    # Genera imágenes de validación
    print("\nGenerazione immagini di validation...")
    for i in tqdm(range(split_counts['val'])):
        generate_dataset_image(
            cards_files, 
            backgrounds_files, 
            current_idx,
            'dataset/images/val',
            'dataset/labels/val'
        )
        current_idx += 1
    
    # Genera imágenes de test
    print("\nGenerazione immagini di test...")
    for i in tqdm(range(split_counts['test'])):
        generate_dataset_image(
            cards_files, 
            backgrounds_files, 
            current_idx,
            'dataset/images/test',
            'dataset/labels/test'
        )
        current_idx += 1
    
    # Verifica los archivos de label
    print("\nVerifica dei file di label...")
    verify_labels('dataset/labels/train')
    
    # Crea file YAML
    create_yaml_file()
    
    # Crea file ZIP
    zip_filename = create_zip_file()
    
    print("\nGenerazione dataset completata!")
    print(f"Il dataset è stato salvato nella cartella 'dataset' e compresso in '{zip_filename}'")
    print("\nRiepilogo:")
    print("- Modello consigliato: YOLOv8n (Nano) per esecuzione ottimizzata su browser")
    print("- Per l'addestramento: yolo train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640")
    print("- Per la conversione in formato web: yolo export model=runs/train/best.pt format=tfjs")
    
    return True

if __name__ == "__main__":
    main()