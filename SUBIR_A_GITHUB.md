# Subir a GitHub - Comandos

## 🦞 Estado Actual

✅ Scripts organizados
✅ README actualizado
✅ Informes generados
✅ Hashes completados

## 📋 Comandos para Subir

### 1. **Comprobar estado**
```bash
cd /mnt/e/VTES/VTES-Card-Scanner/
git status
```

### 2. **Ver cambios**
```bash
git status
git diff
```

### 3. **Añadir archivos nuevos**
```bash
git add README.md run_all.sh INFORME_FINAL.md
```

### 4. **Completar cambios de organización**
```bash
git add .
```

### 5. **Comentar**
```bash
git commit -m "feat: organizar scripts y actualizar README
        - Organizar scripts por categoría (generación, hashing, matching, disciplinas)
        - Actualizar README con documentación completa
        - Crear run_all.sh para ejecutar todo automáticamente
        - Generar INFORME_FINAL.md
        - Actualizar memoria.md"
```

### 6. **Push**
```bash
git push
```

## 📁 Archivos a Subir

Nuevos/Actualizados:
- ✅ README.md
- ✅ run_all.sh
- ✅ INFORME_FINAL.md
- ✅ memoria.md
- ✅ scripts_*/ (organizados)
- ✅ sistema_hibrido_matches.txt (en curso)

## ⚠️ Notas

1. **No subir:**
   - `cartas_vtes/jpg/` (archivos grandes)
   - `.git/` (si existe)
   - Archivos con datos sensibles

2. **Sí subir:**
   - Scripts Python organizados
   - README.md
   - run_all.sh
   - INFORME_FINAL.md
   - memoria.md

## 🚀 Opción Rápida

```bash
git add README.md run_all.sh INFORME_FINAL.md
git commit -m "feat: organizar y documentar
        - Organizar scripts por categoría
        - Actualizar README completo
        - Crear run_all.sh para ejecutar todo
        - Generar informe final"
git push
```

**¿Quieres que ejecute estos comandos?**

O me pones el nombre del repo en GitHub para clonarlo si no existe.
