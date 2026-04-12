# 🗂️ Estructura de Scripts - Scripts Mantenidos

## ✅ Scripts ACTIVOS (mantener)

### Generación de Dataset
- **`vtesCreator.py`** - ✅ **NO TOCAR** (referencia original)
- **`vtes_complete.py`** - ✅ Unificado con augmentations y labels OBB

### Perceptual Hashing
- **`vtes_ph_corregido_binario.py`** - ✅ Script de hashing CORREGIDO (última versión)
- **`vtes_ph_unificado_robusto.py`** - ✅ Hashing robusto con manejo de errores
- **`vtes_perceptual_hash.py`** - ✅ Matching simple de hashes

### Configuración de Zonas
- **`zonas_3_areas.json`** - ✅ Configuración JSON de 3 áreas
- **`zonas_3_areas.py`** - ✅ Configuración Python de zonas
- **`zonas_minimas.json`** - ✅ Zonas mínimas

## 📦 Outputs Generados
- **`vtes_hashes_binarios_corregidos.txt`** - ✅ Hashes CORREGIDOS (últimos)
- **`vtes_hashes_corregidos.txt`** - ⚠️ Obsoleto (puede borrar)
- **`corrupted_images.txt`** - ✅ Lista de imágenes corruptas

## 🗑️ Scripts a Eliminar (mover a eliminados/)
- `vtes_generar_hashes.py`
- `vtes_generar_hashes_corregido.py`
- `vtes_generar_hashes_final.py`
- `vtes_generar_hashes_fix.py`
- `vtes_hash_all_in_one.py`
- `vtes_ph_unificado_robusto_correcto.py`
- `vtes_ph_unificado_actualizado.py` (redundante)
- `zona_explora.py`
- `vtes_convert_webp_to_jpg.py` (si está obsoleto)

## 📂 Zonas de Trabajo
- **`cartas_vtes/`** - Cartas originales
- **`fondos_vtes/`** - Fondos originales  
- **`jpg/`** - Cartas JPG procesadas
- **`vtes-dataset/`** - Dataset final generado
- **`memory/`** - Log de progreso

---

*Estructura organizada por La Garra Cifrada 🦞*
