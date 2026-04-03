# VTES-Card-Scanner

VTES Card Scanner es una herramienta de detección de cartas adaptada para el universo de la Guerra de las Galaxias, usando técnicas de visión por computadora y aprendizaje automático.

## Descripción

Fork adaptado de Pokemon TCGP Card Scanner para detección de cartas de VTES utilizando OpenCV y visión por computadora.

VTES es una colección de juegos de estrategia basada en la Guerra de las Galaxias, cada juego tiene sus propias tarjetas únicas que requieren su propio sistema de identificación. Con esta herramienta podrás automatizar el proceso de recopilar y clasificar las cartas de VTES.

## Funcionalidades

- **Detección de Cartas**: Utiliza técnicas de visión por computadora para detectar automáticamente las cartas en imágenes.
- **Entrenamiento Automático**: Incluye un sistema de entrenamiento automático para ajustar el modelo a diferentes tipos de cartas.
- **Resultados En Tiempo Real**: Muestra los resultados de la detección en tiempo real, facilitando la verificación y análisis.

## Tecnologías

- **C++**: Utilizado para la detección de visión y el procesamiento de imágenes.
- **Python**: Para el entrenamiento del modelo y la automatización del proceso de detección.
- **Machine Learning**: Técnicas de aprendizaje automático para mejorar la precisión de la detección.

## Uso

- **Entrenamiento**:
  ```bash
  python train.py
  ```
  Esto generará un modelo de entrenamiento en la carpeta `models`.

- **Detección**:
  ```bash
  python detect.py path/to/image.jpg
  ```
  Reemplaza `path/to/image.jpg` con el camino a la imagen que deseas analizar.

## Contribución

Acerca del proyecto y cómo contribuir puedes visitar la página de GitHub.

## Licencia

Este proyecto está licenciado bajo la MIT License - consulta el archivo LICENSE.md para obtener más detalles.

## Contacto

Si tienes alguna pregunta o problema, no dudes en contactarnos a través de [tu correo electrónico].
