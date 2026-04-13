#!/usr/bin/env python3
"""
VTES Discipline Counter
Extrae, cuenta y clasifica disciplinas de cartas VTES
Genera "discipline fingerprint" = cantidad + tipos de símbolos
"""

import os
import json
import cv2
import numpy as np
from PIL import Image

# === CONFIGURACIÓN ===
MARGEN_IZQ = 5      # Margen izquierdo (5%)
MARGEN_SUP = 15     # Margen superior (15%)
HASH_BITS = 8       # Bits por zona para fallback

# === DEFINICIÓN DE ZONAS ===
# Banda lateral captura TODAS las disciplinas (izquierda a la banda)
# Zonas:
#   - top_superior: Logo/título en la banda superior
#   - imagen_central: Arte principal + disciplinas centrales
#   - banda_lateral: TODAS las disciplinas en la banda lateral

ZONAS = {
    'top_superior': (MARGEN_IZQ, 20, 0, 100),      # Logo + título (margen sup 15%)
    'imagen_central': (MARGEN_IZQ, 65, MARGEN_SUP, 100),  # Arte principal + disciplines
    'banda_lateral': (MARGEN_IZQ, 85, 0, 100),     # TODAS las disciplines
}


def detect_disciplines(img, zona_name='banda_lateral'):
    """
    Detectar disciplinas en una zona específica.
    Devuelve lista de disciplinas con sus características.
    """
    disciplines = []
    
    try:
        # Resize si es necesario
        if img.width > 1920 or img.height > 1920:
            img = img.resize((1920, 1920), Image.LANCZOS)
        
        w, h = img.size
        
        # Extraer zona
        if zona_name in ZONAS:
            x1_pct, x2_pct, y1_pct, y2_pct = ZONAS[zona_name]
        else:
            return disciplines
        
        x1, x2, y1, y2 = (int(w * pct / 100) for pct in [x1_pct, x2_pct, y1_pct, y2_pct])
        
        if x2 <= x1 or y2 <= y1:
            return disciplines
        
        # Convertir a numpy array
        img_np = np.array(img.convert('L'))
        zona = img_np[y1:y2, x1:x2]
        
        # Thresholding binario
        _, binary = cv2.threshold(zona, 128, 255, cv2.THRESH_BINARY)
        
        # Morphology para eliminar ruido
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Encontrar contornos (disciplines como objetos)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar disciplinas válidas
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Ignorar objetos muy pequeños o muy grandes
            if area < 50 or area > 0.3 * (zona.size):
                continue
            
            # Extraer disciplina
            disciplina_img = zona[y:y+h, x:x+w]
            
            # Calcular features
            disciplinas.append({
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'area': area,
                'aspect_ratio': w/h,
                'density': area / (w * h),
                'image': disciplina_img,
            })
    
    except Exception as e:
        print(f"Error al detectar disciplinas: {e}")
    
    return disciplines


def classify_discipline(disciplina, img_full):
    """
    Clasificar disciplina por tipo de símbolo.
    Usa features invariantes: forma, simetría, complejidad.
    """
    try:
        disciplina_np = np.array(disciplina, dtype=np.uint8)
        
        # Hough Lines para detección de líneas
        edges = cv2.Canny(disciplina_np, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
        
        # Contar líneas
        line_count = len(lines) if lines is not None else 0
        
        # Hough Circle para detección de círculos (discos, runas circulares)
        gray = cv2.cvtColor(disciplina_np, cv2.COLOR_GRAY2BGR)
        circles = cv2.HoughCircles(disciplina_np, cv2.HOUGH_GRADIENT, dp=1, minDist=10,
                                   param1=50, param2=50, minRadius=5, maxRadius=50)
        
        circle_count = 0
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            circle_count = len(circles)
        
        # Calcular huella de frecuencia (FFT) para formas complejas
        f, T = np.fft.fft(disciplina_np)
        amplitude = np.abs(T)
        
        # Contar picos (características distintivas)
        peaks, _ = cv2.findPeaks(amplitude.flatten(), distance=50)
        peak_count = len(peaks)
        
        # Determinar tipo
        if circle_count > 0:
            tipo = 'circulo'
        elif line_count > 5:
            tipo = 'lineas'
        elif peak_count > 5:
            tipo = 'complejo'
        elif disciplina_np.size < 100:
            tipo = 'simple'
        else:
            tipo = 'geometrico'
        
        return {
            'tipo': tipo,
            'lineas': line_count,
            'circulos': circle_count,
            'picos': peak_count,
        }
    
    except Exception as e:
        return {'error': str(e)}


def extract_discipline_template(disciplina_img, bits=8):
    """
    Extraer template simplificado de disciplina.
    Usa avg pooling + binarización con umbral adaptativo.
    """
    try:
        # Resize a tamaño fijo
        disciplina_np = np.array(disciplina_img.convert('L'))
        if disciplina_np.size > 10000:
            disciplina_np = cv2.resize(disciplina_np, (100, 100))
        
        # Umbral adaptativo (percentil 60)
        threshold = np.percentile(disciplina_np, 60)
        binary = disciplina_np > threshold
        
        # Avg pooling + binarización
        pool_size = 4
        pooled = (binary.reshape(-1, pool_size, pool_size, -1).mean(axis=1)).flatten()
        
        # Binarizar
        binary_pooled = pooled > (np.mean(pooled) + 0.2 * np.std(pooled))
        
        # Convertir a string
        return ''.join(['1' if b else '0' for b in binary_pooled[:bits]])
    
    except Exception as e:
        return None


def process_disciplines(img, img_full=None):
    """
    Procesar todas las disciplinas de la carta.
    Devuelve fingerprint = {cantidad: tipos}
    """
    disciplines = []
    
    # Detectar disciplinas en cada zona
    for zona_name in ZONAS.keys():
        disciplinas_zona = detect_disciplines(img, zona_name)
        disciplines.extend(disciplines_zona)
    
    # Clasificar cada disciplina
    for disc in disciplines:
        classificacion = classify_discipline(disc['image'], img_full) if img_full else None
        disc.update(classificacion)
    
    # Extraer template simplificado
    for disc in disciplines:
        template = extract_discipline_template(disc['image'])
        disc['template'] = template
    
    return disciplines


def generate_discipline_fingerprint(disciplines):
    """
    Generar fingerprint de disciplinas.
    Formato: {cantidad_total: [tipos], templates: [...]
    """
    fingerprint = {
        'cantidad': len(disciplines),
        'tipos': {},
        'templates': [],
        'features': [],
    }
    
    # Contar por tipo
    tipo_counts = {}
    for disc in disciplines:
        tipo = disc.get('tipo', 'unknown')
        tipo_counts[tipo] = tipo_counts.get(tipo, 0) + 1
    
    fingerprint['tipos'] = tipo_counts
    
    # Extraer templates (invariantes)
    for disc in disciplines:
        if disc.get('template'):
            fingerprint['templates'].append({
                'tipo': disc.get('tipo'),
                'template': disc['template'],
                'features': {
                    'area': disc.get('area'),
                    'aspect_ratio': round(disc.get('aspect_ratio', 0), 2),
                }
            })
    
    # Calcular features globales
    total_area = sum(d.get('area', 0) for d in disciplines)
    fingerprint['features'] = {
        'total_disciplines': len(disciplines),
        'total_area': total_area,
        'average_density': total_area / len(disciplines) if disciplines else 0,
        'tipo_counts': tipo_counts,
    }
    
    return fingerprint


def process_folder(folder, output, img_full_path=None):
    """
    Procesar carpeta de cartas y extraer fingerprints.
    """
    
    images = []
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        for f in os.listdir(folder):
            if f.lower().endswith(ext):
                images.append(os.path.join(folder, f))
    
    print(f"\n📂 Carpeta: {folder}")
    print(f"  🔍 Encontradas {len(images)} imágenes")
    print(f"  ⚙️ Extrayendo disciplinas")
    
    results = {}
    corrupted = []
    
    for img_path in images:
        try:
            img = Image.open(img_path)
            w, h = img.size
            
            # Extraer disciplinas
            disciplines = process_disciplines(img, img_full_path=img_full_path)
            
            # Generar fingerprint
            fingerprint = generate_discipline_fingerprint(disciplines)
            
            # Guardar
            results[os.path.basename(img_path)] = {
                'cantidad': fingerprint['cantidad'],
                'tipos': fingerprint['tipos'],
                'features': fingerprint['features'],
            }
            
        except Exception as e:
            corrupted.append(img_path)
            continue
    
    # Guardar
    if results:
        with open(output, 'w') as f:
            f.write("# VTES Discipline Fingerprints\n")
            f.write(f"# Total: {len(results)} cartas\n")
            f.write(f"# Format: {{cantidad: tipos, features: {...}}}\n\n")
            
            for img_name, fp in sorted(results.items()):
                f.write(f"[{img_name}]\n")
                f.write(f"  cantidad: {fp['cantidad']}\n")
                f.write(f"  tipos: {fp['tipos']}\n")
                f.write(f"  total_area: {fp['features'].get('total_area', 0)}\n")
                if fp['features'].get('tipo_counts'):
                    for tipo, count in fp['features']['tipo_counts'].items():
                        f.write(f"    - {tipo}: {count}\n")
        
        print(f"\n  ✅ Fingerprints guardados: {output}")
        
        # Estadísticas
        cantidad_counts = {}
        for img, fp in results.items():
            cantidad = fp['cantidad']
            cantidad_counts[cantidad] = cantidad_counts.get(cantidad, 0) + 1
        
        print(f"\n  📊 Estadísticas de disciplinas:")
        print(f"    - Cantidad total: {cantidad_counts}")
        
        tipo_counts_global = {}
        for img, fp in results.items():
            for tipo, count in fp['tipos'].items():
                tipo_counts_global[tipo] = tipo_counts_global.get(tipo, 0) + count
        
        print(f"    - Tipos encontrados: {tipo_counts_global}")


def main():
    parser = argparse.ArgumentParser(description='VTES Discipline Counter')
    parser.add_argument('command', choices=['count'], help='Comando')
    parser.add_argument('--folder', '-f', required=True, help='Carpeta')
    parser.add_argument('--output', '-o', help='Salida')
    parser.add_argument('--zona', default='banda_lateral', help='Zona a analizar')
    
    args = parser.parse_args()
    
    results = {}
    process_folder(args.folder, args.output, args.zona)
    
    print(f"\n✅ Completado: {len(results)} cartas procesadas")


if __name__ == '__main__':
    main()
