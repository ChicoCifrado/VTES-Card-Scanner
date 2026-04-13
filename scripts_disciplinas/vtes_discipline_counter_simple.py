#!/usr/bin/env python3
"""Contar disciplinas de vampiros"""

from PIL import Image
import cv2
import os

def detectar_disciplina(img, w, h):
    """Detectar disciplina en banda lateral."""
    
    # Extraer banda lateral (5%-85%)
    banda_x1 = int(w * 0.05)
    banda_x2 = int(w * 0.85)
    banda_img = img.crop((banda_x1, 0, banda_x2, h))
    
    # Eliminar texto
    banda_np = cv2.cvtColor(banda_img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(banda_np, 128, 255, cv2.THRESH_BINARY)
    
    # Morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Contar
    if contours:
        return len(contours)
    
    return 0

def procesar_carpeta(folder, output):
    """Procesar carpeta y contar disciplinas."""
    
    images = [os.path.join(folder, f) for f in os.listdir(folder) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"📂 Carpeta: {folder}")
    print(f"📁 Imágenes: {len(images)}\n")
    
    resultados = {}
    
    for img_path in images:
        try:
            img = Image.open(img_path)
            w, h = img.size
            
            count = detectar_disciplina(img, w, h)
            resultados[os.path.basename(img_path)] = count
            
            print(f"[{os.path.basename(img_path)}] → {count} disciplinas")
        
        except Exception as e:
            print(f"Error con {os.path.basename(img_path)}: {e}")
            continue
    
    # Guardar
    with open(output, 'w') as out:
        out.write("# Conteo Disciplinas\n")
        for nombre, count in resultados.items():
            out.write(f"[{nombre}] {count}\n")
    
    print(f"\n✅ Resultados guardados: {output}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', '-f', required=True)
    parser.add_argument('--output', default='discipline_counts.txt')
    args = parser.parse_args()
    procesar_carpeta(args.folder, args.output)
