#!/usr/bin/env python3
"""
Generador de dataset VTES para OBS plugin (con 12 hilos en un solo proceso).
Crea imágenes con 1-100 cartas, fondo aleatorio y rotación aleatoria (-180° a +180°).
Genera 10,000 imágenes comprimidas en vtes-dataset.zip.

📍 Ubicación de las imágenes:
   - Temporales: /home/cifrado/.openclaw/workspace/projects/VTES-Card-Scanner/vtes-dataset/
   - ZIP final: /mnt/e/VTES/vtes-dataset.zip

🧵 12 hilos ejecutándose en un solo proceso
"""
import os
import random
import zipfile
import shutil
import threading
from PIL import Image

NUM_WORKERS = 12  # 12 hilos
NUM_IMAGES = 10000  # Total imágenes
NUM_PER_WORKER = NUM_IMAGES // NUM_WORKERS  # 833 imágenes por hilo

# Contador global para sincronizar los hilos
image_counter = [0]
lock = threading.Lock()

def generate_image(cards_files, backgrounds_files, image_index):
    """
    Genera una imagen con 1-100 cartas.
    Todas las cartas se acumulan en la MISMA imagen.
    """
    # Selecciona un fondo aleatorio
    bg_file = random.choice(backgrounds_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    
    # Asegurarse de que el fondo tenga 1080x1080
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Generar entre 1 y 100 cartas (como en trainCreator_mini.py)
    num_cards = random.randint(1, 100)
    
    # Crear la imagen base (una sola vez)
    result_img = bg_img.copy()
    
    # Añadir todas las cartas a la misma imagen
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
        
        # Paste (añade la carta a la imagen acumulada)
        if card_img.mode == 'RGBA':
            mask = card_img.split()[3]
        else:
            mask = None
        result_img.paste(card_img, (paste_x, paste_y), mask)
    
    # Convertir a RGB y guardar (una sola vez al final)
    result_img_rgb = result_img.convert("RGB")
    result_img_rgb.save(f"vtes-dataset/image_{image_index:06d}.jpg", quality=100)

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
    
    # Ruta de salida del ZIP
    target_dir = '/mnt/e/VTES'
    if not os.path.exists(target_dir):
        print(f'❌ Directorio de salida no existe: {target_dir}')
        print(f'Por favor crea el directorio {target_dir} o usa la ruta actual')
        return
    
    print(f"📍 Ubicaciones:")
    print(f"   Cartas: {cards_dir}")
    print(f"   Fondos: {backgrounds_dir}")
    print(f"   Imágenes: vtes-dataset/")
    print(f"   ZIP final: {target_dir}/vtes-dataset.zip")
    print()
    
    print(f"Iniciando generación con {NUM_WORKERS} hilos en un solo proceso...")
    print(f"   Total imágenes: {NUM_IMAGES}")
    print(f"   Imágenes por hilo: {NUM_PER_WORKER}")
    print(f"   Cartas por imagen: 1-100 (aleatorio)")
    print()
    
    # Crear y lanzar los hilos
    threads = []
    for i in range(NUM_WORKERS):
        thread = threading.Thread(
            target=generate_image,
            args=(cards_files, backgrounds_files, i)
        )
        threads.append(thread)
        thread.start()
    
    # Esperar a que todos los hilos terminen
    print("\nProcesos en marcha...")
    for thread in threads:
        thread.join()
    
    # Comprimir a ZIP
    zip_path = os.path.join(target_dir, 'vtes-dataset.zip')
    print(f'\nComprimiendo a ZIP: {zip_path}')
    
    # Comprimir todo el dataset
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for j in range(NUM_IMAGES):
            file_path = f"vtes-dataset/image_{j:06d}.jpg"
            if os.path.exists(file_path):
                zipf.write(file_path, f"image_{j:06d}.jpg")
    
    # Limpiar carpeta temporal
    shutil.rmtree('vtes-dataset')
    
    # Calcular tamaño del ZIP
    zip_size = os.path.getsize(zip_path)
    print(f"\n✅ Dataset completado:")
    print(f"   📄 Imágenes: {NUM_IMAGES}")
    print(f"   📦 ZIP: {zip_path}")
    print(f"   💾 Tamaño: {zip_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()