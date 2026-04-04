# 🦇 VTES Card Detection

Extracción automática de datos de cartas para OBS streaming

---

## CRÉDITOS

Esta herramienta es un fork de [Pokemon-TCGP-Card-Scanner](https://1vcian.github.io/Pokemon-TCGP-Card-Scanner/)

---

## Descripción del proyecto

Este proyecto ha sido creado para mejorar el streaming de las finales de torneos VTES y, por lo tanto, mejorar la visibilidad del juego para los espectadores. Para lograrlo, este plugin de OBS requiere un mecanismo de detección para emparejar las cartas con sus sets. Estamos usando OpenCV y YOLOv11. La implementación está hecha en C++ para maximizar la compatibilidad con OBS.

Este repositorio usa fuentes públicas y estáticas como:
- https://static.krcg.org/data/vtes.json
- https://static.krcg.org/card/

---

## ÚNICO SCRIPT: vtesCreator.py

Único script necesario para generar dataset con:
- Multiprocessing automático
- Bounds con attached (colisiones ≥10%)
- Ratio de aspecto conservado
- Distribución automática 80/10/10
- Generación de labels YOLO (formato COCO)
- Comprimir en ZIP

---

## Estructura del proyecto

- **cartas_vtes/**: Cartas VTES para generar el dataset
- **fondos_vtes/**: Fondos para las imágenes del dataset
- **vtes-dataset/**: Carpeta del dataset generado con subcarpetas para train/val/test
- **labels/**: Labels YOLO en formato COCO

---

## Uso

```bash
# Generar dataset (1, 10, 1000 o 10000 imágenes)
python3 vtesCreator.py --num 1000

# Generar dataset secuencial
python3 vtesCreator.py --num 1000 --sequential
```

**Parámetros:**
- `--num {1,10,1000,10000}`: Número de imágenes
- `--sequential`: Modo secuencial (sin multiprocessing)

**Output:**
- Imágenes en `vtes-dataset/images/{train,val,test}/`
- Labels en formato YOLO: `images/*.txt`
- `bounds.json`: Relaciones con attached
- `vtes-dataset.zip`: Dataset comprimido

---

## Requisitos del sistema

Para Ubuntu/Debian:
```bash
sudo apt-get install libglib2.0-dev libsm6 libxext6 libxrender-dev libgl1-mesa-glx libglu1-mesa

pip install pillow numpy pyyaml tqdm
```

---

## Notas

- Las imágenes se generan en 1080x1080 para máxima calidad
- Cada carta usa factor de escala entre 0.02 y 0.08
- Posiciones totalmente aleatorias sin lógica de rejilla
- Imagen calidad 100 (sin compresión)
- Multiprocessing con `cpu_count()` workers
- Cartas con ratio de aspecto conservado
- Attached detection (≥10% overlap)

---

## Licencia

Estas y sus marcas comerciales pertenecen a Paradox Interactive AB, y se usan con permiso bajo el acuerdo Dark Pack.
