import os
import random
import zipfile
import shutil
from PIL import Image

def scale_and_place_card(card_img, bg_img, scale_factor=None):
    """
    Escala la carta, aplica rotación y la coloca en posición aleatoria.
    Todo el proceso se realiza en una imagen de 1080x1080.
    
    """
    # Asegurarse de que el fondo tenga 1080x1080
    if bg_img.size != (1080, 1080):
        bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Usa el factor de escala proporcionado o genera uno predeterminado
    if scale_factor is None:
        scale_factor = random.uniform(0.02, 0.08)
    
    # Calcula nuevas dimensiones
    new_width = int(1080 * scale_factor)
    new_height = int(card_img.height * (new_width / card_img.width))
    
    # Redimensiona la carta
    card_img = card_img.resize((new_width, new_height), Image.LANCZOS)
    
    # Genera un ángulo de rotación aleatorio entre -180 y +180 grados
    rotation_angle = random.uniform(-180, 180)
        
    # Aplica rotación (expand=True para ajustar tamaño)
    card_img = card_img.rotate(rotation_angle, expand=True, resample=Image.BICUBIC)

    # Coloca en posición totalmente aleatoria
    paste_x = random.randint(0, 1080 - card_img.width)
    paste_y = random.randint(0, 1080 - card_img.height)
    
    result_img = bg_img.copy()
    if card_img.mode == 'RGBA':
        mask = card_img.split()[3]
    else:
        mask = None
    result_img.paste(card_img, (paste_x, paste_y), mask)
    
    return result_img.convert("RGB")  # Convertir a RGB para JPG

def generate_dataset_image(cards_files, backgrounds_files):
    """
    Genera una imagen del dataset VTES con un número fijo de cartas.
    Imagen de 1080x1080 sin compresión.
    
    """
    # Selecciona un fondo aleatorio
    bg_file = random.choice(backgrounds_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    
    # Asegurarse de que el fondo tenga 1080x1080
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Generar entre 1 y 100 cartas
    num_cards = random.randint(1, 100)
    
    for _ in range(num_cards):
        # Selecciona una carta aleatoria
        card_file = random.choice(cards_files)
        card_img = Image.open(card_file).convert("RGBA")
        
        # Determina el factor de escala (entre 0.02 y 0.08)
        scale_factor = random.uniform(0.02, 0.08)
        
        # Escala y coloca la carta
        bg_img = scale_and_place_card(card_img, bg_img, scale_factor)
    
    return bg_img

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
    
    print("Generando imágenes...")
    for i in range(num_images):
        img = generate_dataset_image(cards_files, backgrounds_files)
        img.save(os.path.join(output_dir, f"image_{i:06d}.jpg"), quality=100)
        if (i + 1) % 2000 == 0:
            print(f"✓ Generadas {i + 1} de {num_images} imágenes")
    
    # Comprimir a ZIP
    zip_path = 'vtes-dataset.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(output_dir):
            if file.endswith('.jpg'):
                file_path = os.path.join(output_dir, file)
                zipf.write(file_path, file)
    
    # Limpiar carpeta temporal
    shutil.rmtree(output_dir)
    
    print(f"✓ {num_images} imágenes del dataset VTES generadas con 1-100 cartas, fondo aleatorio y rotación aleatoria (-180° a +180°), guardadas en vtes-dataset.zip")

if __name__ == "__main__":
    main()
