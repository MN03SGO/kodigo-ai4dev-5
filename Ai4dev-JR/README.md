# Sistema de Normalización de Transacciones

## Descripción

Desarrollé un programa que lee transacciones en distintos formatos JSON, las convierte a una estructura común, valida sus datos y permite consultarlas desde una interfaz de línea de comandos.

## Estructura de archivos

- `main.py`: carga los archivos, coordina la normalización y validación, y muestra el menú de opciones.
- `normalizer.py`: detecta el formato de origen y convierte cada registro en una transacción normalizada.
- `validator.py`: valida las transacciones y calcula métricas.
- `config.json`: contiene los mapeos de estados, los formatos de fecha y las monedas admitidas.
- `data.json`: contiene los registros de entrada.

## Cómo ejecutarlo

El proyecto requiere Python 3 y no utiliza librerías externas. Desde la carpeta del proyecto, ejecuto:

```bash
python3 main.py
```

## Decisiones de diseño y uso de IA

Usé Claude como apoyo para escribir el código base, pero definí las reglas de negocio y ajusté el comportamiento durante las pruebas. En particular:

- Asigné la moneda `EUR` a los registros que incluyen el símbolo `€` y no tienen un campo de moneda explícito.
- Los estados que no aparecen en el mapeo se guardan en mayúsculas, por ejemplo, `PENDING`.
- Agregué una opción para mostrar los motivos exactos por los que se rechaza cada transacción.
- Decidí que una fecha que no se puede interpretar hace que la transacción sea inválida.
- El conteo por estado y las sumas por moneda se calculan solo con transacciones válidas, para que los montos inválidos no alteren los totales.
- Los filtros de estado y moneda muestran únicamente transacciones válidas.
- Conservé el JSON original junto al objeto normalizado para mostrarlo al consultar los registros inválidos.
