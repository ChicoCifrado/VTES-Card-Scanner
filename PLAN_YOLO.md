# 🦇 Plan de Trabajo: YOLOv11 para VTES-Card-Scanner

## 📋 Objetivos

1. Entrenar YOLOv11 con dataset VTES generado
2. Crear plugin OBS para detección en tiempo real
3. Configurar API para emparejamiento con sets
4. Integración con BSV (futuro)

---

## 🎯 Fase 1: Entrenamiento YOLOv11

### 1. Preparación del Dataset

**Script:** `vtesCreator.py`
```bash
# Generar dataset completo (10000 imágenes)
python3 vtesCreator.py --num 10000

# Estructura:
# vtes-dataset/
# ├── images/
# │   ├── train/    (8000 imágenes)
# │   ├── val/      (1000 imágenes)
# │   └── test/     (1000 imágenes)
# └── bounds.json   (50,000+ bounds)
```

**Formato YOLO:**
- `train/image_{idx:06d}.jpg`
- `train/{filename}.txt` (bounds en formato COCO)
- `bounds.json` con logs reales

### 2. Conversión de bounds a YOLO

**Crear `create_labels.py`:**
```python
import json

with open('bounds.json') as f:
    bounds = json.load(f)

for item in bounds:
    img_name = item['filename']
    bounds_list = item['bounds']
    
    # Crear archivo COCO
    with open(f"images/{img_name.replace('.jpg', '.txt')}", 'w') as f:
        for bound in bounds_list:
            # Formato: x y width height
            x = bound['x'] / 1080
            y = bound['y'] / 1080
            w = bound['width'] / 1080
            h = bound['height'] / 1080
            f.write(f"{x} {y} {w} {h}\n")
```

### 3. Entrenamiento

```bash
# Instalar YOLOv11
pip install ultralytics

# Entrenar con dataset
yolo train model=yolov11n.pt data=vtes-dataset.yaml epochs=100 imgsz=640

# Dataset YAML
# vtes-dataset.yaml:
# path: /mnt/e/VTES/VTES-Card-Scanner/vtes-dataset
# train: images/train
# val: images/val
# names: vtes_card
```

---

## 🎯 Fase 2: Plugin OBS

### 1. Estructura Plugin

```
VTES-Card-Scanner/
├── vtesCreator.py          ← Generador dataset
├── train.py                ← Entrenar YOLOv11
├── create_labels.py        ← Convertir bounds
├── obs_plugin.cpp          ← Plugin OBS
├── obs_plugin.py           ← API Python
├── vtes-dataset/
│   ├── images/
│   └── vtes-dataset.zip
└── README.md
```

### 2. Plugin OBS (C++)

**Características:**
- Source OBS
- Detectar cartas en fuente
- Mostrar bounding boxes
- Overlay en tiempo real

**Ejemplo mínimo:**
```cpp
// obs_plugin.cpp
#include <obs.hpp>

extern "C" {
    OBS_DATA_EXPORT bool obs_data_get(void *data, uint32_t index, obs_data_t **out) {
        obs_data_t *data = (obs_data_t*)obs_source_get_private_data(obs_source_by_id(index));
        obs_data_release(data);
        *out = nullptr;
        return true;
    }
}

void *create(obs_data_t *data) {
    obs_source_t *source = obs_source_create("vtes_source", nullptr, nullptr, nullptr);
    obs_source_set_private_data(source, obs_data_release_ref(data));
    return source;
}

bool destroy(obs_source_t *source) {
    return true;
}
```

### 3. Script Python OBS

```python
# obs_plugin.py
import sys
sys.path.append('..')

import torch
from ultralytics import YOLO

# Cargar modelo
model = YOLO('best.pt')

# Capturar frame
def capture_frame():
    obs_capture = obs.get_source(obs_source_id)
    width, height = obs_source_get_base_res(obs_capture)
    return obs_capture.capture(width, height)

# Detectar
def detect(frame):
    results = model(frame, verbose=False)
    return results

# Renderizar
def render(results):
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            # Dibujar sobre frame
```

---

## 🎯 Fase 3: API VTES

### 1. Endpoints

```
POST /api/vtes/detect
{
  "source": "cartas_vtes",
  "query": "sahana",
  "set": "VTESSet01"
}

POST /api/vtes/empair
{
  "carta": "sahana.jpg",
  "set": "VTESSet01"
}
```

### 2. Implementación

```python
# app.py
from fastapi import FastAPI
import torch

app = FastAPI()

@app.post("/detect")
def detect_vtes(data: dict):
    model = YOLO('best.pt')
    results = model.detect(data['source'])
    return {"detections": results}

@app.post("/empair")
def empair_sets(data: dict):
    # Buscar emparejamiento
    carta = data['carta']
    set_id = data['set']
    
    # Consultar base de datos BSV
    result = database.find_match(carta, set_id)
    return result
```

### 3. Base de Datos BSV

```python
# database.py
from bs_sdk import BSVClient

client = BSVClient()

# Registrar carta
def register_card(card_data):
    tx = client.register(card_data)
    return tx

# Buscar emparejamiento
def find_match(carta, set_id):
    set_tokens = client.get_tokens(set_id)
    card_tokens = client.get_tokens(carta)
    
    # Buscar emparejamiento
    match = [t for t in set_tokens if t.match(card_tokens)]
    return match
```

---

## 🎯 Fase 4: Integración BSV

### 1. Crear Token VTES

```python
from bs_sdk import TokenHandler

# Crear token VTES
token = TokenHandler.create_token(
    name="VTES Card",
    image=card_data['image'],
    metadata={
        "name": card_data['name'],
        "set": set_id
    }
)

# Emitir
token.emit()
```

### 2. Registrar en Blockchain

```python
# Registrar carta en BSV
tx = client.submit(certificate)

# Certificación
cert = Certifier.certify(certificate)
```

---

## 📋 Próximos Pasos (Prioridad)

### 1. Entrenar YOLOv11
- [ ] Generar dataset 10000 imágenes
- [ ] Crear `create_labels.py`
- [ ] Entrenar modelo
- [ ] Evaluar con validation set

### 2. Crear Plugin OBS
- [ ] Crear `obs_plugin.cpp`
- [ ] Configurar compilación
- [ ] Testear en OBS
- [ ] Integrar con fuentes

### 3. API VTES
- [ ] Instalar FastAPI
- [ ] Crear endpoints
- [ ] Integrar con BSV SDK
- [ ] Documentar API

### 4. BSV Integration
- [ ] Crear token VTES
- [ ] Registrar en blockchain
- [ ] Implementar certification
- [ ] Documentar flujo

---

## 🚀 Notas Técnicas

**YOLOv11:**
- `yolov11n.pt` - Nano (más rápido)
- `yolov11s.pt` - Small (balance)
- `yolov11m.pt` - Medium (precisión)

**Multiprocessing:**
- Ya implementado en `vtesCreator.py`
- workers = `cpu_count()`
- Distribución automática 80/10/10

**Bounds:**
- Formato: `x y width height`
- Normalizado: dividir por 1080
- Ratio de aspecto: conservado
