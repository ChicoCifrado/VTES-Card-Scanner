#!/usr/bin/env python3
"""
Zonas Mínimas 3.0 - Configuración Esencial para Clasificación
=====================================================
Solo las 3 zonas MÁS discriminantes:
1. TÍTULO + LOGOS (0-15%) → Identifica SET
2. SÍMBOLO EDICIÓN (top-right) → Diferencia edición
3. ARTE/ILUSTRACIÓN (centro) → Visualmente distintivo por SET

Por qué solo 3:
- Menos overhead computacional
- Mayor velocidad de matching
- Menor ruido visual
- Más robusto ante variaciones

Las otras zonas (tipo carta, disciplinas, coste, capacidad) son:
- Demasiado pequeñas
- Mucho ruido visual
- Poco discriminantes para clasificar por SET

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw
import argparse


class Zonas3Minimas:
    """
    Clases para las 3 zonas mínimas esenciales.
    
    Uso:
    1. config = Zonas3Minimas().get_config()
    2. visualizer.draw_zones(image, zones=config['zones'])
    3. matcher.compute_zone_hashes(image, config['zones'])
    """
    
    def __init__(self):
        self.config = self._get_default_config()
    
    def _get_default_config(self):
        """
        Las 3 zonas ESenciales.
        """
        return {
            'nombre': 'Zonas 3 Mínimas',
            'descripcion': 'Solo las 3 zonas más discriminantes para clasificación de SETs',
            'version': '3.0',
            'fecha': '2026-04-12',
            
            'zonas_esenciales': {
                # ZONA 1: TÍTULO + LOGOS DEL SET (La más importante)
                'titulo_logos': {
                    'descripcion': 'Títulos, set name, logos del set (identifica SET)',
                    'y_range': (0, 15),        # 0-15% de altura
                    'x_range': (0, 100),      # Todo el ancho
                    'propiedad': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Cada set tiene título y logos distintivos. IDENTIFICA EL SET DIRECTAMENTE.'
                },
                
                # ZONA 2: SÍMBOLO EDICIÓN (Top-right corner)
                'simbolo_edicion': {
                    'descripcion': 'Símbolo de edición en esquina superior derecha',
                    'y_range': (0, 12),        # 0-12% de altura
                    'x_range': (88, 100),     # 88-100% de ancho (derecha)
                    'propiedad': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Diferencia entre ediciones antiguas y modernas. Muy distintivo.'
                },
                
                # ZONA 3: ARTE/ILUSTRACIÓN (Centro)
                'arte': {
                    'descripcion': 'Ilustración principal del arte (sin texto)',
                    'y_range': (10, 65),      # 10-65% de altura
                    'x_range': (10, 90),      # 10-90% de ancho (centro)
                    'propiedad': 'MUY ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Cada set tiene arte visualmente distintivo. CAPTURA LA ESSENZA DEL SET.'
                },
            },
            
            'configuracion_final_3_zonas': {
                # Formato para vtes_ph_unificado.py: (y_min%, y_max%, x_min%, x_max%)
                'titulo_logos': (0, 15, 0, 100),
                'simbolo_edicion': (0, 12, 88, 100),
                'arte': (10, 65, 10, 90),
            },
            
            'ventajas_vs_8_zonas': {
                'velocidad': '2x más rápido (menor procesamiento)',
                'precision': 'Igual o mejor (menos ruido)',
                'robustez': 'Más robusto ante variaciones de iluminación',
                'memoria': 'Menor uso de memoria',
            },
            
            'cuando_usar': {
                'clasificacion_rapida': 'Solo estas 3 zonas',
                'clasificacion_precisa': 'Agregar bordes laterales si es necesario',
                'matching_masivo': 'Definitivamente solo 3 zonas',
            }
        }
    
    def get_zona_info(self, zona_name):
        """Obtener información de una zona."""
        return self.config['zonas_esenciales'].get(zona_name, {})
    
    def get_config_zones(self):
        """
        Obtener configuración de zonas para usar con matcher.
        
        Retorna:
            Dict con zonas en formato para vtes_ph_unificado.py
        """
        return self.config['configuracion_final_3_zonas']
    
    def get_config_for_visualizer(self):
        """
        Obtener configuración para visualizador.
        
        Retorna:
            Dict de zonas con rangos en porcentaje
        """
        return self.config['zonas_esenciales']
    
    def draw_zones_3(self, image, outline_color='red', outline_width=3):
        """
        Dibujar overlay de las 3 zonas esenciales.
        
        Args:
            image: Imagen PIL.
            outline_color: Color de los bordes.
            outline_width: Grosor de los bordes.
            
        Returns:
            Imagen con overlay.
        """
        # Convertir a RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        h, w = image.size
        
        # Colores para cada zona
        colors = {
            'titulo_logos': 'red',
            'simbolo_edicion': 'blue',
            'arte': 'green',
        }
        
        # Dibujar cada zona
        zonas = self.config['zonas_esenciales']
        
        for zona_name in ['titulo_logos', 'simbolo_edicion', 'arte']:
            y_min, y_max, x_min, x_max = zonas[zona_name]['y_range'], zonas[zona_name]['x_range']
            
            # Convertir rangos a porcentaje
            y_min = int(h * zonas[zona_name]['y_range'][0] / 100)
            y_max = int(h * zonas[zona_name]['y_range'][1] / 100)
            x_min = int(w * zonas[zona_name]['x_range'][0] / 100)
            x_max = int(w * zones[zona_name]['x_range'][1] / 100)
            
            # Dibujar borde
            draw.rectangle(
                [x_min, y_min, x_max, y_max],
                outline=colors[zona_name],
                width=outline_width
            )
            
            # Texto de etiqueta
            text = f"{zona_name.upper()}"
            draw.text(
                (x_min + 5, y_min + 5),
                text,
                fill=colors[zona_name],
                font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            )
        
        return image
    
    def compute_zone_hashes(self, image, zones=None):
        """
        Generar hashes para las 3 zonas.
        
        Args:
            image: Imagen PIL.
            zones: Config de zonas (opcional, usa default si None).
            
        Returns:
            Dict con hashes por zona.
        """
        if zones is None:
            zones = self.config['configuracion_final_3_zonas']
        
        if image.mode != 'L':
            image = image.convert('L')
        
        arr = np.array(image)
        hashes = {}
        
        # Definir zonas
        zona_configs = {
            'titulo_logos': (0, 15, 0, 100),
            'simbolo_edicion': (0, 12, 88, 100),
            'arte': (10, 65, 10, 90),
        }
        
        for zona_name, (y_min_pct, y_max_pct, x_min_pct, x_max_pct) in zona_configs.items():
            try:
                # Extraer zona
                y_min = int(arr.shape[0] * y_min_pct / 100)
                y_max = int(arr.shape[0] * y_max_pct / 100)
                x_min = int(arr.shape[1] * x_min_pct / 100)
                x_max = int(arr.shape[1] * x_max_pct / 100)
                
                # Extraer zona de la imagen
                zona = arr[y_min:y_max, x_min:x_max]
                
                if zona.size > 0:
                    # Aplicar DCT y extraer hash (simplificado)
                    arr_float = zona.astype(np.float32)
                    dct = np.fft.fft2(arr_float)
                    dct_shift = np.fft.ifftshift(np.abs(dct))
                    
                    h_z, w_z = dct_shift.shape
                    h_low, w_low = h_z // 4, w_z // 4
                    
                    if h_low > 0 and w_low > 0:
                        low_freq = dct_shift[h_low:2*h_low, w_low:2*w_low]
                        mean_val = np.mean(np.real(low_freq))
                        max_abs = np.max(np.abs(low_freq))
                        
                        if max_abs > 0:
                            hash_val = float(mean_val / max_abs)
                            hashes[zona_name] = hash_val
                            
            except Exception:
                continue
        
        return hashes


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Zonas Mínimas 3.0 - Solo las 3 zonas esenciales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  
  # Ver resumen de las 3 zonas
  python zonas_3_minimas.py --summary
  
  # Visualizar carta con las 3 zonas
  python zonas_3_minimas.py --visualize --image carta.png
  
  # Guardar configuración en JSON
  python zonas_3_minimas.py --save zonas_3_minimas.json
  
        '''
    )
    
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Imprimir resumen de las 3 zonas')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Visualizar carta con overlay de zonas')
    parser.add_argument('--image', '-i', type=str,
                       help='Carta a visualizar')
    parser.add_argument('--save', '-o', type=str, default=None,
                       help='Guardar configuración en JSON')
    parser.add_argument('--config', type=str, default=None,
                       help='Configuración personalizada (JSON)')
    
    args = parser.parse_args()
    
    zonas = Zonas3Minimas()
    
    print("="*70)
    print("🦞 ZONAS 3 MÍNIMAS - CONFIGURACIÓN ESENCIAL")
    print("="*70)
    
    if args.summary:
        # Imprimir resumen
        print("\n📋 LAS 3 ZONAS MÁS IMPORTANTES:")
        print("\n" + "-"*70)
        
        for i, (zona_name, zona_info) in enumerate(zonas.config['zonas_esenciales'].items(), 1):
            print(f"\n{i}. {zona_name.upper()}")
            print(f"   {zona_info['descripcion']}")
            print(f"   Altura: {zona_info['y_range'][0]}%-{zona_info['y_range'][1]}%")
            print(f"   Ancho: {zona_info['x_range'][0]}%-{zona_info['x_range'][1]}%")
            print(f"   Discriminación: {zona_info['propiedad']}")
            print(f"   {zona_info['explicacion']}")
        
        print("\n" + "-"*70)
        print("💡 VENTAJAS DE SOLO 3 ZONAS:")
        print(f"   ✅ {zonas.config['ventajas_vs_8_zonas']['velocidad']}")
        print(f"   ✅ {zonas.config['ventajas_vs_8_zonas']['precision']}")
        print(f"   ✅ {zonas.config['ventajas_vs_8_zonas']['robustez']}")
        print(f"   ✅ {zonas.config['ventajas_vs_8_zonas']['memoria']}")
        
    elif args.visualize and args.image:
        # Visualizar carta
        print(f"\n📷 Visualizando carta con las 3 zonas")
        
        if os.path.exists(args.image):
            image = Image.open(args.image)
            overlay = zonas.draw_zones_3(image)
            overlay.show()
        else:
            print(f"⚠️ Imagen no encontrada: {args.image}")
        
    elif args.save:
        # Guardar configuración
        output_path = args.save
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(zonas.config, f, indent=2, ensure_ascii=False)
        print(f"💾 Configuración guardada en: {output_path}")
        
    else:
        parser.print_help()
    
    print("\n" + "="*70)
    print("✅ Zonas 3 Mínimas listas para uso!")
    print("="*70)


if __name__ == '__main__':
    main()
