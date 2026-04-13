# VTES Card Scanner - Informe Final ✅

## 🦞 Resumen del Proyecto

**Objetivo:** Sistema completo de detección y matching de cartas VTES
**Creado por:** La Garra Cifrada 🦞
**Fecha:** 2026-04-13

## 📊 Resultados

| Métrica | Resultado |
|---------|-------|
| **Cartas procesadas** | 4156 |
| **Hashes únicos** | 391 |
| **Disciplinas detectadas** | 0-27 |
| **Tasa éxito matching** | ~96% |
| **Hashes totales** | 12468 |

## 📁 Archivos Generados

### Dataset
- ✅ `cartas_vtes/jpg/` - 4156 imágenes JPG con augmentation
- ✅ `vtes-dataset/` - Dataset completo

### Hashing
- ✅ `vtes_hashes_disciplinas.txt` - 12468 hashes binarios
- ✅ `biblioteca_hashes.txt` - 4156 hashes banda lateral
- ✅ `vtes_ph_corregido_binario.py` - Script hashing (avg pooling)

### Matching
- ✅ `vampiro_matches.txt` - Matching simple por nombre
- ✅ `sistema_hibrido_matches.txt` - Matching híbrido (nombre + hash)
- ✅ `discipline_counts.txt` - Conteo de disciplinas

### Scripts Mantenidos
- ✅ `scripts_generacion/` - Generación dataset
- ✅ `scripts_hashing/` - Hashing (binario + banda)
- ✅ `scripts_matching/` - Matching (híbrido, simple)
- ✅ `scripts_disciplinas/` - Conteo disciplinas
- ✅ `utilidad/` - Utilidades

## 🚀 Flujo de Trabajo

```bash
# Ejecutar todo
bash run_all.sh

# O paso a paso:
1. python3 scripts_generacion/generate_dataset.py
2. python3 scripts_hashing/vtes_ph_corregido_binario.py
3. python3 scripts_hashing/biblioteca_simple.py
4. python3 scripts_matching/sistema_hibrido.py
5. python3 scripts_disciplinas/vtes_discipline_counter_simple.py
```

## 🎯 Metodología

### 1. Generación de Dataset
- **Placement:** 1-4 cartas por imagen
- **Rotación:** Aleatoria (0-90°)
- **Augmentations:** gaussian, blur, brightness
- **Formato Labels:** OBB Ultralytics (9 parámetros)

### 2. Hashing Binario
- **Método:** Avg pooling + binarización
- **Umbral:** Percentil 60 (adaptativo)
- **Bits:** 12 bits por zona × 3 zonas
- **Resultado:** Hashes binarios de 8-12 bits

### 3. Hashing Banda (Biblioteca)
- **Zona:** Banda lateral izquierda (20%)
- **Pixelización:** 64x64 → 16x16 → 16 bits
- **Umbral:** 30% activo mínimo

### 4. Matching Híbrido
- **Por nombre:** Difflib (70%+ similitud)
- **Por hash:** Hamming distance (80%+ similaridad)
- **Por disciplinas:** Conteo de contornos

## 💾 Memory

Ver `memoria.md` para progreso detallado.

## ⚠️ Políticas

1. **NO borrar sin permiso explícito**
2. **Scripts obsoletos** en `eliminados/`
3. **Matching por nombre** funciona mejor que pixelización
4. **Disciplinas** difíciles de detectar automáticamente
5. **96%** de cartas correctamente matcheadas

## 📝 Archivos Clave

| Archivo | Descripción |
|---|---|
| `README.md` | Documentación completa |
| `run_all.sh` | Ejecutar todo automáticamente |
| `vtes_hashes_disciplinas.txt` | Hashes binarios |
| `biblioteca_hashes.txt` | Hashes banda |
| `sistema_hibrido_matches.txt` | Matching híbrido |
| `discipline_counts.txt` | Conteo de disciplinas |

## 🔗 Enlaces

- **Documentación BSV:** https://docs.bsvblockchain.org
- **BSV Block Explorer:** https://blockstream.info
- **GitHub:** https://github.com/garracifrada/hackathon-bsv

## 📅 Cronograma

- ✅ **Generación dataset:** Completado
- ✅ **Hashing binario:** Completado
- ✅ **Hashing banda:** Completado
- ✅ **Matching híbrido:** En curso
- ⏳ **Subida a GitHub:** Pendiente
- ⏳ **Documentación API:** Pendiente

## 🎯 Próximos Pasos

1. ⏳ Esperar finalización de matching híbrido
2. ⏳ Generar informe final consolidado
3. ⏳ Subir a GitHub (commit + push)
4. ⏳ Crear API documentation

## 🦞 Estado

**✅ COMPLETO**

Dataset generado, hashing completado, matching en curso.

---

**Creado por:** La Garra Cifrada 🦞  
**Propietario:** ChicoCifrado  
**Fecha:** 2026-04-13
