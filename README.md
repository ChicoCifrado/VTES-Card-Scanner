# VTES Card Scanner - Sistema Híbrido 🦞

**Proyecto completo de detección de cartas VTES:**
- Dataset generado (4156 cartas)
- Hashing binario con disciplines
- Matching híbrido (nombre + hash)
- Conteo de disciplinas

## 🦞 Estado

| Componente | Resultado |
|---|---|
| Dataset generado | ✅ 4156 cartas |
| Hashing binario | ✅ 12468 hashes |
| Hashing banda | ✅ 4156 hashes |
| Disciplinas detectadas | ✅ 0-27 |
| Tasa éxito matching | ✅ ~96% |

## 📁 Estructura

```
VTES-Card-Scanner/
├── README.md                    ← Este archivo
├── run_all.sh                   ← Ejecutar todo
├── organizar.sh                 ← Organizar scripts
├── memoria.md                   ← Progreso diario
├── cartas_vtes/
│   └── jpg/                     ← Imágenes (4156)
├── vtes-dataset/                ← Dataset completo
├── scripts_generacion/          ← Generación dataset
│   ├── generate_dataset.py
│   └── vtes_complete.py
├── scripts_hashing/             ← Hashing
│   ├── vtes_ph_corregido_binario.py
│   ├── biblioteca_simple.py
│   ├── biblioteca_v2.py
│   └── biblioteca_process.py
├── scripts_matching/            ← Matching
│   ├── sistema_hibrido.py
│   ├── vampiro_simple.py
│   ├── vampiro_matches_v2.py
│   └── vampiro_final.py
├── scripts_disciplinas/         ← Disciplinas
│   ├── vtes_discipline_counter_simple.py
│   └── vtes_discipline_counter.py
└── utilidad/                    ← Utilidades
    ├── vampiro_muy_simple.py
    └── analizar_biblioteca.py
```

## 🚀 Uso

### **1. Ejecutar todo (recomendado)**
```bash
bash run_all.sh
```
Selecciona opción 6 para ejecutar todo automáticamente.

### **2. Ejecutar paso a paso**

#### Generar dataset
```bash
python3 scripts_generacion/generate_dataset.py \
    --input /ruta/originales \
    --output cartas_vtes/jpg
```

#### Hashing binario
```bash
python3 scripts_hashing/vtes_ph_corregido_binario.py \
    --folder cartas_vtes/jpg \
    --output vtes_hashes_disciplinas.txt
```

#### Hashing banda (biblioteca)
```bash
python3 scripts_hashing/biblioteca_simple.py \
    --folder cartas_vtes/jpg \
    --output biblioteca_hashes.txt
```

#### Matching híbrido
```bash
python3 scripts_matching/sistema_hibrido.py \
    --folder cartas_vtes/jpg \
    --output sistema_hibrido_matches.txt
```

#### Contar disciplinas
```bash
python3 scripts_disciplinas/vtes_discipline_counter_simple.py \
    --folder cartas_vtes/jpg \
    --output discipline_counts.txt
```

### **3. Matching rápido**

Solo por nombre (más rápido):
```bash
python3 scripts_matching/vampiro_simple.py \
    --folder cartas_vtes/jpg
```

## 🎯 Metodología

### **Detección de Tipo**
- **Biblioteca:** Texto inferior grande (>40%)
- **Vampiro:** Texto pequeño + disciplina visible

### **Hashing**
- **Banda lateral:** Hash principal (64x64 → 16x16 → 16 bits)
- **Caja central:** Hash secundario (forma del arte)

### **Matching**
- **Por nombre:** Difflib (70%+ similitud)
- **Por hash:** Hamming distance (80%+ similaridad)
- **Por disciplinas:** Conteo de contornos

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Cartas procesadas | 4156 |
| Hashes únicos | 391 |
| Disciplinas por carta | 0-27 |
| Tasa éxito | 96% |
| Hashes totales | 12468 |

## 📝 Memory

Ver `memoria.md` para progreso detallado.

## ⚠️ Notas

1. **NO borrar sin permiso** (política activa)
2. **Scripts obsoletos** en `eliminados/`
3. **Matching híbrido** combina nombre + hash + disciplinas
4. **Banda lateral** es hash principal para biblioteca

## 🔗 Enlaces

- **Documentación BSV:** https://docs.bsvblockchain.org
- **BSV Block Explorer:** https://blockstream.info
- **GitHub:** https://github.com/garracifrada/hackathon-bsv

## 📅 Última actualización

2026-04-13 - Estado COMPLETO
