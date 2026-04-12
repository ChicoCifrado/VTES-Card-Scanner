# 🦞 VTES-Card-Scanner - Scripts Mantenedos

**Autor:** La Garra Cifrada 🦞  
**Fecha:** 2026-04-12

---

## 📁 Lista de Scripts Mantenedos

### Scripts Esenciales (Generación de Cartas)

| Script | Propósito | Mantener | Estado |
|--------|-----------|----------|--------|
| `vtesCreator.py` | Generación de cartas (referencia) | ✅ SÍ | Referencia |
| `vtes_complete.py` | Dataset con augmentations | ✅ SÍ | En producción |

**Nota:** NO tocar estos scripts a menos que sepas lo que haces.

---

### Scripts de Hashing (Clasificación)

| Script | Propósito | Mantener | Estado |
|--------|-----------|----------|--------|
| `vtes_ph_unificado_actualizado.py` | Hashing multi-zona 3 Áreas | ✅ ACTUALIZAR | **Principal** |
| `vtes_perceptual_hash.py` | Matching simple | ✅ SÍ | Backup |
| `vtes_ph_unificado.py` | Hashing multi-zona (antiguo) | ⚠️ Opcional | Obsoleto |

**Recomendado:** Usar `vtes_ph_unificado_actualizado.py` como script principal.

---

### Scripts de Configuración de Zonas

| Script | Propósito | Mantener | Estado |
|--------|-----------|----------|--------|
| `zonas_3_areas.py` | Definir 3 áreas estratégicas | ✅ SÍ | Principal |
| `zonas_3_areas.json` | Configuración JSON | ✅ SÍ | Referencia |

**Nota:** Estos scripts definen las 3 zonas mínimas para clasificación.

---

### Scripts Eliminados (No Mantener)

| Script | Razón de Eliminación |
|--------|----------------------|
| `vtes_ph_zonas.py` | Consolidado en `vtes_ph_unificado.py` |
| `vtes_zone_explorer.py` | Consolidado en `vtes_ph_unificado.py` |
| `zonas_3_minimas.py` | Reemplazado por `zonas_3_areas.py` |

---

## 🚀 Flujo de Trabajo Recomendado

### 1. Generar Dataset

```bash
python vtes_complete.py --num 100 --with_aug --with_hash --outline --intensity 0.5
```

### 2. Visualizar Cartas con 3 Áreas

```bash
python vtes_ph_unificado_actualizado.py visualize \
    --image carta.jpg \
    --output carta_overlay.jpg
```

### 3. Generar Hashes para Carpeta

```bash
python vtes_ph_unificado_actualizado.py hash \
    --folder cartas_vtes \
    --output hashes.txt
```

### 4. Comparar Cartas

```bash
python vtes_ph_unificado_actualizado.py compare \
    --image1 carta1.jpg \
    --image2 carta2.jpg \
    --output comparacion.txt
```

---

## 📐 Las 3 Áreas Estratégicas

```
┌─────────────────────────────────────────┐
│  1. TOP SUPERIOR (0-15%)                │
│     Título + Símbolo Edición            │
│     → IDENTIFICA EL SET                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  2. IMAGEN CENTRAL (10-65%)             │
│     Arte (forma)                        │
│     → Ovalada = Vampiro                 │
│         Cuadrada = Biblioteca           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  3. BANDA LATERAL (0-25%)               │
│     Clan + Tipo + Coste                 │
│     → Elementos distintivos del SET     │
└─────────────────────────────────────────┘
```

---

## 💡 Ventaja de las 3 Áreas

- ✅ Más rápido (menor procesamiento)
- ✅ Menor ruido visual (mayor precisión)
- ✅ Más robusto a variaciones de iluminación
- ✅ Ideal para matching masivo

---

## 📝 Autor

**La Garra Cifrada** 🦞  
**ChicoCifrado**

---

## ⚠️ Nota Importante

**NO tocar:** `vtesCreator.py` y `vtes_complete.py` a menos que sepas lo que haces.

**Sí actualizar:** `vtes_ph_unificado_actualizado.py` con las 3 áreas.

---

*Este README se generó automáticamente el 2026-04-12*
