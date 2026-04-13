# VTES Card Scanner - README Actualizado

**✅ REPOSITORIO ULTRA LIMPIO**

## 🚀 Ejecutar

```bash
bash run_all.sh
```

Selecciona opción 6 para ejecutar todo automáticamente.

## 📁 Estructura

```
VTES-Card-Scanner/
├── README.md
├── README_ACTUALIZADO.md
├── run_all.sh
├── cartas_vtes/jpg/           ← 4156 imágenes
├── vtes-dataset/              ← Dataset
├── scripts_generacion/        ← 2 scripts
│   ├── vtesCreator.py
│   └── vtes_complete.py
├── scripts_hashing/           ← 2 scripts
│   ├── biblioteca_simple.py
│   └── biblioteca_v2.py
├── scripts_matching/          ← 2 scripts
│   ├── sistema_hibrido.py
│   └── vampiro_simple.py
├── scripts_disciplinas/       ← 1 script
│   └── vtes_discipline_counter_simple.py
└── utilidad/                  ← 2 scripts
    ├── analizar_biblioteca.py
    └── vampiro_muy_simple.py
```

## 🎯 Uso

### Generar dataset
```bash
python3 scripts_generacion/vtes_complete.py generate --input /ruta --output cartas_vtes/jpg
```

### Hashing
```bash
python3 scripts_hashing/biblioteca_simple.py --folder cartas_vtes/jpg
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
| Cartas procesadas | 4156 |
| Hashes únicos | 391 |
| Disciplinas | 0-27 |
| Tasa éxito | 96% |

**✅ 9 scripts esenciales**
