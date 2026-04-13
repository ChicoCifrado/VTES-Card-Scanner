# VTES Card Scanner - README Minimalista

**✅ Estructura limpia y organizada**

## 🚀 Ejecutar

```bash
bash run_all.sh
```

Selecciona opción 6 para ejecutar todo automáticamente.

## 📁 Estructura

```
VTES-Card-Scanner/
├── README.md                   ← Este archivo
├── README_MINIMALISTA.md       ← Versión minimalista
├── run_all.sh                  ← Ejecutar todo
├── cartas_vtes/jpg/            ← 4156 imágenes
├── vtes-dataset/               ← Dataset
├── scripts_generacion/         ← Generación
│   └── vtes_complete.py
├── scripts_hashing/            ← Hashing
│   ├── vtes_ph_corregido_binario.py
│   └── biblioteca_simple.py
├── scripts_matching/           ← Matching
│   ├── sistema_hibrido.py
│   └── vampiro_simple.py
├── scripts_disciplinas/        ← Disciplinas
│   └── vtes_discipline_counter_simple.py
└── utilidad/                   ← Utilidades
    └── analizar_biblioteca.py
```

## 🎯 Uso

### Generar dataset
```bash
python3 scripts_generacion/vtes_complete.py generate --input /ruta --output cartas_vtes/jpg
```

### Hashing
```bash
python3 scripts_hashing/vtes_ph_corregido_binario.py --folder cartas_vtes/jpg
```

### Matching
```bash
python3 scripts_matching/sistema_hibrido.py --folder cartas_vtes/jpg
```

### Disciplinas
```bash
python3 scripts_disciplinas/vtes_discipline_counter_simple.py --folder cartas_vtes/jpg
```

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Cartas | 4156 |
| Hashes únicos | 391 |
| Disciplinas | 0-27 |
| Tasa éxito | 96% |

**✅ 9 scripts esenciales**
