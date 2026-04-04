# 🦇 Plan VTES-Card-Scanner - Estado Actual

---

## 📋 Estado (2026-04-04 19:08)

### ✅ Completado

1. **Dataset VTES generado**
   - vtesCreator.py con multiprocessing
   - 1000 imágenes (en proceso: lucky-lobster)
   - Distribución automática: 80/10/10

2. **Cartas con ratio de aspecto**
   - Cartas mantienen su ratio original
   - No forzando cuadrado

3. **Detection de attached**
   - check_collisions() implementado
   - >=10% overlap detectado
   - Attached property añadido a bounds
   - Comentario: "Aquí va la toda lógica de equipos, retainers, cartas especiales, etc."

4. **create_labels.py**
   - Convierte bounds.json a YOLO
   - Genera .txt (labels) + .json (attached)
   - 800 train, 100 val, 100 test

5. **vtes-dataset.yaml**
   - Configuración para YOLOv11
   - Hyperparameters completos

---

## 🚧 En Proceso

### lucky-lobster
- Generando 1000 imágenes con attached
- Multiprocessing: ~40s restantes

### mellow-reef
- Generando 1000 imágenes sin attached
- Multiprocessing: ~1min restante

---

## 🎯 Próximos Pasos

### Prioridad Alta
1. **Esperar lucky-lobster** termine con 1000 imágenes + attached
2. **Crear labels YOLO** con attached
3. **Evaluar attached pairs** encontrados
4. **Crear dataset.yaml final**

### Medio Plazo
1. **Entrenar YOLOv11** con dataset
2. **Crear plugin OBS** (C++)
3. **Configurar API** para emparejamiento
4. **Integración BSV** (futuro)

### Largo Plazo
1. **Emparejamiento BSV** con sets
2. **Token VTES** en blockchain
3. **Certificación VTES**

---

## 📊 Métricas

- **Imágenes:** 1000
- **Cartas total:** ~50,000
- **Attached pairs:** Esperando resultados
- **Distribución:** 80/10/10
- **Ratio de aspecto:** Conservado

---

## 🔗 Enlaces

- GitHub: https://github.com/ChicoCifrado/VTES-Card-Scanner
- BSV Docs: https://docs.bsvblockchain.org
- BRC Patterns: https://bsv.brc.dev/
