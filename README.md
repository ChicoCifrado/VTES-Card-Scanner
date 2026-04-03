# 🦇 Herramienta de detección de cartas VTES 🦇

Extracción automática de datos de cartas para OBS streaming

---

## CRÉDITOS

Esta herramienta es un fork de https://1vcian.github.io/Pokemon-TCGP-Card-Scanner/

---

## Descripción del proyecto

Este proyecto ha sido creado para mejorar el streaming de las finales de torneos VTES y, por lo tanto, mejorar la visibilidad del juego para los espectadores. Para lograrlo, este *plugin de OBS* requiere un mecanismo de detección para emparejar las cartas con sus sets. Estamos usando OpenCV y YOLOv11. La implementación está hecha en C++ para maximizar la compatibilidad con OBS.

Este repositorio usa fuentes públicas y estáticas como:
- https://static.krcg.org/data/vtes.json
- https://static.krcg.org/card/

trainCreator.py crea un conjunto de datos de imágenes que *debería* incluir diferentes ángulos, iluminación, obstáculos, rotación y resolución.

Yo soy el autor de este código, pero no de las imágenes utilizadas. Estas y sus marcas comerciales pertenecen a Paradox Interactive AB, y se usan con permiso bajo el acuerdo Dark Pack.

---

## Estructura del proyecto

- **cartas_vtes/**: Cartas de cartas VTES para generar el dataset
- **background/**: Fondos para las imágenes del dataset
- **trainCreator.py**: Script principal para generar el dataset completo con YOLO
- **trainCreator_mini.py**: Script simplificado que genera 10 imágenes con configuración específica
- **trainCreator_multi.py**: Script de generación paralela optimizado para múltiples procesos
- **dataset/**: Carpeta del dataset generado con subcarpetas para train/val/test
- **vtes-mini/**: Carpeta específica para las imágenes generadas por trainCreator_mini.py

---

## Requisitos del sistema

Para Ubuntu/Debian:
```bash
sudo apt-get install libglib2.0-dev libsm6 libxext6 libxrender-dev libgl1-mesa-glx libglu1-mesa

pip install pillow numpy pyyaml tqdm
```

No se requiere TensorFlow.

---

## Uso

1. **Preparar directorios**: Colocar cartas en `cartas_vtes/` y fondos en `background/`
2. **Generar dataset**:
   - trainCreator.py: Dataset completo para entrenamiento
   - trainCreator_mini.py: Genera 10 imágenes de ejemplo en `vtes-mini/`
   - trainCreator_multi.py: Generación paralela optimizada
3. **Entrenar YOLO**: Usar el dataset generado con YOLOv8/v11

---

## Notas

- Las imágenes se generan en 1080x1080 para máxima calidad
- Cada carta usa factor de escala entre 0.02 y 0.08
- Posiciones totalmente aleatorias sin lógica de rejilla
- Imagen calidad 100 (sin compresión)