# 🦞 ANÁLISIS DE CÓDIGO - HASHING VTES - INFORME COMPLETO

## 📋 Resumen Ejecutivo

He analizado exhaustivamente todos los scripts de hashing y augmentations. Aquí están los **fallos críticos** encontrados:

---

## 🐛 FALLOS CRÍTICOS

### 1. ❌ `vtes_ph_unificado_robusto.py` - MÉTODO DCT INCORRECTO

#### Problema Principal:
```python
def extract_zone_hash(self, arr, y_range, x_range):
    dct = np.fft.fft2(arr_float)
    dct_shift = np.fft.ifftshift(np.abs(dct))
    low_freq = dct_shift[h_low:2*h_low, w_low:2*w_low]
    mean_val = np.mean(np.real(low_freq))
    max_abs = np.max(np.abs(low_freq))
    return float(mean_val / max_abs)  # ← DEVUELVE FLOAT, NO HASH BINARIO
```

**Errores:**
- ❌ No es perceptual hashing real (usa DCT/FFT)
- ❌ Devuelve floats (0.0-1.0) en lugar de strings binarios
- ❌ Cálculo `mean_val / max_abs` no es estándar
- ❌ Extrae sub-región irregular del DCT

**Consecuencia:**
- Hashes como `"0.345678"` en lugar de `"10110011"`
- Matching no funciona correctamente
- NO es perceptual hashing válido

**Estado:** ⚠️ **INCORRECTO - NO USAR**

---

### 2. ⚠️ `vtes_ph_corregido_binario.py` - CORREGIDO PERO OPTIMIZABLE

#### ✅ Correcto:
- Avg pooling mediante `resize()` con factor 8
- Binarización con umbral 128
- Salidas binarias de 8 bits

#### ⚠️ Problema de implementación:
```python
def extract_zone_hash(self, image, zone_name):
    # ...
    flat = arr.flatten()
    bits = ''.join(str(bit) for bit in flat[:self.hash_bits])
    return bits
```

**Problema:**
- Extrae los **primeros 8 bits** del array aplanado
- NO distribuye bits uniformemente por la zona
- Pierde información por ser "primero en memoria"

**Mejora sugerida:**
```python
# Mejor enfoque: avg pooling explícito en sub-región
def extract_zone_hash(self, image, zone_name):
    # Crop zona
    zone = img_binary.crop((x_min_px, y_min_px, x_max_px, y_max_px))
    
    # Resize a 8x8 para avg pooling explícito
    zone_small = zone.resize((8, 8), Image.Resampling.BILINEAR)
    
    # Binarizar
    arr = np.array(zone_small)
    binary = (arr >= 128).astype(np.uint8)
    
    # Concatenar bits
    bits = binary.flatten().astype(str)
    return ''.join(bits)
```

**Estado:** ⚠️ **CORRECTO PERO NO ÓPTIMO**

---

### 3. ⚠️ Zonas Mal Configuradas en Ambos Scripts

```python
zones_config = {
    'top_superior': (0, 15, 0, 100),      # ✅ OK
    'imagen_central': (10, 65, 10, 90),   # ❌ x_min=10% incorrecto
    'banda_lateral': (0, 100, 0, 25),     # ✅ OK
}
```

**Problema:**
- `imagen_central: (10, 65, 10, 90)` → ignora 10% del lado izquierdo
- Pierde información importante del arte

**Corrección:**
```python
zones_config = {
    'top_superior': (0, 15, 0, 100),
    'imagen_central': (10, 65, 0, 100),  # ✅ x_min=0%
    'banda_lateral': (0, 25, 0, 100),     # ✅ x_min=0%
}
```

---

### 4. ⚠️ `vtes_perceptual_hash.py` - DCT INCORRECTO (IGUAL QUE #1)

Usa el mismo método DCT que `vtes_ph_unificado_robusto.py`:
- Devuelve floats
- No es perceptual hashing binario
- **Igual de incorrecto** que el script #1

**Estado:** ❌ **INCORRECTO - OBSOLETO**

---

### 5. ⚠️ `vtes_complete.py` - AUGMENTATIONS REDUNDANTES

#### Problema en `apply_all_augmentations_to_image()`:
```python
# Rotar carta para compensar
if abs(angle) > 5.0:
    card = card.rotate(-angle, expand=False, resample=Image.BICUBIC)

# Aplicar augmentations
card_aug = augment_only_card(card, 'all', intensity)

# Rotar de nuevo
if abs(angle) > 5.0:
    card_aug = card_aug.rotate(angle, expand=False, resample=Image.BICUBIC)
```

**Problema:**
- Rotar para compensar y luego rotar de nuevo es **redundante**
- Añade operaciones innecesarias
- Mayor tiempo de procesamiento

**Mejora:**
- Si ya rotamos la carta en `scale_and_place_card()`, no necesitamos rotar de nuevo
- Solo aplicar augmentations sin rotaciones adicionales

---

### 6. ⚠️ `vtes_complete.py` - FUNCIÓN `apply_single_augmentation()` VIEJA

La función `apply_single_augmentation()` se mantiene pero **ya no se usa**:
```python
# Solo llamada en augmentaciones individuales:
aug = apply_single_augmentation(aug, 'gaussian', intensity)
```

**Problema:**
- Código obsoleto en el archivo
- Confusión sobre qué usar
- Debería eliminarse o documentarse como deprecated

**Estado:** ⚠️ **OBSOLETO - DEBERÍA ELIMINARSE**

---

## 📊 COMPARATIVA DE SCRIPTS

| Script | Método | Salidas | Estado | Usar |
|--------|--------|---------|--------|------|
| `vtes_ph_unificado_robusto.py` | DCT/FFT | Floats (0.0-1.0) | ❌ INCORRECTO | NO |
| `vtes_ph_corregido_binario.py` | Avg Pooling + Bin | Strings binarios | ⚠️ OPTIMIZABLE | SÍ |
| `vtes_perceptual_hash.py` | DCT | Floats | ❌ INCORRECTO | NO |

---

## 🎯 RECOMENDACIONES

### Prioridad 1: Usar `vtes_ph_corregido_binario.py` con correcciones
```python
# Crear vtes_ph_optimizado.py combinando:
# - Avg pooling de vtes_ph_corregido_binario.py
# - Zonas corregidas
# - Manejo robusto de errores
```

### Prioridad 2: Corregir zonas de `imagen_central`
Cambiar `(10, 65, 10, 90)` a `(10, 65, 0, 100)`

### Prioridad 3: Eliminar scripts incorrectos
- `vtes_ph_unificado_robusto.py` (DCT incorrecto)
- `vtes_perceptual_hash.py` (DCT incorrecto)

### Prioridad 4: Limpiar `vtes_complete.py`
- Eliminar `apply_single_augmentation()` (obsolleta)
- Simplificar `apply_all_augmentations_to_image()`
- Documentar qué funciones son legacy

---

## 🚀 CÓDIGO ÓPTIMO SUGERIDO

```python
#!/usr/bin/env python3
"""
VTES Perceptual Hash - OPTIMIZADO
Avg pooling explícito + binarización + zonas corregidas
"""

def extract_zone_hash_optimized(image, zone_name, zones_config):
    """
    Extraer hash binario optimizado.
    """
    # Normalizar imagen
    if image.width > 1920:
        image = image.resize((1920, 1920), Image.LANCZOS)
    
    # Convertir a escala de grises
    img_gray = image.convert('L')
    
    # Configurar zona
    x_min_pct, x_max_pct, y_min_pct, y_max_pct = zones_config[zone_name]
    w, h = img_gray.size
    
    # Calcular píxeles
    x_min_px = int(w * x_min_pct / 100)
    x_max_px = int(w * x_max_pct / 100)
    y_min_px = int(h * y_min_pct / 100)
    y_max_px = int(h * y_max_pct / 100)
    
    # Crop zona
    zona = img_gray.crop((x_min_px, y_min_px, x_max_px, y_max_px))
    
    # AVG POOLING explícito a 8x8
    zona_small = zona.resize((8, 8), Image.Resampling.BILINEAR)
    
    # Binarizar
    arr = np.array(zona_small)
    binary = (arr >= 128).astype(np.uint8)
    
    # Extraer 8 bits
    bits = binary.flatten().astype(str)
    return ''.join(bits)
```

---

## 📝 CONCLUSIÓN

### Fallos Principales:
1. ❌ `vtes_ph_unificado_robusto.py` usa DCT incorrecto (floats)
2. ⚠️ `vtes_ph_corregido_binario.py` correcto pero extrae bits de forma subóptima
3. ⚠️ Zonas mal configuradas (pierden información)
4. ⚠️ `vtes_perceptual_hash.py` igual de incorrecto (#1)
5. ⚠️ Funciones obsoletas en `vtes_complete.py`

### Script Correcto:
- ✅ `vtes_ph_corregido_binario.py` es el único que genera hashes binarios correctos
- ⚠️ Necesita corrección en extracción de bits y zonas

### Próximos Pasos:
1. Crear `vtes_ph_optimizado.py` con mejoras
2. Corregir zonas de `imagen_central`
3. Eliminar scripts incorrectos (con permiso)
4. Limpiar funciones obsoletas en `vtes_complete.py`

---

**Fecha:** 2026-04-12 19:54  
**Analizado por:** La Garra Cifrada 🦞
