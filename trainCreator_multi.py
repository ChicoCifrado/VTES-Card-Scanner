#!/usr/bin/env python3
"""
Generador de dataset VTES para OBS plugin (con 12 hilos).
Crea imágenes con 1-100 cartas, fondo aleatorio y rotación aleatoria (-180° a +180°).
Genera 10,000 imágenes comprimidas en vtes-dataset.zip.
"""
import os
import random
import zipfile
import shutil
import multiprocessing
from PIL import Image

NUM_WORKERS = 12  # 12 hilos
NUM_IMAGES_PER_WORKER = 10000 // NUM_WORKERS  # Imágenes por hilo

def generate_and_save_image(cards_files, backgrounds_files, output_dir, image_index, num_images_total):
    """
    Función para cada hilo: genera imágenes y las guarda.
    Cada imagen tiene 1-100 cartas (como en trainCreator_mini.py).
    """
    # Selecciona un fondo aleatorio
    bg_file = random.choice(backgrounds_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    
    # Asegurarse de que el fondo tenga 1080x1080
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Generar entre 1 y 100 cartas (como en trainCreator_mini.py)
    num_cards = random.randint(1, 100)
    
    for _ in range(num_cards):
        # Selecciona una carta aleatoria
        card_file = random.choice(cards_files)
        card_img = Image.open(card_file).convert("RGBA")
        
        # Determina el factor de escala
        scale_factor = random.uniform(0.02, 0.08)
        new_width = int(1080 * scale_factor)
        new_height = int(card_img.height * (new_width / card_img.width))
        
        # Redimensiona la carta
        card_img = card_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Rotación aleatoria
        rotation_angle = random.uniform(-180, 180)
        card_img = card_img.rotate(rotation_angle, expand=True, resample=Image.BICUBIC)

        # Posición aleatoria
        paste_x = random.randint(0, 1080 - card_img.width)
        paste_y = random.randint(0, 1080 - card_img.height)
        
        # Paste
        result_img = bg_img.copy()
        if card_img.mode == 'RGBA':
            mask = card_img.split()[3]
        else:
            mask = None
        result_img.paste(card_img, (paste_x, paste_y), mask)
        
        # Convertir a RGB y guardar
        result_img_rgb = result_img.convert("RGB")
        output_path = os.path.join(output_dir, f"image_{image_index:06d}.jpg")
        result_img_rgb.save(output_path, quality=100)
        
        # Incrementar índice
        image_index += 1
        
        # Si hemos generado todas las imágenes
        if image_index >= num_images_total:
            break
    
    return image_index

def main():
    """Función principal para generar múltiples imágenes del dataset VTES."""
    cards_dir = 'cartas_vtes'
    backgrounds_dir = 'fondos_vtes'
    
    # Usar rutas absolutas
    base_path = os.path.dirname(os.path.abspath(__file__))
    cards_dir = os.path.join(base_path, cards_dir)
    backgrounds_dir = os.path.join(base_path, backgrounds_dir)
    
    if not os.path.exists(cards_dir):
        raise FileNotFoundError(f"La carpeta {cards_dir} no existe")
    if not os.path.exists(backgrounds_dir):
        raise FileNotFoundError(f"La carpeta {backgrounds_dir} no existe")
    
    # Cambiar al directorio de fondos para buscar los archivos
    old_cwd = os.getcwd()
    os.chdir(backgrounds_dir)
    
    try:
        cards_files = [os.path.join(cards_dir, f) for f in os.listdir(cards_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        backgrounds_files = [os.path.join(backgrounds_dir, f) for f in os.listdir(backgrounds_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    finally:
        os.chdir(old_cwd)
    
    if not cards_files:
        raise ValueError(f"No se encontraron imágenes en la carpeta {cards_dir}")
    if not backgrounds_files:
        raise ValueError(f"No se encontraron imágenes en la carpeta {backgrounds_dir}")
    
    num_images = 10000
    output_dir = 'vtes-dataset'
    os.makedirs(output_dir, exist_ok=True)
    
    # Ruta de salida del ZIP
    target_dir = '/mnt/e/VTES'
    if not os.path.exists(target_dir):
        print(f'❌ Directorio de salida no existe: {target_dir}')
        print(f'Por favor crea el directorio {target_dir} o usa la ruta actual')
        return
    
    print(f"Iniciando generación con {NUM_WORKERS} hilos...")
    print(f"   Total imágenes: {num_images}")
    print(f"   Imágenes por hilo: {NUM_IMAGES_PER_WORKER}")
    
    # Calcular índices de inicio para cada hilo
    indices = []
    for i in range(NUM_WORKERS):
        start_idx = i * NUM_IMAGES_PER_WORKER
        indices.append(start_idx)
    
    # Crear procesos
    processes = []
    for i in range(NUM_WORKERS):
        p = multiprocessing.Process(
            target=generate_and_save_image,
            args=(cards_files, backgrounds_files, output_dir, indices[i], num_images)
        )
        p.start()
        processes.append(p)
    
    # Esperar a que terminen todos los hilos
    print("\nProcesos en marcha...")
    for i, p in enumerate(processes):
        p.join()
    
    # Comprimir a ZIP
    zip_path = os.path.join(target_dir, 'vtes-dataset.zip')
    print(f'\nComprimiendo a ZIP: {zip_path}')
    
    # Comprimir todo el dataset
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for j in range(num_images):
            file_path = os.path.join(output_dir, f"image_{j:06d}.jpg")
            if os.path.exists(file_path):
                zipf.write(file_path, f"image_{j:06d}.jpg")
    
    # Limpiar carpeta temporal
    shutil.rmtree(output_dir)
    
    # Calcular tamaño del ZIP
    zip_size = os.path.getsize(zip_path)
    print(f"\n✅ Dataset completado:")
    print(f"   📄 Imágenes: {num_images}")
    print(f"   📦 ZIP: {zip_path}")
    print(f"   💾 Tamaño: {zip_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()