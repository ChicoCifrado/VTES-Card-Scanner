#!/bin/bash
# 🦞 VTES Card Scanner - Launcher Central
# Script centralizado para ejecutar todos los scripts del proyecto
# Autor: La Garra Cifrada 🦞
# Fecha: 2026-04-12

# Configuración
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="$PROJECT_ROOT/memory"
LOG_FILE="$MEMORY_DIR/launcher.log"

# Crear memoria si no existe
mkdir -p "$MEMORY_DIR"
touch "$LOG_FILE"

# Función para registrar log
log_msg() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $msg" >> "$LOG_FILE"
    echo "$msg"
}

# Función para mostrar banner
show_banner() {
    cat << 'EOF'
┌─────────────────────────────────────────────────────────────────────────┐
│ 🦞  VTES CARD SCANNER - LAUNCHER CENTRAL                                │
│                              by La Garra Cifrada                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Estructura organizada y centralizada para el proyecto VTES Card        │
│                                                                          
│  📁  Directorios:                                                        │
│    ├─ scripts_generacion/   → Scripts de generación de dataset          │
│    ├─ scripts_hashing/      → Scripts de perceptual hashing              │
│    ├─ eliminados/           → Scripts obsoletos                          │
│    └─ memory/               → Log de progreso y checkpoints               │
│                                                                          
│  📊  Scripts disponibles:                                                 │
│    ├─ Generación de Dataset: vtesCreator.py                              │
│    ├─ Perceptual Hashing:  vtes_ph_corregido_binario.py                  │
│    ├─ Matching:            vtes_perceptual_hash.py                        │
│    └─ Configuración:       zonas_3_areas.json                            │
└─────────────────────────────────────────────────────────────────────────┘

EOF
}

# Función para mostrar información de scripts
show_scripts_info() {
    cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚  INFORMACIÓN DE SCRIPTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  GENERACIÓN DE DATASET
   Archivo: vtesCreator.py
   Ubicación: scripts_generacion/
   
   📋  Parámetros:
   --folder        Carpeta de imágenes de entrada
   --output        Carpeta de salida
   --augmentations gaussian|counter|brightness|flip|all
   --intensity     Intensidad de augmentations (0.0-1.0)
   --outline       Dibujar bounding boxes rojos
   --strict        Detener en primera imagen corrupta
   
   📝  Uso:
   python scripts_generacion/vtesCreator.py --folder <input> --output <output>
   
   💡  Ejemplo:
   python scripts_generacion/vtesCreator.py \
     --folder /ruta/cartas_originales \
     --output /ruta/dataset \
     --augmentations all --intensity 0.5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣  PERCEPTUAL HASHING (CORREGIDO)
   Archivo: vtes_ph_corregido_binario.py
   
   📋  Parámetros:
   --folder        Carpeta de imágenes
   --output        Archivo de salida (.txt)
   --image        Imagen individual para visualizar
   --visualize    Modo visualización
   --samples      Muestras a visualizar
   --bits         Bits por hash (default: 8)
   --threshold    Umbral de binarización (default: 128)
   --show_zones   Mostrar labels de zonas
   
   📝  Uso:
   python vtes_ph_corregido_binario.py --folder <carpeta> --output <salida>
   
   💡  Ejemplo:
   python vtes_ph_corregido_binario.py \
     --folder cartas_vtes/jpg \
     --output vtes_hashes.txt \
     --samples 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣  MATCHING SIMPLE
   Archivo: vtes_perceptual_hash.py
   
   📋  Parámetros:
   --hashes       Archivo de hashes
   --image        Imagen para matchear
   --tolerance    Tolerancia de matching (default: 3)
   
   📝  Uso:
   python vtes_perceptual_hash.py --hashes <hashes.txt> --image <img.jpg>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣  CONFIGURACIÓN DE ZONAS
   Archivo: zonas_3_areas.json
   
   📋  Zonas disponibles:
   - standard      → Zonas estándar
   - bordes        → Zonas en bordes
   - centro        → Zonas centradas
   - superior_inferior → Zonas superior/inferior
   - bordes_y_centro → Zonas bordes + centro
   - 3_areas       → 3 Áreas estratégicas (recomendado)
   
   📝  Uso:
   python vtes_ph_corregido_binario.py --config 3_areas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
}

# Función para ejecutar script
run_script() {
    local script="$1"
    local params="$2"
    
    case "$script" in
        "1_generate_dataset")
            if [ -n "$params" ]; then
                python "$PROJECT_ROOT/scripts_generacion/vtesCreator.py" $params
            else
                echo "❌ Falta: --folder --output"
                echo ""
                echo "Uso: python scripts_generacion/vtesCreator.py --folder <input> --output <output>"
            fi
            ;;
        "2_perceptual_hashing")
            if [ -n "$params" ]; then
                python "$PROJECT_ROOT/vtes_ph_corregido_binario.py" $params
            else
                echo "❌ Falta: --folder --output"
                echo ""
                echo "Uso: python vtes_ph_corregido_binario.py --folder <carpeta> --output <salida>"
            fi
            ;;
        "3_matching")
            if [ -n "$params" ]; then
                python "$PROJECT_ROOT/vtes_perceptual_hash.py" $params
            else
                echo "❌ Falta: --hashes --image"
                echo ""
                echo "Uso: python vtes_perceptual_hash.py --hashes <hashes.txt> --image <img.jpg>"
            fi
            ;;
        "4_visualizar")
            if [ -n "$params" ]; then
                python "$PROJECT_ROOT/vtes_ph_corregido_binario.py --visualize" $params
            else
                echo "❌ Falta: --image --output"
                echo ""
                echo "Uso: python vtes_ph_corregido_binario.py --visualize --image <img.jpg> --output <salida.jpg>"
            fi
            ;;
        "5_configuracion")
            echo ""
            echo "📋 Configuraciones de zonas disponibles:"
            echo ""
            echo "1) standard      → Zonas estándar"
            echo "2) bordes        → Zonas en bordes"
            echo "3) centro        → Zonas centradas"
            echo "4) superior_inferior → Zonas superior/inferior"
            echo "5) bordes_y_centro → Zonas bordes + centro"
            echo "6) 3_areas       → 3 Áreas estratégicas (recomendado)"
            echo ""
            read -p "Seleccionar configuración (1-6): " config
            echo ""
            echo "Usando configuración: $config"
            echo ""
            ;;
        "6_documentacion")
            show_scripts_info
            ;;
        "7_salir")
            echo ""
            echo "👋 Adios! Hasta pronto."
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Script no encontrado: $script"
            echo ""
            echo "Uso: run <numero_script> [parametros]"
            echo ""
            ;;
    esac
}

# Función principal del menú principal
main_menu() {
    echo ""
    echo "🔍  Seleccione una opción:"
    echo ""
    echo "1️⃣  Generar dataset con vtesCreator.py"
    echo "2️⃣  Perceptual Hashing (CORREGIDO)"
    echo "3️⃣  Matching de cartas"
    echo "4️⃣  Visualizar carta con zonas"
    echo "5️⃣  Configurar zonas"
    echo "6️⃣  Ver documentación de scripts"
    echo "7️⃣  Salir"
    echo ""
    read -p "👉 Opción: " opcion
    echo ""
    
    case "$opcion" in
        "1")
            echo ""
            echo "📦  GENERACIÓN DE DATASET"
            echo ""
            echo "Parámetros requeridos:"
            echo "  --folder      Carpeta de imágenes"
            echo "  --output      Carpeta de salida"
            echo ""
            echo "Parámetros opcionales:"
            echo "  --augmentations gaussian|counter|brightness|flip|all"
            echo "  --intensity     Intensidad (0.0-1.0)"
            echo "  --outline       Dibujar bounding boxes"
            echo "  --strict        Detener en primera imagen corrupta"
            echo ""
            echo "Escriba los parámetros (ej: --folder input --output output --augmentations all --intensity 0.5)"
            read -p "👉 Parámetros: " params
            run_script "1_generate_dataset" "$params"
            ;;
        "2")
            echo ""
            echo "🔍  PERCEPTUAL HASHING"
            echo ""
            echo "Parámetros requeridos:"
            echo "  --folder      Carpeta de imágenes"
            echo "  --output      Archivo de salida (.txt)"
            echo ""
            echo "Parámetros opcionales:"
            echo "  --samples      Muestras a visualizar"
            echo "  --visualize    Modo visualización"
            echo "  --bits         Bits por hash (default: 8)"
            echo "  --threshold    Umbral (default: 128)"
            echo "  --show_zones   Mostrar labels"
            echo ""
            echo "Escriba los parámetros (ej: --folder cartas_vtes/jpg --output hashes.txt --samples 2)"
            read -p "👉 Parámetros: " params
            run_script "2_perceptual_hashing" "$params"
            ;;
        "3")
            echo ""
            echo "🔗  MATCHING"
            echo ""
            echo "Parámetros requeridos:"
            echo "  --hashes      Archivo de hashes"
            echo "  --image       Imagen para matchear"
            echo ""
            echo "Escriba los parámetros (ej: --hashes hashes.txt --image carta.jpg)"
            read -p "👉 Parámetros: " params
            run_script "3_matching" "$params"
            ;;
        "4")
            echo ""
            echo "🎨  VISUALIZAR CARTA"
            echo ""
            echo "Parámetros requeridos:"
            echo "  --image       Imagen individual"
            echo "  --output      Archivo de salida"
            echo ""
            echo "Escriba los parámetros (ej: --image carta.jpg --output carta_zones.jpg)"
            read -p "👉 Parámetros: " params
            run_script "4_visualizar" "$params"
            ;;
        "5")
            echo ""
            echo "📐  CONFIGURACIÓN DE ZONAS"
            echo ""
            echo "Configuraciones disponibles:"
            echo "1) standard      → Zonas estándar"
            echo "2) bordes        → Zonas en bordes"
            echo "3) centro        → Zonas centradas"
            echo "4) superior_inferior → Zonas superior/inferior"
            echo "5) bordes_y_centro → Zonas bordes + centro"
            echo "6) 3_areas       → 3 Áreas estratégicas (recomendado)"
            echo ""
            read -p "👉 Configuración (1-6): " config
            echo ""
            echo "Usando: $config"
            ;;
        "6")
            show_scripts_info
            ;;
        "7")
            echo ""
            echo "👋 Adios! Hasta pronto."
            exit 0
            ;;
        *)
            echo "❌ Opción inválida"
            ;;
    esac
}

# Verificar si se pasó un parámetro para ejecución directa
if [ $# -eq 2 ]; then
    run_script "$1" "$2"
else
    # Mostrar banner y ejecutar menú
    show_banner
    main_menu
fi
