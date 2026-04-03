import os
import random
from multiprocessing import Pool, cpu_count
from PIL import Image

def scale_and_place_card(card_img, bg_img, scale_factor, target_size=1080):
    """
    Escala la carta y la coloca en posición aleatoria.
    Todo el proceso se realiza en una imagen de 1080x1080.
    """
    # Asegurarse de que el fondo tenga 1080x1080
    if bg_img.size != (target_size, target_size):
        bg_img = bg_img.resize((target_size, target_size), Image.LANCZOS)
    
    # Calcula nuevas dimensiones con el factor de escala especificado
    new_width = int(target_size * scale_factor)
    new_height = int(card_img.height * (new_width / card_img.width))
    
    # Redimensiona la carta
    card_img = card_img.resize((new_width, new_height), Image.LANCZOS)
    
    # Coloca en posición totalmente aleatoria
    paste_x = random.randint(0, target_size - card_img.width)
    paste_y = random.randint(0, target_size - card_img.height)
    
    result_img = bg_img.copy()
    if card_img.mode == 'RGBA':
        mask = card_img.split()[3]
    else:
        mask = None
    result_img.paste(card_img, (paste_x, paste_y), mask)
    
    return result_img

def generate_dataset_image(cards_files, backgrounds_files, num_cards=10):
    """
    Genera una imagen del dataset VTES con un número fijo de cartas.
    Imagen de 1080x1080 sin compresión.
    """
    # Selecciona un fondo aleatorio
    bg_file = random.choice(backgrounds_files)
    bg_img = Image.open(bg_file).convert("RGBA")
    
    # Asegurarse de que el fondo tenga 1080x1080
    bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
    
    # Generar exactamente 10 cartas
    for i in range(num_cards):
        # Selecciona una carta aleatoria
        card_file = random.choice(cards_files)
        card_img = Image.open(card_file).convert("RGBA")
        
        # Determina el factor de escala (entre 0.02 y 0.08)
        scale_factor = random.uniform(0.02, 0.08)
        
        # Escala y coloca la carta
        bg_img = scale_and_place_card(card_img, bg_img, scale_factor)
    
    # Generar nombre único para la imagen
    img_filename = f"image_{random.randint(0, 10000):06d}.jpg"
    img_path = os.path.join('vtes-mini', img_filename)
    
    # Crear carpeta si no existe
    os.makedirs('vtes-mini', exist_ok=True)
    
    # Guardar sin compresión (calidad 100)
    bg_img = bg_img.convert("RGB")  # Convertir a RGB para JPG
    bg_img.save(img_path, quality=100)
    
    return img_path

def main():
    """Función principal para generar múltiples imágenes del dataset VTES en paralelo."""
    cards_dir = 'cartas_vtes'
    backgrounds_dir = 'background'
    
    if not os.path.exists(cards_dir):
        raise FileNotFoundError(f"La carpeta {cards_dir} no existe")
    if not os.path.exists(backgrounds_dir):
        raise FileNotFoundError(f"La carpeta {backgrounds_dir} no existe")
    
    cards_files = [f for f in os.listdir(cards_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    backgrounds_files = [f for f in os.listdir(backgrounds_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not cards_files:
        raise ValueError(f"No se encontraron imágenes en la carpeta {cards_dir}")
    if not backgrounds_files:
        raise ValueError(f"No se encontraron imágenes en la carpeta {backgrounds_dir}")
    
    num_processes = cpu_count()
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(generate_dataset_image, [(cards_files, backgrounds_files, 10)] * num_processes)
    
    print("✓ Múltiples imágenes del dataset VTES generadas con 10 cartas, escala 0.02-0.08, en 1080x1080, guardadas en vtes-mini")

if __name__ == "__main__":
    main()