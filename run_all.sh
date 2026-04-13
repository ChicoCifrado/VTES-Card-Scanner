#!/bin/bash
# VTES Card Scanner - Runner Principal
# Unifica todos los scripts en un solo comando

set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🦞 VTES Card Scanner"
echo "📁 Directorio: $SCRIPTS_DIR"
echo ""

# Menú principal
echo "=== MENÚ PRINCIPAL ==="
echo ""
echo "1️⃣  Generar dataset"
echo "2️⃣  Hashing binario"
echo "3️⃣  Hashing banda (biblioteca)"
echo "4️⃣  Matching híbrido"
echo "5️⃣  Contar disciplinas"
echo "6️⃣  Ejecutar todo"
echo "0️⃣  Salir"
echo ""

read -p "Selecciona una opción (0-6): " opcion

case $opcion in
    1)
        echo ""
        echo "📦 Generar dataset..."
        python3 "$SCRIPTS_DIR/generate_dataset.py"
        ;;
    2)
        echo ""
        echo "🔐 Hashing binario..."
        python3 "$SCRIPTS_DIR/vtes_ph_corregido_binario.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        ;;
    3)
        echo ""
        echo "📖 Hashing banda (biblioteca)..."
        python3 "$SCRIPTS_DIR/biblioteca_simple.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        ;;
    4)
        echo ""
        echo "🔍 Matching híbrido..."
        python3 "$SCRIPTS_DIR/sistema_hibrido.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        ;;
    5)
        echo ""
        echo "🎯 Contar disciplinas..."
        python3 "$SCRIPTS_DIR/vtes_discipline_counter_simple.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        ;;
    6)
        echo ""
        echo "🚀 Ejecutando todo..."
        # Generar dataset
        echo "1️⃣ Generar dataset..."
        python3 "$SCRIPTS_DIR/generate_dataset.py"
        
        # Hashing binario
        echo "2️⃣ Hashing binario..."
        python3 "$SCRIPTS_DIR/vtes_ph_corregido_binario.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        
        # Hashing banda
        echo "3️⃣ Hashing banda..."
        python3 "$SCRIPTS_DIR/biblioteca_simple.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        
        # Matching híbrido
        echo "4️⃣ Matching híbrido..."
        python3 "$SCRIPTS_DIR/sistema_hibrido.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        
        # Disciplinas
        echo "5️⃣ Contar disciplinas..."
        python3 "$SCRIPTS_DIR/vtes_discipline_counter_simple.py" --folder "$SCRIPTS_DIR/cartas_vtes/jpg"
        
        echo ""
        echo "✅ ¡Todo completado!"
        ;;
    0)
        echo ""
        echo "👋 Adiós"
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        ;;
esac
