#!/usr/bin/env python3
"""
Generador de dataset VTES para OBS plugin (multiprocesamiento).
Crea imágenes con 1-100 cartas, fondo aleatorio y rotación aleatoria (-180° a +180°).
Genera 10,000 imágenes comprimidas en vtes-dataset.zip.

📍 Ubicación de las imágenes:
   - Salida: /mnt/e/VTES/VTES-Card-Scanner/vtes-dataset/
   - ZIP final: /mnt/e/VTES/VTES-Card-Scanner/vtes-dataset.zip

🔧 Multiprocesamiento: usa todos los núcleos disponibles
"""
import os
import random
import zipfile
import multiprocessing

# Configuración global
TARGET_DIR = '/mnt/e/VTES/VTES-Card-Scanner'
VTES_DATASET_DIR = os.path.join(TARGET_DIR, 'vtes-dataset')
ZIP_PATH = os.path.join(TARGET_DIR, 'vtes-dataset.zip')
NUM_WORKERS = multiprocessing.cpu_count()  # Usa todos los núcleos disponibles
NUM_IMAGES = 10000  # Total imágenes
NUM_PER_WORKER = NUM_IMAGES // NUM_WORKERS  # ~833 imágenes por worker

from PIL import Image

def generate_image_wrapper(args):
    """
    Wrapper para multiprocessing.Pool.
    args: (cards_files, backgrounds_files, image_index)
    """
    cards_files, backgrounds_files, image_index = args
    
    # Selecciona un fondo aleatorio
    bg_file = random.choice(backgrounds_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    
    # Asegurarse de que el fondo tenga 1080x1080
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Generar entre 1 y 100 cartas
    num_cards = random.randint(1, 100)
    
    # Crear la imagen base
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
    
    # Convertir a RGB y guardar en la ruta absoluta correcta
    output_path = os.path.join(VTES_DATASET_DIR, f"image_{image_index:06d}.jpg")
    result_img_rgb = result_img.convert("RGB")
    result_img_rgb.save(output_path, quality=100)

def main():
    """Función principal para generar múltiples imágenes del dataset VTES."""
    # Rutas relativas a los scripts
    base_path = os.path.dirname(os.path.abspath(__file__))
    cards_dir = os.path.join(base_path, 'cartas_vtes')
    backgrounds_dir = os.path.join(base_path, 'fondos_vtes')
    
    # Verificar carpetas
    if not os.path.exists(cards_dir):
        raise FileNotFoundError(f"La carpeta {cards_dir} no existe")
    if not os.path.exists(backgrounds_dir):
        raise FileNotFoundError(f"La carpeta {backgrounds_dir} no existe")
    
    # Obtener listados de archivos
    try:
        cards_files = [os.path.join(cards_dir, f) for f in os.listdir(cards_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        backgrounds_files = [os.path.join(backgrounds_dir, f) for f in os.listdir(backgrounds_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    if not cards_files:
        raise ValueError(f"No se encontraron imágenes en la carpeta {cards_dir}")
    if not backgrounds_files:
        raise ValueError(f"No se encontraron imágenes en la carpeta {backgrounds_dir}")
    
    print(f"📍 Archivos:")
    print(f"   Cartas: {len(cards_files)} archivos encontrados")
    print(f"   Fondos: {len(backgrounds_files)} archivos encontrados")
    print()
    
    # Asegurar que la carpeta de salida existe
    os.makedirs(VTES_DATASET_DIR, exist_ok=True)
    print(f"✅ Carpeta de salida lista: {VTES_DATASET_DIR}")
    print()
    
    # Preparamos los argumentos para cada worker
    args_list = [(cards_files, backgrounds_files, i) for i in range(NUM_IMAGES)]
    
    print(f"✅ Configuración multiprocessing:")
    print(f"   Procesadores: {NUM_WORKERS}")
    print(f"   Imágenes totales: {NUM_IMAGES}")
    print(f"   Imágenes por procesador: {NUM_PER_WORKER}")
    print(f"   Cartas por imagen: 1-100 (aleatorio)")
    print()
    
    print(f"Iniciando generación con {NUM_WORKERS} procesos en paralelo...")
    print(f"   Total imágenes: {NUM_IMAGES}")
    print()
    
    # Crear pool de multiprocessing con N workers (un proceso por núcleo)
    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        # Generar índices para todas las imágenes
        pool.map(generate_image_wrapper, args_list)
    
    # Verificar cuántas imágenes se generaron
    generated_images = len([f for f in os.listdir(VTES_DATASET_DIR) if f.endswith('.jpg')])
    print(f"\n✅ Generadas: {generated_images} imágenes")
    
    # Comprimir a ZIP
    print(f'\nComprimiendo a ZIP: {ZIP_PATH}')
    
    # Comprimir todo el dataset usando rutas absolutas
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for j in range(NUM_IMAGES):
            file_path = os.path.join(VTES_DATASET_DIR, f"image_{j:06d}.jpg")
            if os.path.exists(file_path):
                zipf.write(file_path, f"image_{j:06d}.jpg")
    
    # Verificar y mostrar tamaño del ZIP
    if os.path.exists(ZIP_PATH):
        zip_size = os.path.getsize(ZIP_PATH)
        print(f"\n✅ Dataset completado:")
        print(f"   📄 Imágenes: {generated_images}")
        print(f"   📦 ZIP: {ZIP_PATH}")
        print(f"   💾 Tamaño: {zip_size / 1024 / 1024:.1f} MB")
    else:
        print(f"\n❌ Error: No se pudo crear el ZIP en {ZIP_PATH}")

if __name__ == "__main__":
    main()
