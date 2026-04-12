# 🗂️ Estructura de Carpetas Organizada

## ✅ Scripts ACTIVOS (en root)

- **`vtesComplete.py`** - Generación de dataset con augmentations
- **`vtes_perceptual_hash.py`** - Matching simple de hashes
- **`vtes_ph_unificado_robusto.py`** - Hashing con 3 áreas estratégicas
- **`zonas_3_areas.json`** - Configuración JSON de zonas
- **`zonas_3_areas.py`** - Configuración Python de zonas
- **`zonas_minimas.py`** - Zonas mínimas
- **`vtes.json`** - Metadatos del dataset

## 📦 Outputs (en root o subcarpetas)

- **`cartas_vtes/`** - Cartas originales (webp)
- **`fondos_vtes/`** - Fondos originales
- **`jpg/`** - Cartas JPG procesadas
- **`vtes-dataset/`** - Dataset final generado
- **`memory/`** - Log de progreso

## 📁 Directories de Organización

### **`scripts_generacion/`**
Scripts para generar dataset:
- **`vtesCreator.py`** - ✅ **NO TOCAR** (referencia original)

### **`scripts_hashing/`**  
Scripts para hashing:
- Actualmente vacío (el script está en root)

### **`eliminados/`**
Scripts obsoletos y versiones anteriores:
- `vtes_generar_hashes.py`
- `vtes_generar_hashes_corregido.py`
- `vtes_generar_hashes_final.py`
- `vtes_generar_hashes_fix.py`
- `vtes_hash_all_in_one.py`
- `vtes_ph_unificado_actualizado.py`
- `vtes_ph_unificado_robusto_correcto.py`
- `zona_explora.py`
- Hashes obsoletos:
  - `vtes_hashes_corregidos.txt`
  - `vtes_hashes_exitosos.txt`
  - `vtes_hashes_completos.txt`
  - `vtes_hashes_binarios_corregidos.txt`

### **`__pycache__`**
Archivos compilados Python - ⚠️ Puede limpiar si ocupa espacio

## 📝 Documentación

- **`SCRIPTS_MANTENIDOS.md`** - Lista de scripts activos
- **`SCRIPTS_README.md`** - Documentación del proyecto

---

## 🎯 Estructura Final

```
VTES-Card-Scanner/
├── scripts_generacion/       # Scripts de generación
│   └── vtesCreator.py        # ✅ NO TOCAR (referencia)
├── scripts_hashing/          # Scripts de hashing
├── eliminados/               # Scripts obsoletos
│   ├── *.py                  # Scripts antiguos
│   └── vtes_hashes_*.txt     # Hashes obsoletos
├── vtes-ph-corregido-binario.py  # ✅ Script de hashing ACTIVO
├── zonas_3_areas.json        # ✅ Configuración de zonas
├── zonas_3_areas.py          # ✅ Configuración Python
├── zonas_minimas.py          # ✅ Zonas mínimas
├── vtes_perceptual_hash.py   # ✅ Matching
└── {cartas_vtes,fondos_vtes,jpg,vtes-dataset,}memory/
```

---

*Organizado por La Garra Cifrada 🦞*
