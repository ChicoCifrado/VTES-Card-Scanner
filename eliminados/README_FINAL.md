# 🦞 VTES CARD SCANNER - Estructura Final Simplificada

## ✅ Scripts Activos (Solo 2)

### **`unificado.py`** - TODO en un script
- Generar dataset
- Perceptual Hashing (3 áreas)
- Visualizar cartas con zonas
- Matching simple
- Configuración de zonas

### **`run_simple.sh`** - Launcher ultra-simple
- Menú interactivo simplificado
- Ejecución directa a `unificado.py`

---

## 📁 Estructura Ultra-Limpia

```
VTES-Card-Scanner/
├── unificado.py                 ← TODO en un script
├── run_simple.sh                ← Launcher simple
├── vtes_perceptual_hash.py     ← Matching (backup)
├── scripts_generacion/
│   └── vtesCreator.py          ← Generación (NO TOCAR)
├── eliminados/                 ← Scripts obsoletos (10 archivos)
│   ├── vtes_generar_hashes.py
│   ├── vtes_generar_hashes_corregido.py
│   ├── vtes_generar_hashes_final.py
│   ├── vtes_generar_hashes_fix.py
│   ├── vtes_hash_all_in_one.py
│   ├── vtes_ph_unificado_actualizado.py
│   ├── vtes_ph_unificado_robusto_correcto.py
│   ├── zona_explora.py
│   ├── vtes_hashes_corregidos.txt
│   ├── vtes_hashes_exitosos.txt
│   ├── vtes_hashes_completos.txt
│   └── run.sh (launcher antiguo)
└── memory/                     ← Logs y checkpoints

```

---

## 🚀 Uso Simplificado

### Generar dataset:
```bash
python unificado.py generate \
  --folder ./cartas \
  --output ./dataset \
  --augmentations all \
  --intensity 0.5
```

### Hashing:
```bash
python unificado.py hash \
  --folder cartas_vtes/jpg \
  --output hashes.txt \
  --config 3_areas
```

### Visualizar:
```bash
python unificado.py visualize \
  --image carta.jpg \
  --output carta_zones.jpg
```

### Matching:
```bash
python unificado.py match \
  --hashes hashes.txt \
  --image carta.jpg
```

---

## 📊 Estado

✅ **Simplificado**: De ~20 scripts a solo 2 activos  
✅ **Organizado**: Scripts obsoletos en `eliminados/`  
✅ **Documentado**: Esta README actualizada  
✅ **Limpio**: Sin archivos redundantes  

---

*Estructura final por La Garra Cifrada 🦞*
