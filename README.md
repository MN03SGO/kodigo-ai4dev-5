# kodigo-ai4dev-5

## Prompts iniciales

1. `#Eres un experto programador en python`

2. `#Haremos un script que lea las extensiones de los archivos en una carpeta (como .pdf, .mp3, .jpg) y los mueva automaticamente a subcarpetas ordenadas. Consideraciones: Os debian 13. Directorio: /home/sigaran/Descargas. Archivos diferentes no tomar en cuenta.`

3. `#Me parece, pero creo que con esto puede mejorar. Haremos lo siguiente: Automatizaremos el proceso con un servicio de systemd, con un temporizador para una ejecucion periodica manual. Ademas, los archivos temporales (part, .crdownload, .tmp) se moveran a papeleria (utilizar gio subprocess.run).`

---

### b. Breve explicación
i. **Qué se pidió a la IA**: Se solicitó un script para organizar archivos en `~/Descargas` por extensión, y posteriormente, automatizar dicha tarea mediante un servicio y temporizador de `systemd`, integrando la gestión de archivos temporales mediante `gio trash`.

ii. **Por qué se ajustó o refinó el prompt**: Se refinó para incluir requerimientos de automatización a nivel de sistema operativo (`systemd`) y mejores prácticas de gestión de residuos (`gio trash`) en lugar de simplemente eliminar archivos, mejorando la robustez y utilidad del script original.

---

### a. Evidencia de mejora o modificación
Se modificó la lógica inicial (que solo movía archivos) para incorporar la gestión de archivos temporales mediante `subprocess.run(['gio', 'trash', ...])`, aumentando la seguridad y control sobre archivos parcialmente descargados.

---

### 5.
a. **Pruebas del código**: Se verificó la lógica mediante revisión estática del código y simulación de la estructura de directorios, validando el uso de `pathlib` y la sintaxis de `gio`.

b. **Identificación de error/ajuste**: Se identificó que mover archivos a una carpeta llamada "Papelera" manualmente es menos robusto que usar la papelera del sistema (`gio trash`), por lo que se realizó el ajuste para integrar la herramienta nativa de Debian 13.

---

### 6. Reflexión final
a. **Aprendizaje**: El uso de IA permite iterar rápidamente desde un script simple hacia un sistema automatizado completo mediante la integración de herramientas de SO (`systemd`, `gio`).

b. **Vibecoding**:
- **Ventajas**: Alta velocidad de implementación y estructuración lógica compleja de forma conversacional.
- **Límites**: La necesidad de supervisión experta para asegurar que las llamadas al sistema (`systemd`) sean seguras y sigan las mejores prácticas.

c. **Comprensión**: Comprendo plenamente la lógica de `pathlib` y la gestión de procesos (`subprocess`). Necesito reforzar la configuración avanzada de unidades de `systemd` y sus permisos asociados.
