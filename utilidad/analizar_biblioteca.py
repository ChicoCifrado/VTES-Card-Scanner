#!/usr/bin/env python3
"""
Analizar carta de biblioteca
Detectar: forma borde, caja central, texto inferior
"""

from PIL import Image
import numpy as np
import cv2

def analizar(img_path):
    """
    Analizar carta y determinar si es biblioteca o vampiro.
    """
    
    img = Image.open(img_path)
    w, h = img.size
    
    print(f"\n📊 Carta: {img_path}")
    print(f"  Tamaño: {w}x{h}")
    
    # 1. Analizar proporción
    img_np = np.array(img.convert('L'))
    
    # Buscar contorno
    contours, _ = cv2.findContours(img_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        x, y, w_rect, h_rect = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        
        # Aspecto
        aspect_ratio = w_rect / h_rect
        
        # Texto inferior (zona inferior 30%)
        texto_inferior = img.crop((0, int(h * 0.7), w, h))
        texto_np = np.array(texto_inferior.convert('L'))
        texto_binary = (texto_np > 50).astype(np.uint8)  # Convertir a uint8
        texto_area = cv2.countNonZero(texto_binary)
        texto_total = texto_binary.size
        prop_texto = texto_area / texto_total if texto_total > 0 else 0
        
        # Detección tipo
        # Biblioteca: texto inferior grande (>40%) + aspecto más cuadrado (0.6-1.2)
        # Vampiro: texto inferior pequeño + aspecto ovalado (<0.6) o muy ancho (>1.3)
        
        if prop_texto > 0.40 and 0.6 <= aspect_ratio <= 1.2:
            tipo = "biblioteca"
            forma = "cuadrada"
            print(f"  📖 Tipo: LIBRERÍA")
            print(f"    - Texto inferior: {prop_texto:.1%} (grande)")
            print(f"    - Aspecto: {aspect_ratio:.2f} (cuadrado)")
        else:
            tipo = "vampiro"
            forma = "ovalada"
            print(f"  🧛 Tipo: VAMPIRO")
            print(f"    - Texto inferior: {prop_texto:.1%} (pequeño)")
            print(f"    - Aspecto: {aspect_ratio:.2f} (ovalado)")
        
        # 2. Extraer caja central
        margin_x = int(w * 0.15)
        margin_y = int(h * 0.20)
        caja_central = img.crop((margin_x, margin_y, w - margin_x, h - margin_y))
        
        # 3. Hash de caja central
        caja_np = np.array(caja_central.convert('L'))
        threshold = np.percentile(caja_np, 40)
        binary = caja_np > threshold
        
        # Resize
        if binary.size > 4096:
            binary = cv2.resize(binary.astype(np.uint8), (128, 128))
        
        # 8x8 pixelización
        cell = 16
        hash_central = []
        for i in range(8):
            for j in range(8):
                y1, y2 = i*cell, (i+1)*cell
                x1, x2 = j*cell, (j+1)*cell
                celda = binary[y1:y2, x1:x2]
                active = np.sum(celda) / celda.size
                hash_central.append('1' if active > 0.3 else '0')
        
        hash_central = ''.join(hash_central)
        print(f"  Hash central: {hash_central}")
        
        return {
            'tipo': tipo,
            'forma': forma,
            'hash_central': hash_central,
            'prop_texto': prop_texto,
            'aspect_ratio': aspect_ratio,
        }
    
    return {'tipo': 'desconocida', 'forma': 'desconocida', 'hash_central': None}

if __name__ == '__main__':
    import sys
    
    # Verificar argumento
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        # Usar la imagen proporcionada
        img_path = '/home/cifrado/.openclaw/media/inbound/absolutetyranny---243bd4f6-d583-4a20-9b4d-9587e4bed018.jpg'
    
    resultado = analizar(img_path)
    print(f"\n✅ Análisis completado")
    print(f"  Tipo: {resultado['tipo']}")
    print(f"  Hash: {resultado['hash_central']}")
