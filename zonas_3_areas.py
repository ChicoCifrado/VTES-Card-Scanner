#!/usr/bin/env python3
"""
Zonas 3 Áreas - Configuración Estratégica para Clasificación
=====================================================
Solo 3 Áreas Clave:
1. TOP SUPERIOR (0-15%) → Título + Símbolo Edición → Identifica SET
2. IMAGEN CENTRAL (10-65%) → Forma del arte → Vampiro vs Biblioteca
3. BANDA LATERAL (0-25%) → Clan + Tipo + Coste → Distintivo

Ventajas:
- Menos zonas = más rápido
- Menor ruido visual
- Mayor precisión en clasificación
- Más robusto a variaciones

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw
import argparse


class Zonas3Areas:
    """Clase para las 3 áreas estratégicas de clasificación."""
    
    def __init__(self):
        self.config = self._get_default_config()
    
    def _get_default_config(self):
        """Las 3 Áreas Estratégicas para clasificación."""
        return {
            'nombre': 'Zonas 3 Áreas Estratégicas',
            'descripcion': 'Solo 3 áreas clave para clasificar cartas VTES por SET',
            'version': '4.0',
            'fecha': '2026-04-12',
            
            'zonas': {
                # ÁREA 1: TOP SUPERIOR (Título + Símbolo Edición)
                'top_superior': {
                    'descripcion': 'Título del set + símbolo de edición en esquina superior',
                    'y_range': (0, 15),        # 0-15% de altura
                    'x_range': (0, 100),       # Todo el ancho
                    'propiedad': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'IDENTIFICA EL SET DIRECTAMENTE mediante título y logos + símbolo edición.'
                },
                
                # ÁREA 2: IMAGEN CENTRAL (Arte - forma ovalada vs cuadrada)
                'imagen_central': {
                    'descripcion': 'Ilustración principal (forma ovalada=vampiro, cuadrada=biblioteca)',
                    'y_range': (10, 65),       # 10-65% de altura
                    'x_range': (10, 90),       # 10-90% de ancho (centro)
                    'propiedad': 'MUY ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'FORMA DEL ARTE: ovalada=carta vampiro, cuadrada=carta biblioteca.'
                },
                
                # ÁREA 3: BANDA LATERAL (Izquierda - todo lo distintivo)
                'banda_lateral': {
                    'descripcion': 'Símbolo clan, requisitos, coste, tipo de carta (lateral izquierdo)',
                    'y_range': (0, 100),        # Todo el alto
                    'x_range': (0, 25),         # 0-25% de ancho (izquierda)
                    'propiedad': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Captura TIPO CARTA, CLAN, DISCIPLINAS y COSTE. Elementos distintivos del SET.'
                },
            },
            
            'configuracion_final_3_areas': {
                # Formato para vtes_ph_unificado.py: (y_min%, y_max%, x_min%, x_max%)
                'top_superior': (0, 15, 0, 100),      # Top: título + edición
                'imagen_central': (10, 65, 10, 90),   # Central: arte (forma)
                'banda_lateral': (0, 100, 0, 25),     # Lateral: clan, tipo, coste
            },
            
            'explicacion_estrategia': {
                'top_superior': 'Captura título y símbolo edición. Cada set tiene estilo único.',
                'imagen_central': 'La FORMA DEL ARTE diferencia vampiros (ovalados) de bibliotecas (cuadradas). Muy distintivo.',
                'banda_lateral': 'Captura elementos clave: tipo carta, clan, símbolos distintivos.',
            },
            
            'ventajas': {
                'rapidez': 'Más rápido con solo 3 áreas vs 8 zonas',
                'precicion': 'Menor ruido visual, mayor precisión',
                'robustez': 'Más robusto ante variaciones de iluminación',
            },
        }
    
    def get_zona_info(self, zona_name):
        """Obtener información de una zona."""
        return self.config['zonas'].get(zona_name, {})
    
    def get_config_zones(self):
        """Obtener configuración de zonas para usar con matcher."""
        return self.config['configuracion_final_3_areas']
    
    def draw_zones_3_areas(self, image, outline_color='red', outline_width=3):
        """
        Dibujar overlay de las 3 áreas estratégicas.
        
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
            'top_superior': 'red',
            'imagen_central': 'green',
            'banda_lateral': 'blue',
        }
        
        # Dibujar cada zona
        zonas = self.config['zonas']
        
        for zona_name in ['top_superior', 'imagen_central', 'banda_lateral']:
            y_min, y_max, x_min, x_max = zonas[zona_name]['y_range'], zonas[zona_name]['x_range']
            
            # Convertir rangos a porcentaje
            y_min = int(h * zonas[zona_name]['y_range'][0] / 100)
            y_max = int(h * zonas[zona_name]['y_range'][1] / 100)
            x_min = int(w * zonas[zona_name]['x_range'][0] / 100)
            x_max = int(w * zonas[zona_name]['x_range'][1] / 100)
            
            # Dibujar borde
            draw.rectangle(
                [x_min, y_min, x_max, y_max],
                outline=colors[zona_name],
                width=outline_width
            )
            
            # Texto de etiqueta
            try:
                text = f"{zona_name.upper()}"
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                draw.text(
                    (x_min + 5, y_min + 5),
                    text,
                    fill=colors[zona_name],
                    font=font
                )
            except:
                pass
        
        return image
    
    def compute_zone_hashes(self, image, zones=None):
        """
        Generar hashes para las 3 áreas.
        
        Args:
            image: Imagen PIL.
            zones: Config de zonas (opcional).
            
        Returns:
            Dict con hashes por área.
        """
        if zones is None:
            zones = self.config['configuracion_final_3_areas']
        
        if image.mode != 'L':
            image = image.convert('L')
        
        arr = np.array(image)
        hashes = {}
        
        # Definir zonas
        zona_configs = {
            'top_superior': (0, 15, 0, 100),
            'imagen_central': (10, 65, 10, 90),
            'banda_lateral': (0, 100, 0, 25),
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
                    # Aplicar DCT y extraer hash
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
    
    def print_summary(self):
        """Imprimir resumen de las 3 áreas."""
        print("\n" + "="*80)
        print("🦞 ZONAS 3 ÁREAS ESTRATÉGICAS")
        print("="*80)
        
        for i, (zona_name, zona_info) in enumerate(self.config['zonas'].items(), 1):
            print(f"\n{i}. {zona_name.upper()}")
            print(f"   {zona_info['descripcion']}")
            print(f"   Altura: {zona_info['y_range'][0]}%-{zona_info['y_range'][1]}%")
            print(f"   Ancho: {zona_info['x_range'][0]}%-{zona_info['x_range'][1]}%")
            print(f"   Discriminación: {zona_info['propiedad']}")
            print(f"   {zona_info['explicacion']}")
        
        print("\n" + "="*80)
        print("💡 VENTAJAS DE ESTAS 3 ÁREAS:")
        for key, value in self.config['ventajas'].items():
            print(f"   ✅ {value}")
        print("="*80 + "\n")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Zonas 3 Áreas Estratégicas para Clasificación de Cartas VTES',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  
  # Ver resumen de las 3 áreas
  python zonas_3_areas.py --summary
  
  # Visualizar carta con las 3 áreas
  python zonas_3_areas.py --visualize --image carta.png
  
  # Guardar configuración en JSON
  python zonas_3_areas.py --save zonas_3_areas.json
  
        '''
    )
    
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Imprimir resumen de las 3 áreas')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Visualizar carta con overlay de áreas')
    parser.add_argument('--image', '-i', type=str,
                       help='Carta a visualizar')
    parser.add_argument('--save', '-o', type=str, default=None,
                       help='Guardar configuración en JSON')
    
    args = parser.parse_args()
    
    zonas = Zonas3Areas()
    
    print("="*70)
    print("🦞 ZONAS 3 ÁREAS ESTRATÉGICAS")
    print("="*70)
    
    if args.summary:
        # Imprimir resumen
        zonas.print_summary()
        
    elif args.visualize and args.image:
        # Visualizar carta
        print(f"\n📷 Visualizando carta con las 3 áreas estratégicas")
        
        if os.path.exists(args.image):
            image = Image.open(args.image)
            overlay = zonas.draw_zones_3_areas(image)
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
    print("✅ Zonas 3 Áreas listas para uso!")
    print("="*70)


if __name__ == '__main__':
    main()
