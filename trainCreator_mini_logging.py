#!/usr/bin/env python3
"""
Modificación de trainCreator_mini.py con logging de bounds.
Guarda cada carta colocada con su polígono (considerando rotación).
"""
import os
import random
import json
from PIL import Image

# === LOGGING DE CARTAS ===
# Estructura para guardar bounds de todas las cartas generadas
card_bounds_log = []

class CardPlacer:
    """Clase auxiliar para colocar cartas y guardar logs"""
    
    def __init__(self):
        self.bounds_log = []
    
    def scale_and_place_card(self, card_file, bg_img, scale_factor=None):
        """
        Escala, rota y coloca carta, guardando bounds.
        Devuelve la imagen resultante y el log.
        """
        # Asegurarse de que el fondo tenga 1080x1080
        if bg_img.size != (1080, 1080):
            bg_img = bg_img.resize((1080, 1080), Image.LANCZOS)
        
        # Usa el factor de escala proporcionado o genera uno predeterminado
        if scale_factor is None:
            scale_factor = random.uniform(0.02, 0.08)
        
        # Calcula nuevas dimensiones
        new_width = int(1080 * scale_factor)
        new_height = int(1080 * scale_factor)  # Mantener aspecto 1:1 para cartas
        
        # Redimensiona la carta
        card_img = Image.open(card_file).convert("RGBA")
        card_img = card_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Genera un ángulo de rotación aleatorio entre -180 y +180 grados
        rotation_angle = random.uniform(-180, 180)
        
        # Aplica rotación (expand=True para ajustar tamaño)
        card_img = card_img.rotate(rotation_angle, expand=True, resample=Image.BICUBIC)

        # Coloca en posición totalmente aleatoria
        paste_x = random.randint(0, 1080 - card_img.width)
        paste_y = random.randint(0, 1080 - card_img.height)
        
        # Guardar bounds ANTES de pastear
        card_name = os.path.basename(card_file)
        
        # Calcular polígono de la carta rotada (aproximado)
        # El rotate() expand=True hace que la imagen se ajuste a la caja
        bounds = {
            "name": card_name,
            "x": paste_x,
            "y": paste_y,
            "width": card_img.width,
            "height": card_img.height,
            "rotation": rotation_angle,
            "scale": scale_factor,
        }
        
        # Crear máscara para paste con transparencia
        if card_img.mode == 'RGBA':
            mask = card_img.split()[3]
        else:
            mask = Image.new('L', (card_img.width, card_img.height))
            mask.paste(255, (0, 0, card_img.width, card_img.height))
        
        result_img = bg_img.copy()
        result_img.paste(card_img, (paste_x, paste_y), mask)
        
        # Guardar log
        self.bounds_log.append(bounds)
        
        return result_img
    
    def get_bounds(self):
        """Devolver todos los bounds loguados"""
        return self.bounds_log


def generate_dataset_image(cards_files, backgrounds_files, placer=None):
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
    
    # Inicializar placer si no se proporciona
    if placer is None:
        placer = CardPlacer()
    
    for _ in range(num_cards):
        # Selecciona una carta aleatoria
        card_file = random.choice(cards_files)
        
        # Determina el factor de escala (entre 0.02 y 0.08)
        scale_factor = random.uniform(0.02, 0.08)
        
        # Escala y coloca la carta
        bg_img = placer.scale_and_place_card(card_file, bg_img, scale_factor)
    
    return bg_img, placer


def main():
    """Función principal para generar imágenes del dataset VTES."""
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
    
    print(f"📁 {len(cards_files)} cartas encontradas")
    print(f"📁 {len(backgrounds_files)} fondos encontrados")
    
    # Generar 10 imágenes con cantidad variable de cartas (1 a 100 cada una)
    for idx in range(10):
        placer = CardPlacer()
        img, placer = generate_dataset_image(cards_files, backgrounds_files, placer=placer)
        img_path = os.path.join('vtes-mini', f'image_{idx:06d}.jpg')
        os.makedirs('vtes-mini', exist_ok=True)
        # Convertir a RGB para guardar como JPEG
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size)
            bg.paste(img, mask=img.split()[3])
            img = bg
        img.save(img_path, quality=100)
        
        # Guardar log de bounds para esta imagen
        bounds_log = placer.get_bounds()
        
        if bounds_log:
            img_data = {
                "filename": os.path.basename(img_path),
                "num_cards": len(bounds_log),
                "bounds": bounds_log
            }
            
            # Guardar en JSON temporal
            json_path = os.path.join(base_path, 'vtes-mini', 'bounds_log.json')
            # Cargar y actualizar
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    all_bounds = json.load(f)
            except:
                all_bounds = {}
            
            all_bounds[idx] = img_data
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_bounds, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Image {idx:06d} guardada con {len(bounds_log)} cartas en vtes-mini/")
    
    print(f"\n📄 Bounds logs guardados en vtes-mini/bounds_log.json")
    print(f"   Total imágenes: 10")
    print(f"   Total bounds: {sum(len(v.get('bounds', [])) for v in all_bounds.values())}")

if __name__ == "__main__":
    main()