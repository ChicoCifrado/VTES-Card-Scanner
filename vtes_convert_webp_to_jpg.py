#!/usr/bin/env python3
"""
Convertidor masivo de .webp a .jpg
=====================================================
Convierte TODAS las cartas VTES de .webp a .jpg
para procesarlas con PIL normalmente.

Uso:
  python vtes_convert_webp_to_jpg.py --folder cartas_vtes --output jpg
  python vtes_convert_webp_to_jpg.py --all --source /mnt/e/VTES/VTES-Card-Scanner/cartas_vtes --dest /mnt/e/VTES/VTES-Card-Scanner/cartas_vtes/jpg

Autor: La Garra Cifrada 🦞
Fecha: 2026-04-12
"""

import os
import sys
from PIL import Image


def convert_webp_to_jpg(webp_path, jpg_path):
    """
    Convertir .webp a .jpg.
    
    Args:
        webp_path: Ruta al archivo .webp.
        jpg_path: Ruta de salida para el JPG.
        
    Returns:
        True si exitó, False si falló.
    """
    try:
        # Abrir imagen
        img = Image.open(webp_path)
        
        # Eliminar alpha channel si existe
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode == 'LA':
            img = img.convert('RGB')
        elif img.mode == 'P':
            img = img.convert('RGB')
        elif img.mode in ['RGB', 'L']:
            pass  # Ya es compatible
        
        # Guardar como JPG
        img.save(jpg_path, 'JPEG', quality=95)
        img.close()
        
        return True
        
    except Exception as e:
        print(f"  ⚠️ Fallo en {os.path.basename(webp_path)}: {type(e).__name__}")
        return False


def convert_all_webp_to_jpg(source_folder, dest_folder=None, dry_run=False):
    """
    Convertir todos los archivos .webp en una carpeta a JPG.
    
    Args:
        source_folder: Carpeta de origen.
        dest_folder: Carpeta de destino (si None, usar subcarpeta jpg en misma ubicación).
        dry_run: Solo mostrar qué se convertiría.
        
    Returns:
        Dict con estadísticas.
    """
    if dest_folder is None:
        dest_folder = os.path.join(source_folder, 'jpg')
    
    # Crear directorio de destino si no existe
    if not dry_run:
        os.makedirs(dest_folder, exist_ok=True)
    
    # Buscar archivos .webp
    webp_files = []
    for filename in os.listdir(source_folder):
        if filename.lower().endswith('.webp'):
            webp_path = os.path.join(source_folder, filename)
            webp_files.append(webp_path)
    
    print(f"\n📂 Carpeta origen: {source_folder}")
    print(f"💾 Carpeta destino: {dest_folder}")
    print(f"🔍 Encontradas {len(webp_files)} imágenes .webp")
    
    # Estadísticas
    converted = 0
    failed = 0
    
    for webp_path in webp_files:
        # Generar nombre JPG manteniendo prefijo y número
        base_name = os.path.splitext(os.path.basename(webp_path))[0]
        jpg_path = os.path.join(dest_folder, base_name + '.jpg')
        
        # Si ya existe JPG, saltar
        if os.path.exists(jpg_path):
            continue
        
        if dry_run:
            print(f"  🔀 {os.path.basename(webp_path)} → {os.path.basename(jpg_path)}")
            converted += 1
            continue
        
        # Convertir
        success = convert_webp_to_jpg(webp_path, jpg_path)
        
        if success:
            converted += 1
            print(f"  ✅ {os.path.basename(webp_path)} → {os.path.basename(jpg_path)}")
        else:
            failed += 1
    
    # Estadísticas finales
    print(f"\n  📊 Estadísticas:")
    print(f"     Total .webp: {len(webp_files)}")
    print(f"     Convertidos: {converted}")
    print(f"     Ya JPG: {len(webp_files) - converted - failed}")
    print(f"     Fallidos: {failed}")
    
    return {
        'total': len(webp_files),
        'converted': converted,
        'failed': failed,
    }


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convertidor masivo de .webp a .jpg',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  
  # Convertir en misma carpeta (subcarpeta jpg)
  python vtes_convert_webp_to_jpg.py --folder cartas_vtes
  
  # Convertir a carpeta específica
  python vtes_convert_webp_to_jpg.py --folder cartas_vtes --output jpg
  
  # Convertir desde /mnt/e/VTES/VTES-Card-Scanner/
  python vtes_convert_webp_to_jpg.py --folder /mnt/e/VTES/VTES-Card-Scanner/cartas_vtes --dest /mnt/e/VTES/VTES-Card-Scanner/cartas_vtes/jpg
  
        '''
    )
    
    parser.add_argument('--folder', '-f', type=str, required=True,
                       help='Carpeta con archivos .webp')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Carpeta de salida (si None, subcarpeta jpg en misma ubicación)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Solo mostrar qué se convertiría')
    parser.add_argument('--all', '-a', action='store_true', default=True,
                       help='Convertir todos los .webp')
    parser.add_argument('--source', '-s', type=str, default=None,
                       help='Carpeta de origen (si no --source, usa --folder)')
    parser.add_argument('--dest', '-d', type=str, default=None,
                       help='Carpeta de destino (si no --dest, usa --output)')
    
    args = parser.parse_args()
    
    # Determinar rutas
    source = args.source or args.folder
    dest = args.dest or args.output
    
    if dest is None:
        # Subcarpeta jpg en misma ubicación
        dest = os.path.join(source, 'jpg')
    
    # Convertir
    if not args.dry_run:
        stats = convert_all_webp_to_jpg(source, dest_folder=dest)
    else:
        # Solo mostrar qué se convertiría
        webp_files = []
        for filename in os.listdir(source):
            if filename.lower().endswith('.webp'):
                webp_files.append(filename)
        print(f"  🔍 Encontradas {len(webp_files)} imágenes .webp que se convertirían")
    
    # Guardar estadísticas
    if not args.dry_run:
        stats_path = os.path.join(dest, 'conversion_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\n  💾 Estadísticas guardadas en: {stats_path}")
    
    return stats


if __name__ == '__main__':
    main()
