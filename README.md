# 🦞 README VTES Card Scanner

## 📊 Proyecto VTES Card Scanner

Detección de cartas VTES con hashing perceptual y matching.

---

## ✅ ESTADO ACTUAL

### 🎯 Proyectos Completados

1. ✅ **Dataset generado**: 4156 cartas con augmentations
2. ✅ **Hashing completado**: 12468 hashes binarios
3. ✅ **Dataset limpio**: test/, val/, train/, augmented/
4. ✅ **Matching funcional**: vtes_perceptual_hash.py

### 📁 Estructura del Proyecto

```
VTES-Card-Scanner/
├── vtes_unificado.py              ← TODO en un script
├── run_simple.sh                  ← Launcher simplificado
├── vtes_perceptual_hash.py        ← Matching
├── vtesCreator.py                 ← Referencia (NO TOCAR)
├── cartas_vtes/jpg/               ← 4156 imágenes
├── fondos_vtes/                   ← Fondos
├── vtes-dataset/
│   ├── test/                     ← 10 imágenes
│   ├── val/
│   ├── train/
│   ├── augmented/
│   └── bounds.json
└── corrupted_images.txt           ← Vacío (0 corruptas)
```

---

## 🧪 COMANDOS

### Generar dataset:
```bash
# Pequeño (10 imágenes)
./run_simple.sh generate 10

# Grande (1000 imágenes)
./run_simple.sh generate 1000 --intensity 0.5
```

### Generar hashes:
```bash
./run_simple.sh hash
```

### Matching:
```bash
# Exacto (tolerancia 0)
./run_simple.sh match

# Similar (tolerancia 15)
./run_simple.sh match 15
```

### Prueba rápida:
```bash
./run_simple.sh test
```

---

## 📊 RESULTADOS

| Métrica | Valor |
|---------|-------|
| Cartas procesadas | 4156 |
| Válidas | 4156 (100%) |
| Corruptas | 0 |
| Hashes generados | 12468 |
| Dataset generado | Sí |

---

## 🚀 PRÓXIMOS PASOS

### 1️⃣ Matching masivo
```bash
./run_simple.sh match
```

### 2️⃣ Subir a la nube
```bash
rsync -avz --progress \
    cartas_vtes/jpg/ \
    fondos_vtes/ \
    usuario@servidor:/ruta/remota/
```

### 3️⃣ Subir a GitHub
```bash
git add .
git commit -m "Hashing completado"
git push
```

---

## 📝 COMENTARIOS DE USO

### Generar dataset:
- `generate [num] [intensity]`: Generar dataset
- `num`: Número de imágenes (10, 100, 1000, 10000)
- `intensity`: Intensidad augmentations (0.0-1.0)

### Hashing:
- `hash`: Generar hashes de todas las cartas
- Método: AVG POOLING + BINARIZACIÓN (umbral 128)

### Matching:
- `match [tolerance]`: Encontrar cartas similares
- `tolerance`: 0-255 (default: 0)

### Pruebas:
- `test`: Prueba rápida con 10 imágenes

---

## ✅ ARCHIVOS ACTIVOS

| Archivo | Propósito |
|---------|-----------|
| `vtes_unificado.py` | TODO en un script |
| `run_simple.sh` | Launcher simplificado |
| `vtes_perceptual_hash.py` | Matching |
| `vtesCreator.py` | Referencia (NO TOCAR) |

---

## ⚠️ NOTAS

### Política CRÍTICA:
- ❌ **NUNCA** borrar ni restaurar sin permiso explícito
- ✅ `vtesCreator.py` NO TOCAR

### Métodos:
- **Hashing**: AVG POOLING + BINARIZACIÓN
- **Bits**: 8 bits por zona × 3 zonas = 24 bits
- **Umbral**: 128 (≥128 → "1", <128 → "0")

### Zonas:
1. **top_superior** (0-15%): Título + Símbolo Edición → Identifica SET
2. **imagen_central** (10-65%, 0-100% ancho): Forma del arte
3. **banda_lateral** (0-25%): Elementos distintivos

---

**🦞 Estado:** ✅ **LISTO**  
**🦞 Siguiente:** Matching masivo

---

*Generado por La Garra Cifrada 🦞*
