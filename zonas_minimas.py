#!/usr/bin/env python3
"""
Zonas Mínimas para Clasificación de Cartas VTES
=====================================================
Configuración de zonas basada en análisis de 5 cartas:
1. Absolute Tyranny - Biblioteca
2. Aaradhya The Callous Tyrant G6 - Cripta
3. Abyssal Hunter - Biblioteca
4. Academic Hunting Ground - Biblioteca
5. Anarch Salon - Biblioteca

Zonas clave para clasificación:
- ZONA_SUPERIOR: Títulos, set logos, elementos de branding
- ZONA_EDICION: Símbolo de edición (top-right corner)
- ZONA_TIPO_CARTA: Banderas verticales (tipo carta)
- ZONA_CLAN: Símbolo de clan/secta
- ZONA_DISCIPLINAS: Símbolos de disciplinas
- ZONA_ARTE: Ilustración principal (sin texto)
- ZONA_COSTE: Valor de carta (izquierda-abajo)
- ZONA_CAPACIDAD: Poder (derecha-abajo)

ZONAS A IGNORAR:
- ZONA_TEXTO: Texto del cuerpo (imposible leer con ruido)
- ZONA_NUMERO_GRUPO: Demasiado pequeño (<5px)

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw
import argparse


class ZonasMinimasVTES:
    """
    Clases para configurar y usar zonas mínimas óptimas.
    
    Uso básico:
    1. Configurar zonas: config = ZonasMinimasVTES().get_config('vampire')
    2. Visualizar: visualizer.draw_zones(image, zones=config['zones'])
    3. Generar hashes: matcher.compute_zone_hashes(image, config['zones'])
    """
    
    def __init__(self, imagen_muestra=None):
        """
        Inicializar las zonas mínimas.
        
        Args:
            imagen_muestra: Imagen de muestra para ajustar zonas.
        """
        self.imagen_muestra = imagen_muestra
        self.config = self._get_default_config()
    
    def _get_default_config(self):
        """
        Configurar zonas mínimas basadas en el análisis de 5 cartas.
        
        Retorna:
            Diccionario con configuraciones y explicaciones.
        """
        return {
            'nombre': 'Zonas Mínimas VTES',
            'descripcion': 'Zonas clave para clasificación de cartas VTES',
            'version': '1.0',
            'fecha': '2026-04-12',
            
            'zonas': {
                # ZONA 1: TÍTULO + SET LOGO (Superior)
                'titulo_set': {
                    'descripcion': 'Título, set name, logos del set',
                    'y_range': (0, 15),       # 0-15% de altura
                    'x_range': (0, 100),     # Todo el ancho
                    'discriminacion': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Identifica el set y versión mediante título y logos distintivos'
                },
                
                # ZONA 2: SÍMBOLO EDICIÓN (Esquina superior derecha)
                'simbolo_edicion': {
                    'descripcion': 'Símbolo de edición en esquina superior derecha',
                    'y_range': (0, 12),       # 0-12% de altura
                    'x_range': (88, 100),    # 88-100% de ancho (derecha)
                    'discriminacion': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Diferencia entre ediciones antiguas y modernas'
                },
                
                # ZONA 3: TIPO DE CARTA (Izquierda vertical)
                'tipo_carta': {
                    'descripcion': 'Banderas verticales que indican tipo de carta',
                    'y_range': (15, 45),      # 15-45% de altura
                    'x_range': (0, 15),       # 0-15% de ancho (izquierda)
                    'discriminacion': 'MEDIA',
                    'clave_clasificacion': True,
                    'explicacion': 'Colores: verde=Master, rojo/etc. Identifica subtipo de carta'
                },
                
                # ZONA 4: CLAN/SECTA (Izquierda)
                'clan_secta': {
                    'descripcion': 'Símbolo de clan o secta requerida',
                    'y_range': (45, 70),      # 45-70% de altura
                    'x_range': (0, 25),       # 0-25% de ancho (izquierda)
                    'discriminacion': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Símbolo único por clan, diferencia sets del mismo clan'
                },
                
                # ZONA 5: DISCIPLINAS (Izquierda central-abajo)
                'disciplinas': {
                    'descripcion': 'Símbolos de disciplinas (2 símbolos)',
                    'y_range': (70, 85),      # 70-85% de altura
                    'x_range': (0, 20),       # 0-20% de ancho (izquierda)
                    'discriminacion': 'MEDIA',
                    'clave_clasificacion': True,
                    'explicacion': 'Cuadrado=básico, rombo=avanzado. Indica nivel de carta'
                },
                
                # ZONA 6: ARTE (Centro superior)
                'arte': {
                    'descripcion': 'Ilustración principal (sin texto)',
                    'y_range': (8, 60),       # 8-60% de altura
                    'x_range': (10, 90),      # 10-90% de ancho (centro)
                    'discriminacion': 'MUY ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Visualmente distintivo entre sets. NO incluir texto'
                },
                
                # ZONA 7: COSTE (Abajo izquierda)
                'coste': {
                    'descripcion': 'Coste de vida/sangre (rombo/blanco o gota/rojo)',
                    'y_range': (82, 92),      # 82-92% de altura
                    'x_range': (0, 15),       # 0-15% de ancho (izquierda)
                    'discriminacion': 'MEDIA',
                    'clave_clasificacion': True,
                    'explicacion': 'Símbolo de vida (rombo) o sangre (gota). Muy distintivo'
                },
                
                # ZONA 8: CAPACIDAD (Abajo derecha)
                'capacidad': {
                    'descripcion': 'Capacidad del vampiro (círculo rojo)',
                    'y_range': (85, 95),      # 85-95% de altura
                    'x_range': (85, 100),     # 85-100% de ancho (derecha)
                    'discriminacion': 'ALTA',
                    'clave_clasificacion': True,
                    'explicacion': 'Indica poder de la carta. Distintivo visualmente'
                },
                
                # ZONA A IGNORAR: TEXTO (Centro inferior)
                'texto': {
                    'descripcion': 'TEXTO DE LA CARTA (NO USAR)',
                    'y_range': (5, 88),       # 5-88% de altura (cubre todo centro)
                    'x_range': (10, 90),      # 10-90% de ancho
                    'discriminacion': 'BAJA',
                    'clave_clasificacion': False,
                    'explicacion': 'NO INCLUIR: Imposible leer con baja resolución y ruido'
                },
                
                # ZONA A IGNORAR: NÚMERO GRUPO (Muy pequeño)
                'numero_grupo': {
                    'descripcion': 'NÚMERO DE GRUPO (NO USAR)',
                    'y_range': (65, 75),      # 65-75% de altura
                    'x_range': (5, 10),       # 5-10% de ancho (muy pequeño)
                    'discriminacion': 'BAJÍSIMA',
                    'clave_clasificacion': False,
                    'explicacion': 'NO INCLUIR: Demasiado pequeño (<5px), imperceptible'
                },
            },
            
            # Configuración recomendada para producción
            'configuracion_recomendada': {
                'zonas': {
                    'titulo_set': {
                        'y_range': (0, 15),
                        'x_range': (0, 100)
                    },
                    'simbolo_edicion': {
                        'y_range': (0, 12),
                        'x_range': (88, 100)
                    },
                    'tipo_carta': {
                        'y_range': (15, 45),
                        'x_range': (0, 15)
                    },
                    'clan_secta': {
                        'y_range': (45, 70),
                        'x_range': (0, 25)
                    },
                    'disciplinas': {
                        'y_range': (70, 85),
                        'x_range': (0, 20)
                    },
                    'arte': {
                        'y_range': (8, 60),
                        'x_range': (10, 90)
                    },
                    'coste': {
                        'y_range': (82, 92),
                        'x_range': (0, 15)
                    },
                    'capacidad': {
                        'y_range': (85, 95),
                        'x_range': (85, 100)
                    },
                },
                'ignorar': ['texto', 'numero_grupo'],
                'configuracion_final': {
                    'borde_superior': (0, 15, 0, 100),       # Títulos + set logos
                    'simbolo_edicion': (0, 12, 88, 100),     # Símbolo edición (top-right)
                    'tipo_carta': (15, 45, 0, 15),           # Banderas tipo carta
                    'clan_secta': (45, 70, 0, 25),           # Símbolo clan/secta
                    'disciplinas': (70, 85, 0, 20),          # Símbolos disciplinas
                    'arte': (8, 60, 10, 90),                  # Ilustración principal
                    'coste': (82, 92, 0, 15),                 # Coste vida/sangre
                    'capacidad': (85, 95, 85, 100),           # Capacidad vampiro
                }
            },
            
            # Configuración simplificada (solo zonas clave)
            'configuracion_simplificada': {
                'descripcion': 'Solo las zonas más discriminantes para clasificación rápida',
                'zonas': {
                    'titulo_set': (0, 15, 0, 100),           # Títulos + logos
                    'simbolo_edicion': (0, 12, 88, 100),     # Símbolo edición
                    'arte': (8, 60, 10, 90),                  # Ilustración (más distintivo)
                    'clan_secta': (45, 70, 0, 25),           # Símbolo clan
                }
            }
        }
    
    def get_zona_description(self, zona_name):
        """
        Obtener descripción de una zona.
        
        Args:
            zona_name: Nombre de la zona ('titulo_set', 'arte', etc.)
            
        Returns:
            Descripción de la zona.
        """
        return self.config['zonas'].get(zona_name, {}).get('descripcion', '')
    
    def get_zona_info(self, zona_name):
        """
        Obtener información completa de una zona.
        
        Args:
            zona_name: Nombre de la zona.
            
        Returns:
            Dict con información de la zona.
        """
        return self.config['zonas'].get(zona_name, {})
    
    def save_config(self, output_path=None):
        """
        Guardar configuración de zonas en archivo JSON.
        
        Args:
            output_path: Ruta para guardar archivo (opcional).
            
        Returns:
            Ruta del archivo guardado.
        """
        config_json = {
            'nombre': self.config['nombre'],
            'version': self.config['version'],
            'fecha': self.config['fecha'],
            'descripcion': self.config['descripcion'],
            'zonas': self.config['zonas'],
            'configuracion_recomendada': self.config['configuracion_recomendada']['configuracion_final'],
            'configuracion_simplificada': self.config['configuracion_simplificada']['zonas'],
        }
        
        if output_path is None:
            output_path = 'zones_minimas.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_json, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def print_zone_summary(self):
        """
        Imprimir resumen de todas las zonas.
        """
        print("\n" + "="*80)
        print("🦞 ZONAS MÍNIMAS PARA CLASIFICACIÓN DE CARTAS VTES")
        print("="*80)
        
        for zona_name, zona_info in self.config['zonas'].items():
            print(f"\n📍 {zona_name.upper()}")
            print(f"   {zona_info['descripcion']}")
            print(f"   Altura: {zona_info['y_range'][0]}%-{zona_info['y_range'][1]}%")
            print(f"   Ancho: {zona_info['x_range'][0]}%-{zona_info['x_range'][1]}%")
            print(f"   Discriminación: {zona_info['discriminacion']}")
            print(f"   Clave para clasificación: {'✅' if zona_info['clave_clasificacion'] else '❌'}")
            if zona_info.get('explicacion'):
                print(f"   {zona_info['explicacion']}")
        
        print("\n" + "="*80)
        print("💡 RECOMENDACIÓN: Usar configuración_recomendada para producción")
        print("💡 RÁPIDO: Usar configuracion_simplificada para clasificación rápida")
        print("="*80 + "\n")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Zonas Mínimas para Clasificación de Cartas VTES',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  
  # Ver resumen de zonas
  python zonas_minimas.py --summary
  
  # Guardar configuración en JSON
  python zonas_minimas.py --save zones_minimas.json
  
  # Ver descripción de zona específica
  python zonas_minimas.py --info tipo_carta
  
  # Configurar para set específico (ej: Vampire)
  python zonas_minimas.py --set vampire
  
        '''
    )
    
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Imprimir resumen de todas las zonas')
    parser.add_argument('--info', '-i', type=str,
                       help='Información detallada de zona específica')
    parser.add_argument('--save', '-o', type=str, default=None,
                       help='Guardar configuración en archivo JSON')
    parser.add_argument('--set', '-t', type=str, default=None,
                       help='Configurar para set específico')
    
    args = parser.parse_args()
    
    # Crear instancia
    zonas = ZonasMinimasVTES()
    
    if args.info:
        # Mostrar info de zona específica
        zona_info = zonas.get_zona_info(args.info)
        print(f"📍 ZONA: {args.info.upper()}")
        print(f"   {zona_info.get('descripcion', 'Sin descripción')}")
        print(f"   Altura: {zona_info.get('y_range', 'N/A')[0]}%-{zona_info.get('y_range', 'N/A')[1]}%")
        print(f"   Ancho: {zona_info.get('x_range', 'N/A')[0]}%-{zona_info.get('x_range', 'N/A')[1]}%")
        print(f"   Discriminación: {zona_info.get('discriminacion', 'N/A')}")
        
    elif args.save:
        # Guardar configuración
        output_path = zonas.save_config(args.save)
        print(f"💾 Configuración guardada en: {output_path}")
        
    elif args.set:
        print(f"⚠️  Configuración para set '{args.set}' no implementada aún.")
        print(f"   Las zonas son generales para todos los sets.")
        
    elif args.summary:
        # Imprimir resumen
        zonas.print_zone_summary()
        
    else:
        parser.print_help()
    
    return zonas


if __name__ == '__main__':
    main()
