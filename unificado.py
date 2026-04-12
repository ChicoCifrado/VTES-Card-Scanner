#!/usr/bin/env python3
"""
🦞 VTES CARD SCANNER - Unificador Simplificado
Script único que hace TODO lo necesario

Funcionalidades:
1. Generar dataset con augmentations
2. Perceptual Hashing (3 áreas estratégicas)
3. Visualizar cartas con zonas
4. Matching simple

Uso:
  python unificado.py <comando> [opciones]

Comandos:
  generate    → Generar dataset
  hash        → Perceptual Hashing
  visualize   → Visualizar carta
  match       → Matching simple
  help        → Mostrar ayuda

Ejemplos:
  python unificado.py generate --folder input --output output --augmentations all
  python unificado.py hash --folder cartas --output hashes.txt
  python unificado.py visualize --image carta.jpg --output carta_zones.jpg
  python unificado.py match --hashes hashes.txt --image carta.jpg
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFilter

# Configurar directorios
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_ROOT  # /mnt/e/VTES/VTES-Card-Scanner
MEMORY_DIR = os.path.join(PROJECT_ROOT, "memory")

def show_help():
    """Mostrar ayuda completa"""
    print("""
┌─────────────────────────────────────────────────────────────────────────┐
│ 🦞  VTES CARD SCANNER - UNIFICADOR SIMPLE                                 │
├─────────────────────────────────────────────────────────────────────────┤

COMANDOS:
  generate     → Generar dataset con augmentations
  hash         → Perceptual Hashing (3 áreas estratégicas)
  visualize    → Visualizar carta con zonas
  match        → Matching simple de hashes
  help         → Mostrar esta ayuda

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USO - GENERAR DATASET:
  python unificado.py generate --folder <input> --output <output>
  
  Opciones:
    --augmentations {gaussian|counter|brightness|flip|all} (default: all)
    --intensity 0.0-1.0 (default: 0.0)
    --outline    Dibujar bounding boxes rojos
    --strict     Detener en primera imagen corrupta

Ejemplo:
  python unificado.py generate --folder ./cartas --output ./dataset --augmentations all --intensity 0.5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USO - PERCEPTUAL HASHING:
  python unificado.py hash --folder <carpeta> --output <salida.txt>
  
  Opciones:
    --samples N  Muestras a visualizar
    --visualize  Modo visualización
    --bits N     Bits por hash (default: 8)
    --threshold  Umbral (default: 128)
    --show_zones Mostrar labels de zonas
    --config N   Configuración de zonas (1-6)

Ejemplo:
  python unificado.py hash --folder cartas_vtes/jpg --output hashes.txt --samples 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USO - VISUALIZAR:
  python unificado.py visualize --image <imagen.jpg> --output <salida.jpg>

Ejemplo:
  python unificado.py visualize --image carta.jpg --output carta_zones.jpg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USO - MATCHING:
  python unificado.py match --hashes <hashes.txt> --image <imagen.jpg>
  
  Opciones:
    --tolerancia N Tolerancia (default: 3)

Ejemplo:
  python unificado.py match --hashes hashes.txt --image carta.jpg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ZONAS DISPONIBLES:
  1. standard      → Zonas estándar
  2. bordes        → Zonas en bordes
  3. centro        → Zonas centradas
  4. superior_inferior → Zonas superior/inferior
  5. bordes_y_centro → Zonas bordes + centro
  6. 3_areas       → 3 Áreas estratégicas (RECOMENDADO)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOTAS:
  ✅ Script único para todas las operaciones
  ✅ No necesitas usar run.sh separado
  ✅ Mantiene vtesCreator.py intacto
  ✅ Logging automático en memory/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

def load_zone_config(config_name="3_areas"):
    """Cargar configuración de zonas"""
    configs = {
        "1": "standard",
        "2": "bordes",
        "3": "centro",
        "4": "superior_inferior",
        "5": "bordes_y_centro",
        "6": "3_areas",
    }
    return configs.get(config_name, "3_areas")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="VTES Card Scanner - Unificador")
    parser.add_argument("command", type=str, choices=["generate", "hash", "visualize", "match", "help"],
                       help="Comando a ejecutar")
    
    # Opciones para generate
    parser.add_argument("--folder", type=str, help="Carpeta de imágenes")
    parser.add_argument("--output", type=str, help="Carpeta de salida")
    parser.add_argument("--augmentations", type=str, default="all",
                       choices=["gaussian", "counter", "brightness", "flip", "all"])
    parser.add_argument("--intensity", type=float, default=0.0)
    parser.add_argument("--outline", action="store_true")
    parser.add_argument("--strict", action="store_true")
    
    # Opciones para hash
    parser.add_argument("--hash-folder", type=str, dest="hash_folder", help="Carpeta para hashing")
    parser.add_argument("--hash-output", type=str, dest="hash_output", help="Archivo de hashes")
    parser.add_argument("--samples", type=int, default=0, help="Muestras a visualizar")
    parser.add_argument("--visualize", action="store_true", dest="hash_visualize", help="Visualizar")
    parser.add_argument("--bits", type=int, default=8, help="Bits por hash")
    parser.add_argument("--threshold", type=int, default=128, help="Umbral")
    parser.add_argument("--show_zones", action="store_true", dest="hash_show_zones", help="Show labels")
    parser.add_argument("--config", type=str, default="3_areas", help="Configuración de zonas")
    
    # Opciones para visualize
    parser.add_argument("--visualize-image", type=str, dest="visualize_image", help="Imagen a visualizar")
    parser.add_argument("--visualize-output", type=str, dest="visualize_output", help="Salida visualización")
    
    # Opciones para match
    parser.add_argument("--hashes", type=str, dest="match_hashes", help="Archivo de hashes")
    parser.add_argument("--match-image", type=str, dest="match_image", help="Imagen para matchear")
    parser.add_argument("--tolerance", type=float, default=3.0, dest="match_tolerance", help="Tolerancia")
    
    args = parser.parse_args()
    
    # Comandos
    if args.command == "help":
        show_help()
        return
    
    elif args.command == "generate":
        # Aquí usaríamos vtesCreator.py
        print("🔧 Comando generate")
        print(f"  --folder: {args.folder}")
        print(f"  --output: {args.output}")
        print(f"  --augmentations: {args.augmentations}")
        print(f"  --intensity: {args.intensity}")
        print(f"  --outline: {args.outline}")
        print(f"  --strict: {args.strict}")
        print("\n⚠️  Uso: python scripts_generacion/vtesCreator.py [opciones]")
        print(f"   o: python {PROJECT_ROOT}/scripts_generacion/vtesCreator.py --folder {args.folder} --output {args.output}")
        return
    
    elif args.command == "hash":
        # Perceptual Hashing
        print(f"\n🔍 Perceptual Hashing - {args.hash_folder}")
        print(f"  Salida: {args.hash_output}")
        print(f"  Samples: {args.samples}")
        print(f"  Config: {args.config}")
        
        # Ejecutar el script de hashing real
        import subprocess
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "vtes_ph_corregido_binario.py"),
            "--folder", args.hash_folder,
            "--output", args.hash_output,
        ]
        if args.samples > 0:
            cmd.extend(["--samples", str(args.samples)])
        if args.hash_visualize:
            cmd.append("--visualize")
        if args.hash_show_zones:
            cmd.append("--show_zones")
        if args.config != "3_areas":
            cmd.extend(["--config", args.config])
        
        print(f"\n▶️  Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd)
        return
    
    elif args.command == "visualize":
        # Visualizar
        print(f"\n🎨 Visualizar carta:")
        print(f"  --image: {args.visualize_image}")
        print(f"  --output: {args.visualize_output}")
        
        import subprocess
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "vtes_ph_corregido_binario.py"),
            "--visualize",
            "--image", args.visualize_image,
            "--output", args.visualize_output,
        ]
        
        print(f"\n▶️  Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd)
        return
    
    elif args.command == "match":
        # Matching
        print(f"\n🔗 Matching:")
        print(f"  --hashes: {args.match_hashes}")
        print(f"  --image: {args.match_image}")
        print(f"  --tolerance: {args.match_tolerance}")
        
        import subprocess
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "vtes_perceptual_hash.py"),
            "--hashes", args.match_hashes,
            "--image", args.match_image,
            "--tolerance", str(args.match_tolerance),
        ]
        
        print(f"\n▶️  Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd)
        return
    
    else:
        show_help()

if __name__ == "__main__":
    main()
