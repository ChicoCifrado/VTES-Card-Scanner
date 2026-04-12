#!/bin/bash
# 🦞 VTES Card Scanner - Launcher Simplificado
# Unifica todas las operaciones en un único script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
    generate)
        # Generar dataset con vtes_complete.py
        python3 vtes_complete.py --num "${2:-100}" \
            --with_aug \
            --outline \
            --intensity "${3:-0.5}"
        ;;
    hash)
        # Generar hashes perceptuales
        python3 vtes_hashing_simple.py hash \
            --folder cartas_vtes/jpg \
            --output vtes_hashes.txt
        ;;
    match)
        # Matching de cartas
        python3 vtes_matching.py \
            --hashes vtes_hashes.txt \
            --cluster "${2:-0}"
        ;;
    test)
        # Prueba rápida (10 imágenes)
        echo "🧪 Prueba rápida de VTES Card Scanner"
        python3 vtes_complete.py --num 10 \
            --with_aug \
            --outline \
            --intensity 0.5
        ;;
    help|-h|--help)
        echo "🦞 VTES Card Scanner - Unificado"
        echo ""
        echo "Uso: $0 {generate|hash|match|test}"
        echo ""
        echo "Comandos:"
        echo "  generate [num] [intensity]  Generar dataset"
        echo "                                num: 10, 100, 1000, 10000"
        echo "                                intensity: 0.0-1.0"
        echo ""
        echo "  hash                         Generar hashes perceptuales"
        echo "                                de todas las cartas"
        echo ""
        echo "  match [tolerance]            Matching de cartas similares"
        echo "                                tolerance: 0-255 (default: 0)"
        echo ""
        echo "  test                         Prueba rápida (10 imágenes)"
        echo ""
        echo "  help                         Esta ayuda"
        echo ""
        echo "Ejemplos:"
        echo "  $0 generate 100 0.5         Generar 100 imágenes al 50%"
        echo "  $0 hash                      Generar hashes de todas las cartas"
        echo "  $0 match                     Encontrar cartas similares"
        echo "  $0 test                      Prueba rápida"
        ;;
esac
